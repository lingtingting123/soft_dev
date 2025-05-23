from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status, views, viewsets
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from accounts.models import User
from accounts.serializers import (
    UserSerializer,
    ProfileSerializer,
    ProfileWrapperSerializer,
    UserWrapperSerializer
)


@api_view(['POST'])
def account_registration(request):
    try:
        user_data = request.data.get('user', {})  # 更安全的获取方式

        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 使用包装器序列化响应
        wrapper = UserWrapperSerializer(user)
        return Response(wrapper.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"errors": {"body": [str(e)]}},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def account_login(request):
    try:
        user_data = request.data.get('user', {})
        user = authenticate(
            email=user_data.get('email'),
            password=user_data.get('password')
        )

        if user is None:
            return Response(
                {"errors": {"body": ["Invalid credentials"]}},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 使用包装器并添加token
        wrapper = UserWrapperSerializer(user)
        wrapper.token = str(RefreshToken.for_user(user).access_token)
        return Response(wrapper.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"errors": {"body": [str(e)]}},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wrapper = UserWrapperSerializer(request.user)
        return Response(wrapper.data)

    def put(self, request):
        user_data = request.data.get('user', {})
        serializer = UserSerializer(
            request.user,
            data=user_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        wrapper = UserWrapperSerializer(request.user)
        return Response(wrapper.data)

    def delete(self, request):
        user = request.user
        try:
            # 删除用户本身
            user.delete()

            return Response({"message": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(
                {"errors": {"body": [str(e)]}},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileDetailView(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ['follow', 'unfollow']:
            return ProfileSerializer
        return ProfileWrapperSerializer

    def retrieve(self, request, username=None):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"errors": {"body": ["User not found"]}},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, username=None):
        profile = self.get_object()
        follower = request.user

        if profile == follower:
            return Response(
                {"errors": {"body": ["Cannot follow yourself"]}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if profile.followers.filter(pk=follower.id).exists():
                return Response(
                    {"errors": {"body": ["Already following"]}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            profile.followers.add(follower)

        elif request.method == 'DELETE':
            if not profile.followers.filter(pk=follower.id).exists():
                return Response(
                    {"errors": {"body": ["Not following"]}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            profile.followers.remove(follower)

        # 使用ProfileSerializer返回简化数据
        serializer = self.get_serializer(profile)
        return Response({"profile": serializer.data})  


