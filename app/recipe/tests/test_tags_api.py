
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
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

