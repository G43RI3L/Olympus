from django.urls import path

from . import views

urlpatterns = [
    path('workouts', views.workout_list, name='workout-list'),
    path('workouts/new', views.workout_create, name='workout-create'),
    path('workouts/<int:pk>', views.workout_detail, name='workout-detail'),
    path('workouts/<int:pk>/join', views.workout_join, name='workout-join'),
]
