from django.test import TestCase
from django.contrib.auth import get_user_model #Helper func from django
from django.urls import reverse 
from django.test import Client


class AdminSiteTests(TestCase):

    def setUp(self):
        #Create user and client
        self.client = Client() #Django Test Client - allows usage of HTTP requests
        self.admin_user = get_user_model().objects.create_superuser('user@example.com', 'testpass')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(email='test@example.com', password='testpass', name='Test User')
    
    def test_users_list(self):
        #Test that users are listed on page
        url = reverse('admin:core_user_changelist') #defined by django admin
        res = self.client.get(url) #makes a HTTP get request

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        url = reverse('admin:core_user_change', args=[self.user.id]) #defined by django admin
        res = self.client.get(url)

        #Ensure pages loaded correctly
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add') #defined by django admin
        res = self.client.get(url)

        #Ensure pages loaded correctly
        self.assertEqual(res.status_code, 200)



