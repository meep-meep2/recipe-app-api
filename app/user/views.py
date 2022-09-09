from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES #optional

class ManageUserView(generics.RetrieveUpdateAPIView): #view given by rest framework lib to provide functionality for retrieving and updating data in the database

    #Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self): #overrides typical behavior (gets object for HTTP get_request() or any other requests made to the api) returns user instead
        #get and return the authenticated user
        return self.request.user
