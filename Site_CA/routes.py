from flask import render_template, request, redirect, url_for, flash, abort
from Site_CA import app, database, bcrypt
from Site_CA.forms import FormCriarConta, FormLogin, FormEditarPerfil, FormCriarPost
from Site_CA.models import Usuario, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets
import os
from PIL import Image


@app.route('/')
def home():
    posts= Post.query.order_by(Post.id.desc()).all()
    return render_template('home.html', posts=posts)


@app.route('/contato')
def contato():
    return render_template('contato.html')


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_criarconta = FormCriarConta()
    form_login = FormLogin()

    if form_criarconta.validate_on_submit() and 'botao_criar_conta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()

        flash(f'Conta criada com sucesso para o e-mail {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    
    if form_login.validate_on_submit() and 'botao_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar.data)
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            parametro_next = request.args.get('next')
            if parametro_next:
                return redirect(parametro_next)
            else:
                return redirect(url_for('home'))
        else:
            flash('Falha no login. Por favor, verifique seu e-mail e senha.', 'alert-danger')

    return render_template('login.html', form_criarconta=form_criarconta, form_login=form_login)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Você saiu da sua conta.', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}') if current_user.foto_perfil else None
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form_criar_post = FormCriarPost()
    if form_criar_post.validate_on_submit():
        post = Post(titulo=form_criar_post.titulo.data, corpo=form_criar_post.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso.', 'alert-success')
        return redirect(url_for('home'))

    return render_template('criar_post.html', form_criar_post=form_criar_post)


def salvar_foto(foto):
    codigo = secrets.token_hex(8)
    _, extensao = os.path.splitext(foto.filename)
    nome_foto = codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_foto)
    compr = (180, 180)
    foto_compr = Image.open(foto)
    foto_compr.thumbnail(compr)
    foto_compr.save(caminho_completo)
    return nome_foto


def update_cursos(form_edit):
    lista_cursos = []
    for campo in form_edit:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return '; '.join(lista_cursos)


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form_edit = FormEditarPerfil()
    if form_edit.validate_on_submit():
        current_user.username = form_edit.username.data
        current_user.email = form_edit.email.data
        if form_edit.foto_perfil.data:
            nome_foto = salvar_foto(form_edit.foto_perfil.data)
            current_user.foto_perfil = nome_foto
        current_user.cursos = update_cursos(form_edit)
        database.session.commit()
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form_edit.username.data = current_user.username
        form_edit.email.data = current_user.email
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}') if current_user.foto_perfil else None
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form_edit=form_edit)


@app.route('/post/<int:id_post>', methods=['GET', 'POST'])
@login_required
def exibir_post(id_post):
    post = Post.query.get_or_404(id_post)
    if current_user.is_authenticated:
        if current_user == post.autor:
            form = FormCriarPost()
            if request.method == 'GET':
                form.titulo.data = post.titulo
                form.corpo.data = post.corpo
            elif form.validate_on_submit():
                post.titulo = form.titulo.data
                post.corpo = form.corpo.data
                database.session.commit()
                flash('Post atualizado com sucesso.', 'alert-success')
                return redirect(url_for('home'))
        else:
            form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<int:id_post>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(id_post):
    post = Post.query.get_or_404(id_post)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso.', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)
        return redirect(url_for('home'))