from rest_framework import viewsets , status, mixins, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 
from taggit.models import Tag
from rest_framework.decorators import api_view
from accounts.models import User
from articles.models import Article
from articles.serializers import ArticleSerializer, TagSerializer
from articles.filters import ArticleFilter
from django.views import View  #  4/13
from django.shortcuts import get_object_or_404  #  4/13

class ArticleView(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer 
    permission_classes=[IsAuthenticated]
    lookup_field='slug'
    filterset_class = ArticleFilter
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return [IsAuthenticatedOrReadOnly()]

        return super().get_permissions()
    
    #begin
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "articles": serializer.data,
            "articlesCount": queryset.count()
        })
    
    def create(self, request, *args, **kwargs):
        try:
            article_data = request.data.get('article')

            # 确保 scheduledAt 为空字符串时转换为 None  3/31
            if 'scheduledAt' in article_data and article_data['scheduledAt'] == "":
                article_data['scheduledAt'] = None
                #标题检测4.01
            if Article.objects.filter(title=article_data.get("title")).exists():
             return Response({"error": "文章标题已存在，请更换标题"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=article_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"article":serializer.data}, status=status.HTTP_201_CREATED)
        
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)    
            
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, slug, *args, **kwargs):
        if request.method == 'POST':
            try:
                article = Article.objects.get(slug=slug) 
                
                if article.favorites.filter(id=request.user.id).exists():
                    return Response({"errors": {
                        "body": [
                            "Already Favourited Article"
                        ]
                    }})
                    
                article.favorites.add(request.user)
                serializer = self.get_serializer(article)
                return Response({"article": serializer.data})
                   
            except Exception:
                return Response({"errors": {
                    "body": [
                        "Bad Request"
                    ]
                }}, status=status.HTTP_404_NOT_FOUND)   
        else:
            try:
                
                article = Article.objects.get(slug=slug)
                if article.favorites.get(id=request.user.id):
                    article.favorites.remove(request.user.id)
                    serializer = self.get_serializer(article)
                    return Response({ "article": serializer.data })
                
                else:
                    raise Exception
            
            except Exception:
                return Response({"errors": {
                    "body": [
                        "Bad Request"
                    ]
                }}, status=status.HTTP_404_NOT_FOUND)  
            
    @action(detail=False)
    def feed(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"errors": {
                "body": ["Authentication required"]
            }}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            followed_authors = User.objects.filter(followers=request.user)
            queryset = self.get_queryset()
            articles = queryset.filter(
                author__in=followed_authors).order_by('-created')
            queryset = self.filter_queryset(articles)
            
            serializer = self.get_serializer(queryset, many=True)
            response = {
                'articles': serializer.data,
                'articlesCount': len(serializer.data)
            }
            return Response(response)
               
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)   
        
    def retrieve(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = queryset.get(slug=slug)
            serializer = self.get_serializer(article)

            if request.user.is_authenticated:  #  4/14
                print("当前用户：{request.user.email}，正在添加浏览记录")
                if article in request.user.recently_viewed_articles.all():
                    request.user.recently_viewed_articles.remove(article)
                request.user.recently_viewed_articles.add(article)
            
            return Response({"article": serializer.data})
            
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)     
    
    def update(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = queryset.get(slug=slug)
            
            if request.user != article.author:
                return Response({"errors": {
                    "body": [
                        "UnAuthorized Action"
                    ]
                }}, status=status.HTTP_401_UNAUTHORIZED)
                
            request_data = request.data.get('article')
            serializer = self.get_serializer(article, data=request_data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({"article": serializer.data})
        
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND) 
    
    def destroy(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = queryset.get(slug=slug)
        
            if request.user != article.author:
                return Response({"errors": {
                    "body": [
                        "UnAuthorized Action"
                    ]
                }}, status=status.HTTP_401_UNAUTHORIZED)
                
            article.delete()
            return Response(status=status.HTTP_200_OK)
          
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)          

            
class TagView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names=['get',]
    

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            tags = [element.name for element in queryset]
            serializer = self.get_serializer({ 'tags': tags })
            return Response(serializer.data)
            
        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def check_title(request):
    title = request.query_params.get('title', None)
    if title:
        exists = Article.objects.filter(title=title).exists()
        return Response({"exists": exists})
    return Response({"error": "Title parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def viewed_articles(request):
    try:
        user = request.user
        articles = user.recently_viewed_articles.all().order_by('-id')  # 或按时间排序
        serializer = ArticleSerializer(articles, many=True, context={'request': request})
        return Response({
            "articles": serializer.data,
            "articlesCount": len(serializer.data)
        }) # 4/14
    except Exception:
        return Response({"errors": {
            "body": [
                "Bad Request"
            ]
        }}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def clear_history(request):
    user_id = request.user.id
    try:
        user = User.objects.get(id=user_id)
        user.recently_viewed_articles.clear()
        return Response({"message": "History cleared successfully."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
