from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Workout, WorkoutParticipant

User = get_user_model()


class WorkoutModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joao', password='senha123')

    def test_workout_no_passado_e_invalido(self):
        workout = Workout(
            creator=self.user,
            title='Treino ontem',
            location='Academia',
            scheduled_for=timezone.now() - timedelta(days=1),
        )
        with self.assertRaises(Exception):
            workout.full_clean()

    def test_confirmed_count_e_is_full(self):
        workout = Workout.objects.create(
            creator=self.user,
            title='Treino de perna',
            location='Academia X',
            scheduled_for=timezone.now() + timedelta(days=1),
            max_participants=1,
        )
        self.assertEqual(workout.confirmed_count, 0)
        self.assertFalse(workout.is_full)

        WorkoutParticipant.objects.create(
            workout=workout, user=self.user, status=WorkoutParticipant.Status.CONFIRMED
        )
        self.assertEqual(workout.confirmed_count, 1)
        self.assertTrue(workout.is_full)

    def test_nao_permite_participacao_duplicada(self):
        workout = Workout.objects.create(
            creator=self.user,
            title='Corrida',
            location='Parque',
            scheduled_for=timezone.now() + timedelta(days=1),
        )
        WorkoutParticipant.objects.create(workout=workout, user=self.user)
        with self.assertRaises(Exception):
            WorkoutParticipant.objects.create(workout=workout, user=self.user)


class WorkoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='maria', password='senha123')
        self.client.login(username='maria', password='senha123')

    def test_criar_treino_via_view(self):
        response = self.client.post(reverse('workout-create'), {
            'title': 'Yoga no parque',
            'description': 'Trazer tapete',
            'workout_type': 'OTHER',
            'location': 'Parque Central',
            'scheduled_for': (timezone.now() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        })
        self.assertEqual(Workout.objects.count(), 1)
        workout = Workout.objects.first()
        self.assertEqual(workout.title, 'Yoga no parque')
        # Quem cria já entra como participante confirmado.
        self.assertTrue(
            WorkoutParticipant.objects.filter(workout=workout, user=self.user).exists()
        )
        self.assertRedirects(response, reverse('workout-detail', kwargs={'pk': workout.pk}))

    def test_marcar_e_desmarcar_presenca(self):
        outro_user = User.objects.create_user(username='pedro', password='senha123')
        workout = Workout.objects.create(
            creator=outro_user,
            title='Corrida',
            location='Parque',
            scheduled_for=timezone.now() + timedelta(days=1),
        )

        # Marca presença
        self.client.get(reverse('workout-join', kwargs={'pk': workout.pk}))
        self.assertTrue(
            WorkoutParticipant.objects.filter(workout=workout, user=self.user).exists()
        )

        # Desmarca presença (segunda chamada deve remover)
        self.client.get(reverse('workout-join', kwargs={'pk': workout.pk}))
        self.assertFalse(
            WorkoutParticipant.objects.filter(workout=workout, user=self.user).exists()
        )

    def test_nao_marca_presenca_com_vagas_esgotadas(self):
        criador = User.objects.create_user(username='ana', password='senha123')
        workout = Workout.objects.create(
            creator=criador,
            title='Crossfit',
            location='Box X',
            scheduled_for=timezone.now() + timedelta(days=1),
            max_participants=1,
        )
        WorkoutParticipant.objects.create(workout=workout, user=criador)

        self.client.get(reverse('workout-join', kwargs={'pk': workout.pk}))
        self.assertFalse(
            WorkoutParticipant.objects.filter(workout=workout, user=self.user).exists()
        )
