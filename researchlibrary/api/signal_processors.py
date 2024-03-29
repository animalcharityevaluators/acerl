import logging
from itertools import chain

from django.db.models import signals
from haystack.signals import BaseSignalProcessor

from .models import Category, Person, Resource

logger = logging.getLogger(__name__)


class SignalProcessor(BaseSignalProcessor):
    def setup(self):
        for model in (Resource, Person):  # All models with indices
            signals.post_save.connect(self.handle_save, sender=model)
            signals.post_delete.connect(self.handle_delete, sender=model)
        for model in (Resource, Category, Person):  # All models
            signals.post_save.connect(self.handle_related, sender=model)
            signals.post_delete.connect(self.handle_related, sender=model)
        signals.m2m_changed.connect(self.handle_m2m)

    def teardown(self):
        for model in (Resource, Person):
            signals.post_save.disconnect(self.handle_save, sender=model)
            signals.post_delete.disconnect(self.handle_delete, sender=model)
        for model in (Resource, Category, Person):
            signals.post_save.disconnect(self.handle_related, sender=model)
            signals.post_delete.disconnect(self.handle_related, sender=model)
        signals.m2m_changed.disconnect(self.handle_m2m)

    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.
        """
        logger.debug("Handle save sent by %r for %s – %s", sender, instance, kwargs)
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            index = self.connections[using].get_unified_index().get_index(sender)
            index.update_object(instance, using=using)

    def handle_delete(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        delete should be sent to & delete the object on those backends.
        """
        logger.debug("Handle delete sent by %r for %s – %s", sender, instance, kwargs)
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            index = self.connections[using].get_unified_index().get_index(sender)
            index.remove_object(instance, using=using)

    def handle_related(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        logger.debug("Handle related sent by %r for %s – %s", sender, instance, kwargs)
        for using in using_backends:
            unified_index = self.connections[using].get_unified_index()
            if sender == Resource:
                # TODO: Complex case using several indices. Omitted for now.
                pass
            elif sender == Person:
                index = unified_index.get_index(Resource)
                objects = chain(instance.resources_authored.all(), instance.resources_edited.all())
                for obj in objects:
                    index.update_object(obj, using=using)
            else:
                index = unified_index.get_index(Resource)
                objects = instance.resources.all()
                if len(objects) < 10:
                    # We have timeout problems when too many resources need to be updated
                    for obj in objects:
                        index.update_object(obj, using=using)

    def handle_m2m(self, sender, instance, action, reverse, model, pk_set, **kwargs):
        logger.debug(
            "Handle m2m sent by %r for %s with %s on %s (%s) updating %s – %s",
            sender,
            instance,
            action,
            model,
            reverse,
            pk_set,
            kwargs,
        )
        if action.startswith("post_") and Resource in (instance._meta.model, model):
            if instance._meta.model == Resource:
                self.handle_save(instance._meta.model, instance)
            elif model == Resource:
                self.handle_related(instance._meta.model, instance)
