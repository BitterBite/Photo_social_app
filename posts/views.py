# posts/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from .models import Post, Comment, Like, Location, Image
from .serializers import PostSerializer, CommentSerializer, ImageSerializer
from django.shortcuts import render
from drf_spectacular.utils import extend_schema

def home(request):
    return render(request, 'home.html')

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="create_post",
        description="Создать новый пост с текстом, изображениями и геоданными",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Текст поста"},
                    "images": {
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                        "description": "Изображения (можно несколько)"
                    },
                    "location": {"type": "string", "description": "Геоданные в формате JSON"},
                },
                "required": ["text"],
            }
        },
        responses={201: PostSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        print("Authorization header:", request.META.get('HTTP_AUTHORIZATION'))
        print("Request data:", request.data)
        print("Request files:", request.FILES)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            raise PermissionDenied("Вы не можете удалить этот пост.")
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        operation_id="like_post",
        description="Поставить лайк посту",
        request=None,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Статус операции"}
                }
            }
        }
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        print("Authorization header:", request.META.get('HTTP_AUTHORIZATION'))
        post = self.get_object()
        Like.objects.get_or_create(post=post, user=request.user)
        return Response({'status': 'liked'}, status=201)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()
        post_pk = self.kwargs['post_pk']
        return Comment.objects.filter(post_id=post_pk)

    def perform_create(self, serializer):
        post_pk = self.kwargs['post_pk']
        post = Post.objects.get(pk=post_pk)
        serializer.save(author=self.request.user, post=post)