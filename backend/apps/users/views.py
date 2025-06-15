from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from djoser.views import UserViewSet

from .models import User, Subscription
from .serializers import (
    UserProfileAvatarSerializer,
    UserShortSerializer,
    SubscriptionSerializer,
    CreateSubscriptionSerializer,
)


class UserProfileViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserShortSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me",
    )
    def me(self, request):
        serializer = UserShortSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["put", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="avatar",
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            if "avatar" not in request.data:
                return Response(
                    {"error": "Поле 'avatar' обязательно."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = UserProfileAvatarSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.avatar:
            request.user.avatar.delete()
            request.user.avatar = None
            request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="subscriptions",
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(followers__subscriber=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="subscribe",
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)

        if request.method == "POST":
            if request.user == author:
                return Response(
                    {"error": "Нельзя подписаться на самого себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CreateSubscriptionSerializer(
                data={"subscriber": request.user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(
            subscriber=request.user, author=author
        )
        if not subscription.exists():
            return Response(
                {"error": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
