from typing import Union

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, \
    UpdateAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .serializers import UserGetSerializer, UserCreateSerializer, ProfileInfoSerializer, ResetPasswordSerializer, \
    ProfileUpdateSerializer

from .models import User


class LocationViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer
    filter_backends = [
        DjangoFilterBackend, ]
    # todo Нужен ли здесь вью сет

    def get_serializer_class(self) -> Union[type[UserCreateSerializer], type[UserGetSerializer]]:
        """serializer depending on the method"""
        if self.action == 'create':
            return UserCreateSerializer
        else:
            return UserGetSerializer


@method_decorator(csrf_exempt, name='dispatch')
class AuthenticationCreateAPI(CreateAPIView):
    # TODO Разобраться в этом получше
    """implementing user authentication/login system"""

    def post(self, request: Request, *args, **kwargs) -> JsonResponse:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse(UserGetSerializer(user).data, safe=False)
        else:
            raise exceptions.NotAuthenticated


class PasswordReset(UpdateAPIView):
    """redefining get_object method to get user.id from session token
    (django by default tries to find pk in web path)"""
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    def get_object(self) -> User:
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)

        return obj


# TODO Как я эту **** обошел? Создал кастом класс, который не чекает csrf, но надо нормально понять что он делает и вернуть его обратно
class UserDestroyAPIView(DestroyAPIView):
    """ implementing user logout view
     and redefining get_object method to get user. id from session token
     (same as we did in PasswordReset view)"""
    queryset = User.objects.all()
    serializer_class = ProfileInfoSerializer
    permission_classes = [IsAuthenticated, ]

    def destroy(self, request: Request, *args, **kwargs) -> JsonResponse:
        if isinstance(request.user, AnonymousUser):
            return JsonResponse({'status': 'failed'}, status=401, safe=False)
        logout(request)
        return JsonResponse({'status': 'succeed'}, status=200, safe=False)

    def get_object(self) -> User:
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)

        return obj


class UserProfileList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileInfoSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [TemplateHTMLRenderer]

    def get_object(self) -> User:
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)

        return obj

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'serializer': serializer.data}, template_name='lkredact.html')


class UserProfileEditList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileInfoSerializer
    permission_classes = [IsAuthenticated, ]
    renderer_classes = [TemplateHTMLRenderer]

    def get_object(self) -> User:
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'serializer': serializer.data}, template_name='lk.html')


class UserProfileEditAPIUpdate(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self) -> User:
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs): # todo хэндлить ошибки
        obj = self.get_object()
        obj.Mol.FIO = request.data.get('first_name').strip() + ' ' + request.data.get('last_name').strip() + ' ' + request.data.get('father_name').strip()
        obj.Mol.post = request.data.get('post', obj.Mol.post)
        obj.Mol.phone_num = request.data.get('phone_num', obj.Mol.phone_num)
        obj.Mol.save()
        obj.save()
        print(obj.Mol.FIO)
        return Response(status=200)


class LoginAPIView(ListAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        return Response(template_name='index.html')
