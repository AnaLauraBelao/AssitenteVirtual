import os
from datetime import datetime, timedelta
from pony.orm import *
from src.enum.status_tarefa import StatusAtividade

db = Database()
db.bind(provider="sqlite", filename=os.path.join(os.path.dirname(__file__), 'db.db'))


class Projetos(db.Entity):
    id = PrimaryKey(int, auto=True)
    id_tmetric = Required(int, unique=True)
    nome = Required(str)
    atividades = Set("Atividades")


class Atividades(db.Entity):
    id = PrimaryKey(int, auto=True)
    id_tmetric = Required(int)
    id_teamwork = Required(int)
    id_projeto_tmetric = Required(int)
    nome_tarefa = Required(str)
    data = Required(datetime)
    status = Required(str, default=StatusAtividade.EM_ANDAMENTO.value)
    projeto = Required(Projetos, reverse="atividades", lazy=True)


class Agendamentos(db.Entity):
    id = PrimaryKey(int, auto=True)
    comando = Required(str)
    cron = Required(str)


class Subscriptions(db.Entity):
    id = PrimaryKey(int, auto=True)
    subscription = Required(str, unique=True)
    description = Optional(str)
    resource_groups = Set("ResourceGroups")


class ResourceGroups(db.Entity):
    id = PrimaryKey(int, auto=True)
    subscription = Required(Subscriptions, reverse="resource_groups", lazy=True)
    resource_group = Required(str, unique=True)
    description = Optional(str)
    servers = Set("Servers")


class Servers(db.Entity):
    id = PrimaryKey(int, auto=True)
    resource_group = Required(ResourceGroups, reverse="servers", lazy=True)
    server_name = Required(str, unique=True)
    description = Optional(str)
    rules = Set("Rules")


class Channels(db.Entity):
    id = PrimaryKey(int, auto=True)
    channel = Required(str, unique=True)
    description = Optional(str)
    rules = Set("Rules")


class Rules(db.Entity):
    id = PrimaryKey(int, auto=True)
    channel = Required(Channels, reverse="rules", lazy=True)
    server = Required(Servers, reverse="rules", lazy=True)
    name = Required(str, unique=True)
    type = Required(str)
    env = Optional(str)
    description = Optional(str)

class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    discord_id = Required(str, unique=True)
    teamwork_user_id = Required(int, unique=True)
    email = Required(str, unique=True)
    name = Required(str)
    planning_name = Required(str)


db.generate_mapping(create_tables=True)
