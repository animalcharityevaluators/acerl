import datetime
import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from ..models import Category, Person, Resource

settings.HAYSTACK_CONNECTIONS["default"]["PATH"] = os.path.join(
    settings.BASE_DIR, "..", "test_whoosh_index"
)


class SearchTests(TestCase):
    """
    Basic tests for the search endpoint.

    # TODO: Extend according to https://trello.com/c/fAUsohvO/2-interface-prototype
    """

    endpoint_url = "/api/v1/search/"
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        author = Person.objects.create(name="Mock Author")
        category = Category.objects.create(name="Mock Category")
        Resource.objects.create(
            title="Mock Turtle",
            abstract="A little summary of the mock content.",
            published=datetime.date.today(),
        )
        Resource.objects.create(
            title="Mock Chicken",
            abstract="A little summary of the mock content.",
            published=datetime.date.today(),
        )
        Resource.objects.create(
            title="Mock Cow",
            abstract="A little summary of the mock content.",
            published=datetime.date.today(),
        )
        Resource.objects.create(
            title="Mock Pig",
            abstract="A little summary of the mock content.",
            published=datetime.date.today(),
        )
        Resource.objects.create(
            title="Mock Piglet",
            abstract="A little summary of the mock content.",
            published=datetime.date.today(),
        )
        Resource.objects.create(
            title="Mock Turkey",
            abstract="A little summary of the mock content.",
            published=datetime.date(1994, 10, 19),
        )
        resources = list(Resource.objects.all())
        author.resources_authored.add(*resources)
        category.resources.add(*resources[:5])
        resources[5].categories.add(category)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        call_command("clear_index", interactive=False)

    def test_content_type(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertEqual(response["content-type"], "application/json")

    def test_status(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertEqual(response.status_code, 200)

    def test_mock_count(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertIsInstance(response.json()["count"], int)
        self.assertEqual(response.json()["count"], 6)

    def test_pig_count(self):
        response = self.client.get(self.endpoint_url + "?q=pig")
        self.assertIsInstance(response.json()["count"], int)
        self.assertEqual(response.json()["count"], 1)

    def test_results(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertIsInstance(response.json()["results"], list)

    def test_published(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertTrue(response.json()["results"][0]["published"])

    def test_mindate_filter(self):
        response = self.client.get(self.endpoint_url + "?q=mock&minyear=2010")
        self.assertEqual(response.json()["count"], 5)

    def test_maxdate_filter(self):
        response = self.client.get(self.endpoint_url + "?q=mock&maxyear=2000")
        self.assertEqual(response.json()["count"], 1)

    def test_empty_query(self):
        response = self.client.get(self.endpoint_url)
        self.assertEqual(response.json()["count"], 6)

    def test_sortby_date(self):
        response = self.client.get(self.endpoint_url + "?q=mock&sort=published")
        self.assertEqual(response.json()["results"][0]["published"], "1994-10-19")

    def test_text(self):
        response = self.client.get(self.endpoint_url + "?q=mock")
        self.assertIsInstance(response.json()["results"][0]["abstract"], str)

    def test_category_filter(self):
        response = self.client.get(self.endpoint_url + "?category=Mock%20Category")
        self.assertEqual(response.json()["count"], 6)
