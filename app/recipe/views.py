from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
        elif self.action == 'upload-image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer): #overriding django rest_framework method
        serializer.save(user=self.request.user)

    #must apply this action to a specific recipe
    @action(methods=['POST'], detail=True, url_path='upload-image' )
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
