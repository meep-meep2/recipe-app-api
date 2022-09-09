from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    #Create and return a recipe detail URL
    return reverse('recipe:recipe-detail', args=recipe_id)

#helps set up a recipe with defaults, but lets us change the ones needed to test
def create_recipe(user, **params):
    #Create and return a sample recipe
    defaults = {
            'title' : 'Sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('5.50'), #shouldn't use decimal or float fields, should use integer for money
            'description' : 'Sample recipe description',
            'link' : 'http://example.com/recipe.pdf'
    }

    defaults.update(params) #change these default values based on info received

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeAPITests(TestCase):
    #Unauthenticated tests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        #Test that auth is required to call api

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@example.com', 'testpass')
        self.client.force_authenticate(user=self.user) #All users using this client will be authenticated


    def test_retrieve_recipes(self):
        #Test retrieving list of recipes

        create_recipe(user = self.user)
        create_recipe(user = self.user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        #Test list of recipes is limited to authenticated user
        other_user = get_user_model().objects.create_user('other@example.com', 'testpass')
        create_recipe(user = self.user)
        create_recipe(user = other_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user = self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        payload = {
            'title' : 'Sample recipe name',
            'time_minutes' : 5,
            'price' : Decimal('5.50'), #shouldn't use decimal or float fields, should use integer for money
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

