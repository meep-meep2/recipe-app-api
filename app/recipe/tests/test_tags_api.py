from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

#Tests views? Serializer is just the model.

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    #create and return a tag detail url
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email = 'user@example.com', password='pass123'):
    return get_user_model().objects.create_user(email, password)

class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        #Test that auth is required to call api

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@example.com', 'testpass')
        self.client.force_authenticate(self.user) #All users using this client will be authenticated


    def test_retrieve_tags(self):
        #Test retrieving list of recipes

        Tag.objects.create(user = self.user, name='Vegan' )
        Tag.objects.create(user = self.user, name='Vegetarian' )

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_list_limited_to_user(self):
        #Test list of recipes is limited to authenticated user
        other_user = get_user_model().objects.create_user('other@example.com', 'testpass')
        Tag.objects.create(user = other_user, name='Vegan' )
        tag = Tag.objects.create(user = self.user, name='Vegetarian' )

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):

        tag = Tag.objects.create(user=self.user, name='Dessert')
        payload = {'name' : 'Dessert'}

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_recipe(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipes(self):
        tag1 = Tag.objects.create(user=self.user, name='noodles')
        tag2 = Tag.objects.create(user=self.user, name='sauce')

        recipe = Recipe.objects.create(
            title='Spaghetti',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        tag = Tag.objects.create(user=self.user, name='Eggs')
        Tag.objects.create(user=self.user, name='Lentils')
        r1 = Recipe.objects.create(
            title='Spaghetti',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        r2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        r1.tags.add(tag)
        r2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only' : 1})
        self.assertEqual(len(res.data), 1)