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
    
    def test_new_user_email_normalized(self):
        #Test email is normalized for new users.
        emails = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['Test2@Example.com', 'Test2@example.com'], 
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in emails:
            user = get_user_model().objects.create_user(email, 'password')
            self.assertEqual(user.email, expected)
        
    def test_new_user_without_email_raises_error(self):
        #Test that a new user without an email raises a ValueError.

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        #Test creating superuser
        user = get_user_model().objects.create_superuser('test@example.com', 'password')
        self.assertTrue(user.is_superuser) #Field provided by Permissions Mixin in UserManager class
        self.assertTrue(user.is_staff)






    





