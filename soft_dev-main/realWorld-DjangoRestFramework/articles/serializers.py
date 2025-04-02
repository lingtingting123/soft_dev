from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from taggit.models import Tag
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from articles.models import Article


User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('username', 'bio', 'image', 'following')
        
    def get_following(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.followers.filter(pk=user.id).exists()
        return False

    
class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)
    description = serializers.CharField(source='summary')
    body = serializers.CharField(source='content')
    tagList = TagListSerializerField(source='tags', required=False)
    createdAt = serializers.DateTimeField(source='created',format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
    updatedAt = serializers.DateTimeField(source='updated',format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField(read_only=True)
    scheduledAt = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ', required=False, allow_null=True)  # 新增字段 3/28

    # class Meta:
    #     model = Article
    #     fields = ['slug', 'title', 'description', 'body', 'tagList', 'createdAt',
    #               'updatedAt', 'favorited', 'favoritesCount', 'author']
    #     read_only_fields = ['slug', 'createdAt', 'updatedAt', 'author']
    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body', 'tagList', 'createdAt',
                  'updatedAt', 'favorited', 'favoritesCount', 'author', 'scheduledAt']  # 添加 scheduledAt 到 fields 3/28
        read_only_fields = ['slug', 'createdAt', 'updatedAt', 'author']

    def validate_scheduledAt(self, value):  # AI codes 3/31
        if value == "":
            return None  # 确保 Django 不会因空字符串报错
        return value

    def get_author(self, obj):
        request = self.context.get('request') 
        # serializer = AuthorSerializer(request.user, context={'request': request})
        serializer = AuthorSerializer(obj.author, context={'request': request})
        return serializer.data
    
    def get_favorited(self, instance):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return instance.favorites.filter(pk=request.user.pk).exists()
        return False
    
    def get_favoritesCount(self, instance):
        return instance.favorites.count()
       
    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     article = Article(
    #         author=self.context['request'].user,
    #         **validated_data
    #     )
    #     article.save()
    #     article.tags.add(*tags)
    #     return article
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        scheduled_at = validated_data.pop('scheduledAt', None) # 3/31
        article = Article(
            author=self.context['request'].user,
            scheduledAt=scheduled_at, # 3/31
            **validated_data
        )
        article.save()

        article.tags.add(*tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        instance.tags.clear()
        instance.tags.add(*tags)
        
        return instance
    
    
class TagSerializer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.CharField()
    )
        