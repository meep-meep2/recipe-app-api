from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient  #database holding info about recipes

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False) #adds nested serializer (a model within a model, so a single recipe can have a list of tag objects)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag, #make sure all fields in tag are created
            )
            recipe.tags.add(tag_obj) #*2*

    #Custom logic that allows addition of tags (a nested serializer which is read only by default)
    def create(self, validated_data): #overrides default

        tags = validated_data.pop('tags', []) #remove tag object from validated data (like get, but removes data from list if it exists. If DNE return empty list)
        recipe = Recipe.objects.create(**validated_data) #have to remove tag object bc Recipe is not expecting tag in its create method, wants you to add it as an additional field later -- see *2*
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        #overrides default
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance




class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']





