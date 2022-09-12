from decimal import Decimal
import tempfile
import os
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    #Create and return a recipe detail URL
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

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

class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@example.com', 'testpass')
        self.client.force_authenticate(self.user) #All users using this client will be authenticated


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

    def test_partial_update(self):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user,
            title = 'Sample title',
            link = original_link,
        )

        payload = {'title': 'New title'}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        recipe = create_recipe(
            title = 'Sample recipe name',
            user = self.user,
            description = 'Sample recipe description',
            link = 'http://example.com/recipe.pdf',
        )

        payload = {
            'title' : 'Sample2 recipe name',
            'time_minutes' : 10,
            'price' : Decimal('2.50'), #shouldn't use decimal or float fields, should use integer for money
            'description' : 'NEW recipe description',
            'link' : 'http://example.com/recipe.pdf'
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        new_user = create_user(email = 'user2@example.com', password ='testpass')
        recipe = create_recipe(user=self.user)

        payload = { 'user' : new_user.id }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)


    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        new_user = create_user(email = 'user2@example.com', password ='testpass')
        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    #Nested Serializer Tests ---

    def test_create_recipe_with_new_tags(self):
        payload = {
            'title' : 'Sample2 recipe name',
            'time_minutes' : 10,
            'price' : Decimal('2.50'), #shouldn't use decimal or float fields, should use integer for money
            'tags' : [{'name': 'Thai'}, {'name' : 'Dinner'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)    #helping provide more info about why the test failed
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        tag = Tag.objects.create(user = self.user, name='Italian')
        payload = {
            'title' : 'Sample2 recipe name',
            'time_minutes' : 10,
            'price' : Decimal('2.50'), #shouldn't use decimal or float fields, should use integer for money
            'tags' : [{'name': 'Italian'}, {'name' : 'Breakfast'}],
        } #first tag should not be recreated it should just attach itself, the second tag should be created bc it doesnt exist yet.

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)    #helping provide more info about why the test failed
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())
            #Ensures that the specific tag 'tag' exists in the tags assigned to the recipe.

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        #Test creating tag when updating a recipe
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all()) #tags not cached when creating recipe (bc nested serializer) so need to do refresh from db on recipe

    def test_update_recipe_assign_tag(self):
        #Test assigning an existing tag when updating a recipe
        tag_soup = Tag.objects.create(user=self.user, name='Soup')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag_soup)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_soup, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag_soup = Tag.objects.create(user=self.user, name='Soup')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag_soup)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    #---------- Ingredients --------------------------

    def test_create_recipe_with_new_ingredients(self):
        payload = {
            'title' : 'Sample2 recipe name',
            'time_minutes' : 10,
            'price' : Decimal('2.50'), #shouldn't use decimal or float fields, should use integer for money
            # 'tags' : [{'name': 'Thai'}, {'name' : 'Dinner'}],
            'ingredients' : [{'name': 'ingr1'}, {'name': 'ingr2'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)    #helping provide more info about why the test failed
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingr in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name = ingr['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        ingr = Ingredient.objects.create(user = self.user, name='ingr1')
        payload = {
            'title' : 'Sample2 recipe name',
            'time_minutes' : 10,
            'price' : Decimal('2.50'), #shouldn't use decimal or float fields, should use integer for money
            'ingredients' : [{'name': 'ingr1'}, {'name': 'ingr2'}],
        } #first tag should not be recreated it should just attach itself, the second tag should be created bc it doesnt exist yet.

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)    #helping provide more info about why the test failed
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingr, recipe.ingredients.all())
            #Ensures that the specific tag 'tag' exists in the tags assigned to the recipe.

        for ingr in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name = ingr['name'],
                user = self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):

        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'Peanuts'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingr = Ingredient.objects.get(user=self.user, name='Peanuts')
        self.assertIn(new_ingr, recipe.ingredients.all()) #tags not cached when creating recipe (bc nested serializer) so need to do refresh from db on recipe

    def test_update_recipe_assign_ingredient(self):

        ingr1 = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(ingr1)

        ingr2 =  Ingredient.objects.create(user=self.user, name='Pepper')
        payload = {'ingredients': [{'name': 'Pepper'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingr2, recipe.ingredients.all())
        self.assertNotIn(ingr1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        ingr = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = create_recipe(user = self.user)
        recipe.ingredients.add(ingr)

        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'pass123',
        )
        self.client.force_authenticate(self.user) #All users using this client will be authenticated
        self.recipe = create_recipe(user=self.user)

    def tearDown(self): #helps remove clutter (test images)
        self.recipe.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10)) #Creates a fake test image to "upload"
            img.save(image_file, format='JPEG')
            image_file.seek(0) #need to return to start of file to upload it (auto goes to end when you save it)
            payload = {'image' : image_file}
            res = self.client.put(url, payload, format='multipart') #best way to handle file uploads
            #^^ creates temp file inside this method that will be deleted once test is finished.

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        #Test uploading invalid image.
        url = image_upload_url(self.recipe.id)
        payload = {'image' : 'notanimg'}
        res = self.client.put(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
















