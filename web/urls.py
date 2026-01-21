from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/solve/', views.solve_maze, name='solve_maze'),
    path('api/generate/', views.generate_maze, name='generate_maze'),
    path('api/compare/', views.compare_algos, name='compare_algos'),
]
