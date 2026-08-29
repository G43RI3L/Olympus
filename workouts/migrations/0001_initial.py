from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('workout_type', models.CharField(
                    choices=[
                        ('RUNNING', 'Corrida'),
                        ('GYM', 'Academia'),
                        ('SWIMMING', 'Natação'),
                        ('CYCLING', 'Ciclismo'),
                        ('SPORTS', 'Esporte coletivo'),
                        ('OTHER', 'Outro'),
                    ],
                    default='OTHER',
                    max_length=20,
                )),
                ('location', models.CharField(max_length=200)),
                ('scheduled_for', models.DateTimeField(help_text='Data e hora em que o treino vai acontecer.')),
                ('max_participants', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='created_workouts',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['scheduled_for'],
            },
        ),
        migrations.CreateModel(
            name='WorkoutParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pendente'),
                        ('CONFIRMED', 'Confirmado'),
                        ('DECLINED', 'Recusado'),
                    ],
                    default='CONFIRMED',
                    max_length=10,
                )),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='workout_participations',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('workout', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='participants',
                    to='workouts.workout',
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name='workoutparticipant',
            constraint=models.UniqueConstraint(
                fields=('workout', 'user'), name='unique_participant_per_workout'
            ),
        ),
    ]
