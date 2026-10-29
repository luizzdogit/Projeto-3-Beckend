from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from .models import Tarefa


class TarefaAPITests(APITestCase):
    client_class = APIClient

    def setUp(self):
        user_model = get_user_model()
        self.ana = user_model.objects.create_user(
            username='ana',
            password='senha-de-teste-ana',
        )
        self.beto = user_model.objects.create_user(
            username='beto',
            password='senha-de-teste-beto',
        )
        self.ana_token = Token.objects.create(user=self.ana)
        self.beto_token = Token.objects.create(user=self.beto)
        self.lista_url = reverse('tarefa-lista')

    def autenticar(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def criar_tarefa(self, usuario, **kwargs):
        dados = {
            'titulo': 'Tarefa de teste',
            'usuario': usuario,
        }
        dados.update(kwargs)
        return Tarefa.objects.create(**dados)

    def test_login_devolve_token(self):
        response = self.client.post(
            reverse('api-login'),
            {'username': 'ana', 'password': 'senha-de-teste-ana'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.ana_token.key)

    def test_sem_token_401(self):
        response = self.client.get(self.lista_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lista_so_do_proprio_usuario(self):
        tarefa_ana = self.criar_tarefa(self.ana, titulo='Tarefa da Ana')
        self.criar_tarefa(self.beto, titulo='Tarefa do Beto')
        self.autenticar(self.ana_token)

        response = self.client.get(self.lista_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item['id'] for item in response.data], [tarefa_ana.id])

    def test_filtros(self):
        tarefa_alta_concluida = self.criar_tarefa(
            self.ana,
            titulo='Urgente concluída',
            prioridade='ALTA',
            concluida=True,
        )
        self.criar_tarefa(
            self.ana,
            titulo='Baixa pendente',
            prioridade='BAIXA',
            concluida=False,
        )
        self.autenticar(self.ana_token)

        response = self.client.get(
            self.lista_url,
            {'prioridade': 'alta', 'concluida': 'true'},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item['id'] for item in response.data],
            [tarefa_alta_concluida.id],
        )

    def test_criar_define_dono_pelo_token(self):
        self.autenticar(self.ana_token)

        response = self.client.post(
            self.lista_url,
            {
                'titulo': 'Nova tarefa',
                'prioridade': 'MEDIA',
                'usuario': self.beto.id,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tarefa = Tarefa.objects.get(pk=response.data['id'])
        self.assertEqual(tarefa.usuario, self.ana)

    def test_patch_altera_so_um_campo(self):
        tarefa = self.criar_tarefa(
            self.ana,
            titulo='Título original',
            descricao='Descrição original',
            concluida=False,
        )
        self.autenticar(self.ana_token)

        response = self.client.patch(
            reverse('tarefa-detalhe', args=[tarefa.id]),
            {'concluida': True},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tarefa.refresh_from_db()
        self.assertTrue(tarefa.concluida)
        self.assertEqual(tarefa.titulo, 'Título original')
        self.assertEqual(tarefa.descricao, 'Descrição original')

    def test_isolamento_404_em_detalhe_de_outro(self):
        tarefa = self.criar_tarefa(self.ana, titulo='Privada da Ana')
        detalhe_url = reverse('tarefa-detalhe', args=[tarefa.id])
        self.autenticar(self.beto_token)

        get_response = self.client.get(detalhe_url)
        patch_response = self.client.patch(
            detalhe_url,
            {'titulo': 'Tentativa de alteração'},
            format='json',
        )
        delete_response = self.client.delete(detalhe_url)

        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(patch_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tarefa.objects.filter(pk=tarefa.id).exists())

    def test_delete_proprio(self):
        tarefa = self.criar_tarefa(self.ana)
        self.autenticar(self.ana_token)

        response = self.client.delete(
            reverse('tarefa-detalhe', args=[tarefa.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tarefa.objects.filter(pk=tarefa.id).exists())
