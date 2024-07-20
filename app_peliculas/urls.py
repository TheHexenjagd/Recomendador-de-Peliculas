from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_movies, name='search_movies'),
    path('search/random/', views.search_random_movie, name='search_random_movie'),
]
