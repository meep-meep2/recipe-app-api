#Fields:
#email, name, is_active, is_staff

#Model Manager
#Custom Logic
    #hash password 
from django.test import TestCase
from django.contrib.auth import get_user_model #Helper func from django

class ModelsTests(TestCase):
    '''Test Models '''

    def test_create_user_with_email_successful(self):
        #Was able to successfully create user with email address.

        email = "test@example.com"
        password = 'testpassword'

        #Creates user with just email and password
        user = get_user_model().objects.create_user(email = email,
                                                    password = password )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    





