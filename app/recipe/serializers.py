from rest_framework import serializers
from core.models import Recipe, Tag  #database holding info about recipes

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False) #adds nested serializer (a model within a model, so a single recipe can have a list of tag objects)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']

    #Custom logic that allows addition of tags (a nested serializer which is read only by default)
    def create(self, validated_data):
        tags = validated_data.pop('tags', []) #remove tag object from validated data (like get, but removes data from list if it exists. If DNE return empty list)
        recipe = Recipe.objects.create(**validated_data) #have to remove tag object bc Recipe is not expecting tag in its create method, wants you to add it as an additional field later -- see *2*

        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user = auth_user,
                **tag, #make sure all fields in tag are created
            )
            recipe.tags.add(tag_obj) #*2*
        return recipe





class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']





