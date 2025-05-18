# from rest_framework.decorators import api_view, action
# from rest_framework.response import Response
# from rest_framework import status, views, viewsets
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
#
# from accounts.models import User
# from accounts.serializers import UserSerializer, ProfileSerializer
#
#
# @api_view(['POST',])
# def account_registration(request):
#     try:
#         user_data = request.data.get('user')
#
#         serializer = UserSerializer(data=user_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)
#
#     except Exception:
#         return Response(status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['POST',])
# def account_login(request):
#     try:
#         user_data = request.data.get('user')
#         user = authenticate(email=user_data['email'], password=user_data['password'])
#         if user is None:
#             return Response({"errors": {
#                 "body": ["Invalid email or password"]
#             }}, status=status.HTTP_401_UNAUTHORIZED)
#
#         serializer = UserSerializer(user)
#         jwt_token = RefreshToken.for_user(user)
#         serializer_data = serializer.data
#         serializer_data['token'] = str(jwt_token.access_token)
#         serializer_data['username'] = user.username
#         response_data = {
#             "user": serializer_data,
#         }
#         return Response(response_data, status=status.HTTP_202_ACCEPTED)
#
#     except Exception as e:
#         return Response({"errors": {
#             "body": ["Authentication failed"]
#         }}, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserView(views.APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, format=None):
#         user = self.request.user
#         serializer = UserSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def put(self, request, format=None, pk=None):
#         user = self.request.user
#         user_data = request.data.get('user')
#
#         user.email = user_data['email']
#         user.bio = user_data['bio']
#         user.image = user_data['image']
#         user.save()
#
#         serializer = UserSerializer(user)
#
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class ProfileDetailView(viewsets.ModelViewSet):
#
#     queryset = User.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]
#     lookup_field = 'username'
#     http_method_names = ['get', 'post', 'delete']
#
#     def get_permissions(self):
#         if self.action == 'list':
#             return [IsAuthenticatedOrReadOnly(),]
#         return super().get_permissions()
#
#     def list(self, request, username=None, *args, **kwargs):
#         try:
#             profile = User.objects.get(username=username)
#             serializer = self.get_serializer(profile)
#             return Response({"profile": serializer.data})
#
#         except Exception:
#             return Response({"errors": {
#                 "body": [
#                     "Invalid User"
#                 ]
#             }})
#
#     @action(detail=True, methods=['post', 'delete'])
#     def follow(self, request, username=None, *args, **kwargs):
#         if request.method == 'POST':
#
#             profile = self.get_object()
#             follower = request.user
#             if profile == follower:
#                 return Response({"errors": {
#                     "body": [
#                         "Invalid follow Request"
#                     ]
#                 }}, status=status.HTTP_400_BAD_REQUEST)
#
#             profile.followers.add(follower)
#             serializer = self.get_serializer(profile)
#             return Response({ "profile": serializer.data })
#
#         elif request.method == 'DELETE':
#
#             profile = self.get_object()
#             follower = request.user
#             if profile == follower:
#                 return Response({"errors": {
#                     "body": [
#                         "Invalid follow Request"
#                     ]
#                 }}, status=status.HTTP_400_BAD_REQUEST)
#
#             if not profile.followers.filter(pk=follower.id).exists():
#                 return Response({"errors": {
#                     "body": [
#                         "Invalid follow Request"
#                     ]
#                 }}, status=status.HTTP_400_BAD_REQUEST)
#
#             profile.followers.remove(follower)
#             serializer = self.get_serializer(profile)
#             return Response({ "profile": serializer.data })


# 修改后的视图文件
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
