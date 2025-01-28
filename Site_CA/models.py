from Site_CA import database, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def get_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), nullable=False)
    email = database.Column(database.String(120), nullable=False, unique=True)
    senha = database.Column(database.String(60), nullable=False)
    foto_perfil = database.Column(database.String, nullable=False, default= "default.jpg")
    post = database.relationship('Post', backref='autor', lazy=True)
    cursos = database.Column(database.String, nullable=False, default='Não informado')

    def contar_posts(self):
        return len(self.post)


class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String(30), nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    data_criacao = database.Column(database.DateTime, nullable=False, default= datetime.utcnow)         # default=lambda: datetime.now(datetime.timezone.utc) default=datetime.utcnow
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)