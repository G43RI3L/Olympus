from django.contrib import admin

from .models import Workout, WorkoutParticipant


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'workout_type', 'location', 'scheduled_for', 'confirmed_count')
    list_filter = ('workout_type',)
    search_fields = ('title', 'location', 'creator__username')


@admin.register(WorkoutParticipant)
class WorkoutParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'status', 'joined_at')
    list_filter = ('status',)
