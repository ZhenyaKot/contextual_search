import requests
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import RegisterForm, LoginForm
from .models import User
from .serializers import UserSerializer


class UserAPIList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.AllowAny()]  # Регистрация доступна всем
        return [permissions.IsAdminUser()]  # Просмотр списка только админам

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT токен после регистрации
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class UserAPIDestroy(generics.DestroyAPIView):  # Только удаление!
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Отправляем данные в API
                response = requests.post(
                    'http://127.0.0.1:8000/api/v1/user/',
                    json={
                        'username': form.cleaned_data['username'],
                        'email': form.cleaned_data['email'],
                        'password': form.cleaned_data['password1']
                    },
                    timeout=5
                )

                if response.status_code == 201:
                    # Получаем токены для нового пользователя
                    auth_response = requests.post(
                        'http://127.0.0.1:8000/api/v1/token/',
                        json={
                            'username': form.cleaned_data['username'],
                            'password': form.cleaned_data['password1']
                        },
                        timeout=5
                    )

                    if auth_response.status_code == 200:
                        token_data = auth_response.json()
                        return JsonResponse({
                            'access': token_data['access'],
                            'refresh': token_data['refresh']
                        })

                    return JsonResponse({
                        'errors': {'__all__': ['Ошибка авторизации после регистрации']}
                    }, status=400)

                # Обработка ошибок API
                errors = response.json()
                return JsonResponse({'errors': errors}, status=response.status_code)

            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    'errors': {'__all__': [f'Ошибка соединения с сервером: {str(e)}']}
                }, status=500)
            except ValueError as e:
                return JsonResponse({
                    'errors': {'__all__': ['Ошибка обработки ответа сервера']}
                }, status=500)

        # Ошибки валидации формы
        errors = {}
        for field in form.errors:
            errors[field] = form.errors[field]
        return JsonResponse({'errors': errors}, status=400)

    # GET запрос - показать пустую форму
    form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Получаем токен из API
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/token/',
                json={
                    'username': form.cleaned_data['username'],
                    'password': form.cleaned_data['password']
                }
            )

            if response.status_code == 200:
                token_data = response.json()
                request.session['access_token'] = token_data['access']
                request.session['refresh_token'] = token_data['refresh']
                request.session['username'] = form.cleaned_data['username']
                return redirect('home:search_view')
    else:
        form = LoginForm()
    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    # Очищаем сессию Django
    logout(request)

    # Очищаем JWT токены из сессии
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    if 'username' in request.session:
        del request.session['username']

    # Очищаем cookies
    response = redirect('home:search_view')
    response.delete_cookie('sessionid')

    return response
