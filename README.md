# API de Tarefas Pessoais

API REST de tarefas pessoais desenvolvida como Projeto 3 da disciplina
Construção de Backend, no IESB.

**Autor:** não informado no workspace.

## Tecnologias

- Python
- Django
- Django REST Framework
- Django REST Framework Token Authentication
- SQLite para desenvolvimento local

## Estrutura

```text
todoapi/
├── manage.py
├── requirements.txt
├── tarefas/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── todoapi/
│   ├── settings.py
│   └── urls.py
└── venv/  (ambiente virtual local; não versionado)
```

## Instalação e execução

No PowerShell, na pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

O PowerShell pode bloquear a ativação do ambiente virtual conforme a política
local de execução. Nesse caso, use diretamente `.\venv\Scripts\python.exe` e
`.\venv\Scripts\pip.exe` nos comandos abaixo.

### Chave secreta

Não há chave secreta fixa no código. A aplicação lê `DJANGO_SECRET_KEY` do
ambiente ou, para desenvolvimento local, o arquivo `.secret_key`, ignorado pelo
Git. Crie o arquivo local somente se ainda não existir:

```powershell
if (-not (Test-Path .secret_key)) {
    python -c "import secrets; from pathlib import Path; Path('.secret_key').write_text(secrets.token_urlsafe(50), encoding='utf-8')"
}
```

Em ambientes publicados, configure `DJANGO_SECRET_KEY` como variável de
ambiente e não publique a chave. O modo `DEBUG` atual destina-se somente ao
desenvolvimento.

### Banco, administrador e servidor

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O painel administrativo fica em <http://127.0.0.1:8000/admin/>.

## Endpoints

| Método | Caminho | Finalidade |
|---|---|---|
| POST | `/api/login/` | Obter um token usando usuário e senha |
| GET, POST | `/api/tarefas/` | Listar ou criar tarefas do usuário autenticado |
| GET, PUT, PATCH, DELETE | `/api/tarefas/<id>/` | Consultar, editar ou excluir uma tarefa própria |

As rotas de tarefas exigem autenticação por token. Envie o cabeçalho:

```text
Authorization: Token <TOKEN>
```

### Login por token

Exemplo fictício de requisição:

```http
POST /api/login/ HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{"username": "<usuario>", "password": "<senha>"}
```

Resposta ilustrativa; o token abaixo não é válido:

```json
{"token": "token-ficticio-nao-utilizavel"}
```

### Filtros

A listagem aceita os parâmetros opcionais `prioridade` (`baixa`, `media` ou
`alta`) e `concluida` (`true` ou `false`). Exemplo:

```text
GET /api/tarefas/?prioridade=alta&concluida=true
```

### Exemplo de criação

Requisição fictícia:

```http
POST /api/tarefas/ HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Token <TOKEN>
Content-Type: application/json

{"titulo": "Estudar para a prova", "descricao": "", "prioridade": "ALTA"}
```

Resposta ilustrativa:

```json
{
  "id": 1,
  "titulo": "Estudar para a prova",
  "descricao": "",
  "concluida": false,
  "prioridade": "ALTA",
  "data_criacao": "2026-01-15T12:00:00Z",
  "data_limite": null,
  "usuario": 1
}
```

Os valores de exemplo são fictícios. O usuário responsável é definido pela API
a partir do token, não pelo corpo enviado pelo cliente.

## Isolamento entre usuários

Cada operação de tarefas exige autenticação. A consulta e a listagem filtram
pelas tarefas pertencentes ao usuário autenticado; tentar acessar a tarefa de
outra pessoa retorna `404`. Ao criar, o servidor associa a tarefa ao usuário do
token.

## Testes

Execute:

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Resultado verificado na preparação desta entrega: **8 testes executados, OK**.
