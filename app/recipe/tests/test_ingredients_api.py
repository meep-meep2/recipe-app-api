from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGR_URL = reverse('recipe:ingredient-list')

def detail_url(ingr_id):
    #create and return a tag detail url
    return reverse('recipe:ingredient-detail', args=[ingr_id])

def create_user(email = 'user@example.com', password='pass123'):
    return get_user_model().objects.create_user(email, password)

class PublicIngredientsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        #Test that auth is required to call api

        res = self.client.get(INGR_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@example.com', 'testpass')
        self.client.force_authenticate(self.user) #All users using this client will be authenticated

    def test_retrieve_ingrs(self):
        #Test retrieving list of recipes

        Ingredient.objects.create(user = self.user, name='Carrot' )
        Ingredient.objects.create(user = self.user, name='Tofu' )

        res = self.client.get(INGR_URL)

        ingrs = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingrs, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        #Test list of recipes is limited to authenticated user
        other_user = get_user_model().objects.create_user('other@example.com', 'testpass')
        Ingredient.objects.create(user = other_user, name='Kale' )
        ingredient = Ingredient.objects.create(user = self.user, name='Chicken' )

        res = self.client.get(INGR_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):

        ingr = Ingredient.objects.create(user=self.user, name='Sugar')
        payload = {'name' : 'Pepper'}

        url = detail_url(ingr.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingr.refresh_from_db()
        self.assertEqual(ingr.name, payload['name'])

    def test_delete_ingredient(self):
        ingr = Ingredient.objects.create(user=self.user, name='Salt')

        url = detail_url(ingr.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingrs = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingrs.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        in1 = Ingredient.objects.create(user=self.user, name='noodles')
        in2 = Ingredient.objects.create(user=self.user, name='sauce')

        recipe = Recipe.objects.create(
            title='Spaghetti',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGR_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        ingr = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
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
        r1.ingredients.add(ingr)
        r2.ingredients.add(ingr)

        res = self.client.get(INGR_URL, {'assigned_only' : 1})
        self.assertEqual(len(res.data), 1)

