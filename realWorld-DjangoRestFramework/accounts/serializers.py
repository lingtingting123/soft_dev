from rest_framework import serializers
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'bio', 'image')
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == 'password':
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance


class ProfileWrapperSerializer(serializers.Serializer):
    """
    符合RealWorld规范的profile包装器
    响应格式: { "profile": { ... } }
    """
    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        request = self.context.get('request')
        following = False
        if request and request.user.is_authenticated:
            following = obj.followers.filter(pk=request.user.id).exists()

        return {
            'username': obj.username,
            'bio': obj.bio,
            'image': obj.image,
            'following': following
        }


# 保留原ProfileSerializer以备他用（如嵌套在其他序列化器中）
class ProfileSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'bio', 'image', 'following')

    def get_following(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.followers.filter(pk=user.id).exists()
        return False

class UserWrapperSerializer(serializers.Serializer):
    """
    符合RealWorld规范的user包装器
    响应格式: { "user": { ... } }
    """
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        data = UserSerializer(obj).data
        if hasattr(self, 'token'):
            data['token'] = self.token
        return data
