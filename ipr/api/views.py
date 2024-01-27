from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions, viewsets, filters
from rest_framework.response import Response

from .permissions import IsAuthenticatedReadOnly
from .serializers import (
    CommentSerializer,
    CreateTaskSerializer,
    TaskSerializer,
    UserSerializer,
    CreateIprSerializer,
    ReadIprSerializer,
)
from iprs.models import Ipr, Task
from users.models import User


class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = (
        "name",
        "lastname",
    )
    search_fields = ("lastname",)
    ordering_fields = ("lastname",)
    ordering = ("lastname",)


class MeUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedReadOnly,)

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            return qs.filter(pk=self.request.user.pk)
        except ObjectDoesNotExist:
            return qs.none()


class SubordinateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().prefetch_related("subordinates")
    serializer_class = UserSerializer

    def list(self, request, pk=None):
        user = get_list_or_404(User, pk__exact=pk)
        subordinates = user[0].subordinates.all()
        serializer = self.get_serializer(instance=subordinates, many=True)
        response = {"username": user[0].username, "subordinates": serializer.data}
        return Response(response)


class IprViewSet(viewsets.ModelViewSet):
    queryset = Ipr.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "status",
        "end_date",
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReadIprSerializer
        return CreateIprSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """
        Если руководитель/подчиненный определяется в модели User типом bool:
        """
        if self.request.user.superior:
            return Ipr.objects.filter(author=self.request.user)
        if self.request.user.subordinates:
            return Ipr.objects.filter(employee=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskSerializer
        return CreateTaskSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs.get("task_id"))
        serializer.save(author=self.request.user, task=task)

    def get_queryset(self):
        task = get_object_or_404(Task, id=self.kwargs.get("task_id"))
        return task.comments.all()
