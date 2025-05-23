"""
URL configuration for con_sear project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import UserAPIList, UserAPIUpdate, UserAPIDestroy

# from user.views import RegisterView, UserListView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'), namespace='home')),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/user/', UserAPIList.as_view()),
    path('api/v1/user/<int:pk>/', UserAPIUpdate.as_view()),
    path('api/v1/userdelete/<int:pk>/', UserAPIDestroy.as_view()),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('api/register/', RegisterView.as_view(), name='auth_register'),
    # path('api/users/', UserListView.as_view(), name='user-list'),
]

