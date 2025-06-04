from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from decorators import login_required, admin_required, session_expired
import secret
import pymongo
import hashlib
from datetime import datetime, timezone

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
funcionarios_collections = db['funcionarios']
funcionario = Blueprint("funcionario", __name__)


@funcionario.route("/admin/funcionario")
@login_required
@session_expired
def funcionario_index():
    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }

    funcionarios = []
    desligados = []
    for f in funcionarios_collections.find():
        funcionario = {
            "id": str(f['_id']),
            "nome": f['nome'],
            "matricula": f['matricula'],
            "ligado": f['ligado'],
            "desligado": f.get('desligado'),
        }

        if funcionario["desligado"] is not None:
            desligados.append(funcionario)
        else:
            funcionarios.append(funcionario)

    return render_template("funcionario.html",
                           funcionarios=funcionarios,
                           desligados=desligados,
                           sessao=sessao
                           )


@funcionario.route("/admin/funcionario/add", methods=["POST"])
@login_required
@session_expired
@admin_required
def funcionario_add():
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")
    administrador = request.form.get("administrador")
    rua = request.form.get("rua")
    cep = request.form.get("cep")

    if nome and matricula and senha and rua and cep:
        funcionario = funcionarios_collections.find_one({
            "matricula": matricula,
        })

        if funcionario:
            flash("Matricula tem que ser única!", "danger")
            return redirect(url_for(".funcionario_index"))

        funcionarios_collections.insert_one({
            "nome": nome,
            "matricula": matricula,
            "administrador": administrador is not None,
            "endereco": {
                "rua": rua,
                "cep": cep,
            },
            "ligado": datetime.now(timezone.utc),
            "senha": hashlib.sha256(senha.encode('utf-8')).hexdigest(),
        })
        flash("Cadastrado com sucesso!", "success")
    else:
        vazios = []
        if not nome:
            vazios.append("nome")
        if not matricula:
            vazios.append("campos")
        if not senha:
            vazios.append("senha")
        if not rua:
            vazios.append("rua")
        if not cep:
            vazios.append("cep")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/edit/<string:funcionario_id>")
@login_required
@session_expired
def funcionario_edit(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash("Não pode editar o Admin!", "danger")
        return redirect(url_for(".funcionario_index"))

    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }

    return render_template("funcionario_editar.html",
                           funcionario=funcionarios_collections.find_one({"_id": ObjectId(funcionario_id)}),
                           sessao=sessao
                           )


@funcionario.route("/admin/funcionario/edit/<string:funcionario_id>/form", methods=["POST"])
@login_required
@session_expired
def funcionario_edit_action(funcionario_id):
    # Coletar dados do formulário
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")
    administrador = request.form.get("administrador")
    rua = request.form.get("rua")
    cep = request.form.get("cep")

    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash("Não pode editar o Admin!", "danger")
        return redirect(url_for(".funcionario_index"))

    # Validação server-side
    if not all([nome, matricula, rua, cep]):
        vazios = []
        if not nome:
            vazios.append("nome")
        if not matricula:
            vazios.append("campos")
        if not senha:
            vazios.append("senha")
        if not rua:
            vazios.append("rua")
        if not cep:
            vazios.append("cep")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")
        return redirect(url_for(".funcionario_edit", funcionario_id=funcionario_id))

    # Preparar dados para atualização
    update_data = {
        "nome": nome,
        "matricula": matricula,
        "administrador": administrador is not None,
        "endereco": {
            "rua": rua,
            "cep": cep
        },
    }

    # Atualizar senha apenas se for fornecida
    if senha:
        update_data["senha"] = hashlib.sha256(senha.encode('utf-8')).hexdigest()

    try:
        # Atualização única no banco de dados
        result = funcionarios_collections.update_one(
            {"_id": ObjectId(funcionario_id)},
            {"$set": update_data}
        )

        if result.modified_count == 1:
            flash("Funcionário atualizado com sucesso!", "success")
        else:
            flash("Nenhuma alteração foi detectada.", "warning")

    except Exception as e:
        flash("Erro crítico na atualização do funcionário!", "danger")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/<string:funcionario_id>/desligar")
@login_required
@session_expired
def funcionario_desligar(funcionario_id):
    if funcionario_id == '682e4ad7c6002bc2c0163de8':
        flash("Não pode editar o Admin!", "danger")
        return redirect(url_for(".funcionario_index"))

    funcionarios_collections.update_one(
        {"_id": ObjectId(funcionario_id)},
        {
                "$set": {
                    "desligado": datetime.now(timezone.utc),
                }
            }
        )
    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/<string:funcionario_id>/religar")
@login_required
@session_expired
def funcionario_religar(funcionario_id):

    funcionarios_collections.update_one(
        {"_id": ObjectId(funcionario_id)},
        {
                "$set": {
                    "desligado": None,
                    "ligado": datetime.now(timezone.utc),
                }
        }
    )
    return redirect(url_for(".funcionario_index"))


""" QUANDO QUISER TROCAR O DESLIGAR POR DELETAR
@funcionario.route("/admin/funcionario/<string:funcionario_id>/desligar")
def funcionario_desligar(funcionario_id):
    funcionarios_collections.delete_one({"_id": ObjectId(funcionario_id)})
    return redirect(url_for(".funcionario_index"))
"""
