from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
import secret
import time
import pymongo

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos']
funcionarios_collections = db['funcionarios']
funcionario = Blueprint("funcionario", __name__)


@funcionario.route("/admin/funcionario")
def funcionario_index():
    funcionarios = []
    for f in funcionarios_collections.find():
        funcionarios.append({
            "id": str(f['_id']),
            "nome": f['nome'],
            "matricula": f['matricula'],
        })

    return render_template("funcionario.html",
                           funcionarios=funcionarios)


@funcionario.route("/admin/funcionario/add", methods=["POST"])
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
            "senha": senha,
            "administrador": administrador is not None,
            "endereco": {
                "rua": rua,
                "cep": cep,
            },
            "ligado": int(time.time()),
        })
        flash("Cadastrado com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/edit/<string:funcionario_id>")
def funcionario_edit(funcionario_id):
    return render_template("funcionario_editar.html",
                           funcionario=funcionarios_collections.find_one({"_id": ObjectId(funcionario_id)}))


@funcionario.route("/admin/<string:funcionario_id>/edit", methods=["POST"])
def funcionario_edit_action(funcionario_id):
    nome = request.form.get("nome")
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")
    administrador = request.form.get("administrador")
    rua = request.form.get("rua")
    cep = request.form.get("cep")

    if nome and matricula and senha and rua and cep:
        funcionarios_collections.update_one(
            {"_id": ObjectId(funcionario_id)},
            {
                "$set": {
                    "nome": nome,
                    "matricula": matricula,
                    "senha": senha,
                    "administrador": administrador is not None,
                    "endereco": {
                        "rua": rua,
                        "cep": cep,
                    },
                }
            }
        )
        flash("Funcionário atualizado com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".funcionario_index"))


@funcionario.route("/admin/funcionario/desligar/<string:funcionario_id>")
def funcionario_desligar(funcionario_id):
    funcionarios_collections.delete_one({"_id": ObjectId(funcionario_id)})
    return redirect(url_for(".funcionario_index"))