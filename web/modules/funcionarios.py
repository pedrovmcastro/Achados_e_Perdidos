# Finalizado
from bson.codec_options import CodecOptions
from bson.objectid import ObjectId
from datetime import datetime, timezone
from decorators import login_required, session_expired, admin_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from hashlib import sha256
import pymongo
import secret

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
funcionarios_collections = db['funcionarios']

funcionario = Blueprint('funcionario', __name__)


@funcionario.route('/admin/funcionario')
@login_required
@session_expired
def funcionario_index():
    sessao = {
        'id': session.get('funcionario_id', ''),
        'nome': session.get('nome', ''),
        'administrador': session.get('administrador', ''),
    }

    funcionarios = []
    desligados = []
    for f in funcionarios_collections.find():
        funcionario = {
            'id': str(f['_id']),
            'nome': f['nome'],
            'matricula': f['matricula'],
            'ligado': f['ligado'],
            'desligado': f.get('desligado'),
        }

        if funcionario['desligado'] is not None:
            desligados.append(funcionario)
        else:
            funcionarios.append(funcionario)

    return render_template('funcionario.html',
                           funcionarios=funcionarios,
                           desligados=desligados,
                           sessao=sessao
                           )


@funcionario.route('/admin/funcionario/add', methods=['POST'])
@login_required
@session_expired
@admin_required
def funcionario_add():
    nome = request.form.get('nome')
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')
    administrador = request.form.get('administrador')
    rua = request.form.get('rua')
    cep = request.form.get('cep')

    if not matricula.isdigit():
        flash('Matricula tem que ser um número!', 'danger')
        return redirect(url_for('.funcionario_index'))

    funcionario = funcionarios_collections.find_one({
        'matricula': matricula,
    })

    if funcionario:
        flash('Matricula tem que ser única!', 'danger')
        return redirect(url_for('.funcionario_index'))

    if len(cep) < 9:
        flash('Formato do CEP inválido!', 'danger')
        return redirect(url_for('.funcionario_index'))

    if not all([nome, senha, rua]):
        vazios = []
        if not nome:
            vazios.append('Nome')
        if not senha:
            vazios.append('Senha')
        if not rua:
            vazios.append('Rua')

        plural = 's' if len(vazios) > 1 else ''
        flash(f'Campo{plural} não preenchido{plural}:  {", ".join(vazios)}!', 'danger')
        return redirect(url_for('.funcionario_index'))

    new_data = {
        'nome': nome,
        'matricula': matricula,
        'administrador': administrador is not None,
        'endereco': {
            'rua': rua,
            'cep': cep,
        },
        'ligado': datetime.now(timezone.utc),
        'senha': sha256(senha.encode('utf-8')).hexdigest(),
    }

    try:
        result = funcionarios_collections.insert_one(new_data)

        if result.inserted_id:
            flash('Funcionário adicionada com sucesso!', 'success')
        else:
            flash('Erro ao adicionar funcionário.', 'danger')
    except Exception:
        flash('Erro crítico ao adicionar a funcionário!', 'danger')

    return redirect(url_for('.funcionario_index'))


@funcionario.route('/admin/funcionario/edit/<string:funcionario_id>')
@login_required
@session_expired
def funcionario_edit(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash('Não pode editar o Admin!', 'danger')
        return redirect(url_for('.funcionario_index'))

    funcionario = funcionarios_collections.find_one({'_id': ObjectId(funcionario_id)})

    sessao = {
        'id': session.get('funcionario_id', ''),
        'nome': session.get('nome', ''),
        'administrador': session.get('administrador', ''),
    }

    return render_template('funcionario_editar.html',
                           funcionario=funcionario,
                           sessao=sessao
                           )


@funcionario.route('/admin/funcionario/edit/<string:funcionario_id>/form', methods=['POST'])
@login_required
@session_expired
def funcionario_edit_action(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash('Não pode editar o Admin!', 'danger')
        return redirect(url_for('.funcionario_index'))

    nome = request.form.get('nome')
    matricula = request.form.get('matricula')
    senha = request.form.get('senha')
    administrador = request.form.get('administrador')
    rua = request.form.get('rua')
    cep = request.form.get('cep')

    if 1 <= len(cep) < 9:
        flash('Formato do CEP inválido!', 'danger')
        return redirect(url_for('.funcionario_edit', funcionario_id=funcionario_id))

    if not all([nome, matricula, senha, rua]):
        vazios = []
        if not nome:
            vazios.append('Nome')
        if not matricula:
            vazios.append('Matrícula')
        if not senha:
            vazios.append('Senha')
        if not rua:
            vazios.append('Rua')

        plural = 's' if len(vazios) > 1 else ''
        flash(f'Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!', 'danger')
        return redirect(url_for('.funcionario_edit', funcionario_id=funcionario_id))

    cep = cep.replace('-', '') if cep else None
    update_data = {
        'nome': nome,
        'matricula': matricula,
        'administrador': administrador is not None,
        'endereco': {
            'rua': rua,
            'cep': cep,
        },
    }

    if senha:
        update_data['senha'] = sha256(senha.encode('utf-8')).hexdigest()

    try:
        result = funcionarios_collections.update_one(
            {'_id': ObjectId(funcionario_id)},
            {'$set': update_data}
        )

        if result.modified_count == 1:
            flash('Funcionário atualizado com sucesso!', 'success')
        else:
            flash('Nenhuma alteração foi detectada.', 'warning')
    except Exception:
        flash('Erro crítico na atualização do funcionário!', 'danger')

    return redirect(url_for('.funcionario_index'))


@funcionario.route('/admin/funcionario/<string:funcionario_id>/desligar')
@login_required
@session_expired
@admin_required
def funcionario_desligar(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash('Não pode editar o Admin!', 'danger')
        return redirect(url_for('.funcionario_index'))

    funcionarios_collections.update_one(
        {'_id': ObjectId(funcionario_id)},
        {
                '$set': {
                    'desligado': datetime.now(timezone.utc),
                }
            }
        )

    return redirect(url_for('.funcionario_index'))


@funcionario.route('/admin/funcionario/<string:funcionario_id>/religar')
@login_required
@session_expired
@admin_required
def funcionario_religar(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash('Não pode editar o Admin!', 'danger')
        return redirect(url_for('.funcionario_index'))

    funcionarios_collections.update_one(
        {'_id': ObjectId(funcionario_id)},
        {
                '$set': {
                    'desligado': None,
                    'ligado': datetime.now(timezone.utc),
                }
        }
    )

    return redirect(url_for('.funcionario_index'))
