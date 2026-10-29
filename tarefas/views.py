from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Tarefa
from .serializers import TarefaSerializer


class TarefaListCreateView(generics.ListCreateAPIView):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Tarefa.objects.filter(usuario=self.request.user)

        concluida = self.request.query_params.get('concluida')
        if concluida is not None:
            valor = concluida.lower()
            if valor not in ('true', 'false'):
                raise ValidationError(
                    {'concluida': 'Use true ou false.'}
                )
            queryset = queryset.filter(concluida=(valor == 'true'))

        prioridade = self.request.query_params.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade.upper())

        return queryset

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class TarefaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TarefaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tarefa.objects.filter(usuario=self.request.user)