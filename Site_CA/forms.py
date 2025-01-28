from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, equal_to, ValidationError
from email_validator import validate_email, EmailNotValidError
from Site_CA.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome do Usuário', validators=[DataRequired(), Length(min=5, max=30)])
    email = StringField('Email', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), equal_to('senha')])
    botao_criar_conta = SubmitField('Criar Conta')

    def validate_email(self, field):    # Traduzir o erro (anteriormente na class - email = StringField('Email', validators=[DataRequired(), Email()]))
        try:
            validate_email(field.data)
        except EmailNotValidError:
            raise ValidationError('E-mail inválido')
        
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario:
            raise ValidationError('Este e-mail já está em uso. Por favor, utilize um e-mail diferente ou acesse sua conta existente.')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=20)])
    lembrar = BooleanField('Lembrar de mim')
    botao_login = SubmitField('Entrar')

    def validate_email(self, field):
        try:
            validate_email(field.data)
        except EmailNotValidError:
            raise ValidationError('E-mail inválido')
        

class FormEditarPerfil(FlaskForm):
    username = StringField('Nome do Usuário', validators=[DataRequired(), Length(min=5, max=30)])
    email = StringField('Email', validators=[DataRequired()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])

    curso_excel = BooleanField('Excel Impressionador')
    curso_python = BooleanField('Python Impressionador')
    curso_vba = BooleanField('VBA Impressionador')
    curso_powerbi = BooleanField('Power BI Impressionador')
    curso_ppt = BooleanField('PowerPoint Impressionador')
    curso_sql = BooleanField('SQL Impressionador')

    botao_atualizar_perfil = SubmitField('Salvar')

    def validate_email(self, field):
        if field.data != current_user.email:
            usuario = Usuario.query.filter_by(email=field.data).first()
            if usuario:
                raise ValidationError('Este e-mail já está em uso. Por favor, utilize um e-mail diferente.')
            

class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(min=5, max=50)])
    corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired(), Length(min=10, max=3000)])
    botao_criar_post = SubmitField('Criar Post')
    botao_editar_post = SubmitField('Postar')