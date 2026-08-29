from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()


class Workout(models.Model):
    """
    Um treino que um usuário cria e outros podem marcar presença.
    Ex: "Corrida no parque", "Treino de perna na academia X", etc.
    """

    class WorkoutType(models.TextChoices):
        RUNNING = 'RUNNING', 'Corrida'
        GYM = 'GYM', 'Academia'
        SWIMMING = 'SWIMMING', 'Natação'
        CYCLING = 'CYCLING', 'Ciclismo'
        SPORTS = 'SPORTS', 'Esporte coletivo'
        OTHER = 'OTHER', 'Outro'

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_workouts',
    )
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    workout_type = models.CharField(
        max_length=20,
        choices=WorkoutType.choices,
        default=WorkoutType.OTHER,
    )
    location = models.CharField(max_length=200)
    scheduled_for = models.DateTimeField(
        help_text='Data e hora em que o treino vai acontecer.'
    )
    # Quantas pessoas cabem no treino. Null = sem limite.
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return f'{self.title} ({self.scheduled_for:%d/%m/%Y %H:%M})'

    def clean(self):
        # Regra de negócio: não faz sentido criar um treino no passado.
        if self.scheduled_for and self.scheduled_for < timezone.now():
            raise ValidationError('A data do treino não pode estar no passado.')

    @property
    def confirmed_count(self):
        return self.participants.filter(status=WorkoutParticipant.Status.CONFIRMED).count()

    @property
    def is_full(self):
        if self.max_participants is None:
            return False
        return self.confirmed_count >= self.max_participants

    @property
    def is_past(self):
        return self.scheduled_for < timezone.now()


class WorkoutParticipant(models.Model):
    """
    Relação entre um usuário e um treino que ele marcou presença.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendente'
        CONFIRMED = 'CONFIRMED', 'Confirmado'
        DECLINED = 'DECLINED', 'Recusado'

    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='participants',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_participations',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Um usuário só pode ter UMA participação por treino (evita duplicidade
        # de "marcar presença" duas vezes, que era um risco no design antigo
        # de LikePost, que não tinha essa garantia no nível do banco).
        constraints = [
            models.UniqueConstraint(
                fields=['workout', 'user'], name='unique_participant_per_workout'
            )
        ]

    def __str__(self):
        return f'{self.user.username} em {self.workout.title} ({self.status})'
