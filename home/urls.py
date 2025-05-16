from django.urls import path

from home import views

app_name = 'home'

urlpatterns = [
    path('', views.search_view, name='search_view'),

]
