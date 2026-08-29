from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile

User = get_user_model()


class SignupTests(TestCase):
    def test_signup_cria_usuario_e_profile(self):
        response = self.client.post(reverse('signup'), {
            'username': 'novousuario',
            'email': 'novo@example.com',
            'password': 'senhaSegura123',
            'password2': 'senhaSegura123',
        })
        self.assertTrue(User.objects.filter(username='novousuario').exists())
        self.assertTrue(Profile.objects.filter(user__username='novousuario').exists())
        self.assertRedirects(response, reverse('settings'))

    def test_signup_falha_com_senhas_diferentes(self):
        response = self.client.post(reverse('signup'), {
            'username': 'outrousuario',
            'email': 'outro@example.com',
            'password': 'senha123',
            'password2': 'senhaDiferente',
        })
        self.assertFalse(User.objects.filter(username='outrousuario').exists())
        self.assertRedirects(response, reverse('signup'))


class SettingsViewTests(TestCase):
    """
    Cobre o bug que corrigimos: salvar as configuracoes sem enviar uma nova
    foto de perfil nao deve mais gerar NameError.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='usuarioteste', password='senha123', email='antigo@example.com'
        )
        self.profile = Profile.objects.create(user=self.user, id_user=self.user.id)
        self.client.login(username='usuarioteste', password='senha123')

    def test_salvar_settings_sem_trocar_foto_nao_quebra(self):
        response = self.client.post(reverse('settings'), {
            'bio': 'Minha nova bio',
            'location': 'Maceio, AL',
            'email': 'novo@example.com',
        })
        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Minha nova bio')
        self.assertEqual(self.profile.location, 'Maceio, AL')
        self.assertEqual(self.user.email, 'novo@example.com')
