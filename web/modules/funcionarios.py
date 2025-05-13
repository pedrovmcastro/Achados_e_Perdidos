from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from decorators import login_required, admin_required
import secret
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
funcionarios_collections = db['funcionarios']
funcionario = Blueprint("funcionario", __name__)


@funcionario.route("/admin/funcionario")
@login_required
def funcionario_index():
    funcionarios = []
    for f in funcionarios_collections.find():
        funcionarios.append({
            "id": str(f['_id']),
            "nome": f['nome'],
            "matricula": f['matricula'],
            "ligado": f['ligado'],
            "desligado": f.get('desligado'),
        })
    sessao = {
        "id": session["funcionario_id"],
        "nome": session["nome"],
        "administrador": session["administrador"],
    }

    return render_template("funcionario.html",
                           funcionarios=funcionarios,
                           sessao=sessao
                           )


@funcionario.route("/admin/funcionario/add", methods=["POST"])
@login_required
def funcionario_add():
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")
    administrador = request.form.get("administrador")
    rua = request.form.get("rua")
    cep = request.form.get("cep")

    if nome and matricula and senha and rua and cep:
        funcionarios_collections.insert_one({
            "nome": nome,
            "matricula": matricula,
            "administrador": administrador is not None,
            "endereco": {
                "rua": rua,
                "cep": cep,
            },
            "ligado": datetime.now(timezone.utc),
        })
        flash("Cadastrado com sucesso!", "success")
    else:
        flash("Alguma coisa deu errado!", "danger")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/edit/<string:funcionario_id>")
@login_required
def funcionario_edit(funcionario_id):
    sessao = {
        "id": session["funcionario_id"],
        "nome": session["nome"],
        "administrador": session["administrador"],
    }


    return render_template("funcionario_editar.html",
                           funcionario=funcionarios_collections.find_one({"_id": ObjectId(funcionario_id)}),
                           sessao=sessao
                           )


@funcionario.route("/admin/funcionario/edit/<string:funcionario_id>/form", methods=["POST"])
@login_required
def funcionario_edit_action(funcionario_id):
    
    # Coletar dados do formulário
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")
    administrador = request.form.get("administrador")
    rua = request.form.get("rua")
    cep = request.form.get("cep")

    # Validação server-side
    if not all([nome, matricula, rua, cep]):
        flash("Todos os campos obrigatórios devem ser preenchidos!", "danger")
        return redirect(url_for(".funcionario_edit", funcionario_id=funcionario_id))

    # Preparar dados para atualização
    update_data = {
        "nome": nome,
        "matricula": matricula,
        "administrador": administrador is not None,
        "endereco": {
            "rua": rua,
            "cep": cep
        }
    }

    # Atualizar senha apenas se for fornecida
    if senha:
        update_data["senha"] = senha

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
        print(f"Erro na atualização: {e}")
        flash("Erro crítico na atualização do funcionário!", "danger")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/<string:funcionario_id>/desligar")
@login_required
def funcionario_desligar(funcionario_id):
    funcionarios_collections.update_one(
        {"_id": ObjectId(funcionario_id)},
        {
                "$set": {
                    "desligado": datetime.now(timezone.utc),
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
