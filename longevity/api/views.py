from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from core.tasks import send_otp_task
from users.models import User

from .permissions import AdminOnly
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer


class SignUpView(
    CreateModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.data)
        email = serializer.data["email"]
        user = get_object_or_404(User, email=email)
        send_otp_task.delay(user.email)
        return Response(serializer.data)


class TokenView(TokenViewBase):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('email',)

    def get_object(self):
        user_email = self.kwargs['pk']
        user = get_object_or_404(User, email=user_email)
        return user

    @action(methods=['get', 'patch', 'put', 'delete'], detail=False)
    def me(self, request):
        if request.method == 'GET':
            user = User.objects.get(email=request.user.email)
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        if request.method == 'PATCH' or request.method == 'PUT':
            partial = True if request.method == 'PATCH' else False
            user = User.objects.get(username=request.user.username)
            data = request.data.copy()
            data['role'] = user.role
            serializer = self.get_serializer(
                user,
                data=data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(user, '_prefetched_objects_cache', None):
                user._prefetched_objects_cache = {}

            return Response(serializer.data)

        if request.method == 'DELETE':
            raise MethodNotAllowed(method='DELETE')

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return (AdminOnly(),)
