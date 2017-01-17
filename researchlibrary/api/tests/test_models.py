from django.test import TestCase
from ..models import Person, Resource, Keyword, Category


class ModelTests(TestCase):
    """
    Tests for the models.
    """
    endpoint_url = '/admin/'

    def test_save_person(self):
        person = Person.objects.create(name='Sara Nowak')
        self.assertTrue(person.pk, person)
        person.delete()

    def test_save_resource(self):
        resource = Resource.objects.create(
            title='The Book of the New Sun', published='1980-05-23')
        self.assertTrue(resource.pk, resource)
        resource.delete()

    def test_save_keyword(self):
        keyword = Keyword.objects.create(name='fluffy')
        self.assertTrue(keyword.pk, keyword)
        keyword.delete()

    def test_save_category(self):
        category = Category.objects.create(name='Hairdryers')
        self.assertTrue(category.pk, category)
        category.delete()
