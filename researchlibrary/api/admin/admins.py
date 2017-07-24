import requests
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.conf.urls import url
from django.db.models.query import QuerySet
from ..models import Person, Category, NewCategory, Keyword, Resource
from .utils import Gist
from mptt.admin import DraggableMPTTAdmin
from django.forms import ModelForm

class UsageCountListFilter(admin.SimpleListFilter):
    title = 'Usage count'
    parameter_name = 'usage_count'
    count_field = 'resources__id'

    def lookups(self, request, model_admin):
        return (
            ('0', 'Unused'),
            ('1', 'Used once'),
            ('2', 'Used twice'),
            ('3', 'Used thrice'),
            ('4', 'Used often'),
        )

    def queryset(self, request, queryset):
        value = int(self.value()) if self.value() else None
        if value is not None and value < 4:
            return queryset.annotate(resource_count=Count(self.count_field)) \
                .filter(resource_count=value)
        elif value is not None:
            return queryset.annotate(resource_count=Count(self.count_field)) \
                .filter(resource_count__gte=4)
        else:
            return queryset


class AuthorUsageCountListFilter(UsageCountListFilter):
    title = 'Usage count as author'
    parameter_name = 'usage_count_as_author'
    count_field = 'resources_authored__id'


class EditorUsageCountListFilter(UsageCountListFilter):
    title = 'Usage count as editor'
    parameter_name = 'usage_count_as_editor'
    count_field = 'resources_edited__id'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count']
    list_filter = [UsageCountListFilter]
    search_fields = ['name']

    def get_queryset(self, request):
        return Category.objects.annotate(cat_count=Count('resources'))

    def usage_count(self, obj):
        return obj.resources.count()
    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'cat_count'

@admin.register(NewCategory)
class NewCategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'usage_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
            return NewCategory.objects.annotate(cat_count=Count('resources'))

    def usage_count(self, obj):
        return obj.resources.count() if obj.is_leaf_node() else None

    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'cat_count'


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count']
    list_filter = [UsageCountListFilter]
    search_fields = ['name']

    def get_queryset(self, request):
        return Keyword.objects.annotate(kw_count=Count('resources'))

    def usage_count(self, obj):
        return obj.kw_count
    usage_count.short_description = 'Usage Count'
    usage_count.admin_order_field = 'kw_count'


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'usage_count_as_author', 'usage_count_as_editor']
    list_filter = [AuthorUsageCountListFilter, EditorUsageCountListFilter]
    search_fields = ['name']

    def usage_count_as_author(self, obj):
        return obj.auth_count

    def usage_count_as_editor(self, obj):
        return obj.edi_count

    def get_queryset(self, request):
        return Person.objects.annotate(auth_count=Count('resources_authored')) \
            .annotate(edi_count=Count('resources_edited'))

    def usage_count(self, obj):
        return obj.ct_count
    usage_count_as_author.short_description = 'Usage Count as author'
    usage_count_as_author.admin_order_field = 'auth_count'
    usage_count_as_editor.short_description = 'Usage Count as editor'
    usage_count_as_editor.admin_order_field = 'edi_count'


class ResourceForm(ModelForm):
    class Meta:
        model = Resource
        fields = ['newcategories']

    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        if NewCategory.objects.all():
            all_categories = NewCategory.objects.all()
            leaf_ids = [c.id for c in all_categories if c.is_leaf_node()]
            leaf_qs = all_categories.filter(id__in=leaf_ids)
            self.fields['newcategories'].queryset = leaf_qs


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    form = ResourceForm
    change_list_template = 'api/change_list.html'
    change_form_template = 'api/change_form.html'
    list_display = ['augmented_title', 'concatenated_authors', 'published', 'resource_type']
    search_fields = ['title', 'authors__name', 'editors__name', 'url', 'publisher', 'subtitle',
                     'journal', 'series', 'edition', 'sourcetype']
    list_filter = ['resource_type', 'categories', 'newcategories', 'sourcetype', 'keywords']
    date_hierarchy = 'published'
    filter_horizontal = ['authors', 'editors', 'keywords', 'categories', 'newcategories']
    fieldsets = (
        ('Main Fields', {
            'fields': ('title', 'subtitle', 'authors', 'editors', 'published', 'accessed', 'url',
                       'fulltext_url', 'resource_type', 'categories', 'newcategories')
        }),
        ('Auxilliary Fields', {
            'classes': ('collapse',),
            'fields': ('keywords', 'abstract', 'review'),
        }),
        ('Optional Fields', {
            'classes': ('collapse',),
            'fields': ('publisher', 'journal', 'volume', 'number', 'startpage',
                       'endpage', 'series', 'edition', 'sourcetype', 'fulltext'),
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fulltext = None
        self.title = None

    def augmented_title(self, obj):
        return format_html(
            '<a href="{external_url}" target=_blank title="View resource (external)">[↗]</a>'
            '&nbsp;&nbsp;<a href="{edit_url}">{title}</a>',
            edit_url=reverse('admin:api_resource_change', args=[obj.id]),
            external_url=obj.url,
            title=obj.title)
    augmented_title.short_description = 'Title'
    augmented_title.admin_order_field = 'title'

    def concatenated_authors(self, obj):
        return ', '.join([author.name for author in obj.authors.all()])
    concatenated_authors.short_description = 'Authors'

    def get_urls(self):
        urls = super(ResourceAdmin, self).get_urls()
        new_urls = [
            url(r'^add_url/$', self.add_url, name='api_resource_add_url'),
        ]
        return new_urls + urls

    def get_changeform_initial_data(self, request):
        initial = super(ResourceAdmin, self).get_changeform_initial_data(request)
        initial['fulltext'] = getattr(request, 'fulltext', None)
        initial['title'] = getattr(request, 'title', None)
        return initial

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        extra_context = extra_context or {}
        if obj.fulltext:
            extra_context['keywords'] = Gist.find_keywords(obj.fulltext)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if hasattr(request, 'fulltext'):
            extra_context['keywords'] = Gist.find_keywords(request.fulltext)
        return super().add_view(request, form_url, extra_context=extra_context)

    def add_url(self, request, form_url='', extra_context=None):
        if request.method == 'POST' and not (self.fulltext or self.title):
            extra_context = extra_context or {}
            url_ = request.POST['url']
            response = requests.get(url_, timeout=10)
            gist = Gist(html=response.text)
            request.title = gist.title
            request.fulltext = gist.text
            extra_context['keywords'] = gist.keywords
            # Manipulating the request
            request.method = 'GET'
            request.GET = request.POST
            return self.add_view(
                request, reverse('admin:api_resource_add'), extra_context=extra_context)
        return URLResourceAdmin(model=self.model, admin_site=self.admin_site) \
            .add_view(request, form_url, extra_context=extra_context)

    def has_add_permission(self, request):
        """Make the plus button show up. Why is this necessary?"""
        return True


class URLResourceAdmin(admin.ModelAdmin):
    add_form_template = 'api/add_form.html'
    fieldsets = [(None, {'fields': ['url']})]
