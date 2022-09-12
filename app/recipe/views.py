from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    #View for manage recipe apis
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all() #objects available for this viewset (DOM objects?)
    authentication_classes = [TokenAuthentication]
    permission_classes =[IsAuthenticated]

    def get_queryset(self):
        #instead of returning all objects defined, filter by authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        #Return serializer class for request

        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer): #overriding django rest_framework method
        serializer.save(user=self.request.user)


#using viewset bc Create Read Update Delete on a model - has to be generic so we can add the mixin
class TagViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                 mixins.ListModelMixin, viewsets.GenericViewSet):
    #Manage tags in the db
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #only want to return tags associated with authenticated user.
    def get_queryset(self):
        #instead of returning all objects defined, filter by authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')
                #reverse name order

    #mixin.UpdateModelMixin - automatically updates model for you apparently so we don't have to write a method for it.

class IngredientViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                 mixins.ListModelMixin, viewsets.GenericViewSet):
    #Manage tags in the db
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #only want to return tags associated with authenticated user.
    def get_queryset(self):
        #instead of returning all objects defined, filter by authenticated user
        return self.queryset.filter(user=self.request.user).order_by('-name')
                #reverse name order
