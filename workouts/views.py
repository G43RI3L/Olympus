from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Workout, WorkoutParticipant


@login_required(login_url='signin')
def workout_list(request):
    """Lista os próximos treinos disponíveis para marcar presença."""
    workouts = Workout.objects.filter(
        scheduled_for__gte=timezone.now()
    ).select_related('creator').prefetch_related('participants')

    # IDs dos treinos em que o usuário logado já confirmou presença,
    # pra podermos mostrar "Cancelar presença" em vez de "Marcar presença".
    my_participations = set(
        WorkoutParticipant.objects.filter(
            user=request.user,
            status=WorkoutParticipant.Status.CONFIRMED,
        ).values_list('workout_id', flat=True)
    )

    return render(request, 'workouts/list.html', {
        'workouts': workouts,
        'my_participations': my_participations,
    })


@login_required(login_url='signin')
def workout_create(request):
    """Cria um novo treino."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        workout_type = request.POST.get('workout_type', Workout.WorkoutType.OTHER)
        location = request.POST.get('location', '').strip()
        scheduled_for = request.POST.get('scheduled_for')
        max_participants = request.POST.get('max_participants') or None

        if not title or not location or not scheduled_for:
            messages.error(request, 'Preencha título, local e data do treino.')
            return redirect('workout-create')

        workout = Workout(
            creator=request.user,
            title=title,
            description=description,
            workout_type=workout_type,
            location=location,
            scheduled_for=scheduled_for,
            max_participants=max_participants,
        )

        try:
            workout.full_clean()
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return redirect('workout-create')

        workout.save()

        # Quem cria o treino já entra confirmado automaticamente.
        WorkoutParticipant.objects.create(
            workout=workout,
            user=request.user,
            status=WorkoutParticipant.Status.CONFIRMED,
        )

        messages.success(request, 'Treino criado com sucesso!')
        return redirect('workout-detail', pk=workout.pk)

    return render(request, 'workouts/create.html', {
        'workout_types': Workout.WorkoutType.choices,
    })


@login_required(login_url='signin')
def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk)
    participants = workout.participants.filter(
        status=WorkoutParticipant.Status.CONFIRMED
    ).select_related('user')

    is_participant = participants.filter(user=request.user).exists()

    return render(request, 'workouts/detail.html', {
        'workout': workout,
        'participants': participants,
        'is_participant': is_participant,
    })


@login_required(login_url='signin')
def workout_join(request, pk):
    """Marca ou desmarca a presença do usuário logado em um treino."""
    workout = get_object_or_404(Workout, pk=pk)

    existing = WorkoutParticipant.objects.filter(
        workout=workout, user=request.user
    ).first()

    if existing:
        existing.delete()
        messages.info(request, 'Presença cancelada.')
    else:
        if workout.is_full:
            messages.error(request, 'Esse treino já está com vagas esgotadas.')
            return redirect('workout-detail', pk=pk)
        if workout.is_past:
            messages.error(request, 'Não é possível marcar presença em um treino que já passou.')
            return redirect('workout-detail', pk=pk)

        WorkoutParticipant.objects.create(
            workout=workout,
            user=request.user,
            status=WorkoutParticipant.Status.CONFIRMED,
        )
        messages.success(request, 'Presença confirmada!')

    return redirect('workout-detail', pk=pk)
