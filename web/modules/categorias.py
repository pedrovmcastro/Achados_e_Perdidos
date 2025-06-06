from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from decorators import login_required, admin_required, session_expired
import secret
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
categoria_collections = db['categorias']
categoria = Blueprint("categoria", __name__)


def get_nomes_categorias():
    return [cat['nome'] for cat in categoria_collections.find()]


@categoria.route("/admin/categoria")
@login_required
@session_expired
def categoria_index():
    categorias = []
    for c in categoria_collections.find():
        categorias.append({
            "id": str(c['_id']),
            "nome": c['nome'],
        })
    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }

    return render_template("categoria.html",
                           categorias=categorias,
                           sessao=sessao
                           )


@categoria.route("/admin/categoria/add", methods=["POST"])
@login_required
@session_expired
def categoria_add():
    nome = request.form.get("nome")
    campos = request.form.getlist('campos[]')

    if nome and campos:
        categoria_collections.insert_one({
            "nome": nome,
            "campos": campos,
        })
        flash("Cadastrado com sucesso!", "success")
    else:
        vazios = []
        if not nome:
            vazios.append("nome")
        if not campos:
            vazios.append("campos")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")

    return redirect(url_for(".categoria_index"))


@categoria.route("/admin/categoria/edit/<string:categoria_id>")
@login_required
@session_expired
def categoria_edit(categoria_id):
    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }

    return render_template("categoria_editar.html",
                           categoria=categoria_collections.find_one({"_id": ObjectId(categoria_id)}),
                           sessao=sessao,
                           )


@categoria.route("/admin/categoria/edit/<string:categoria_id>/form", methods=["POST"])
@login_required
@session_expired
def categoria_edit_action(categoria_id):

    # Coletar dados do formulário
    nome = request.form.get("nome")
    campos = request.form.getlist('campos[]')

    campos = [c.strip() for c in campos if c.strip()]
    campos = list(dict.fromkeys(campos))

    # Validação server-side
    if not nome or not campos:
        vazios = []
        if not nome:
            vazios.append("nome")
        if not campos:
            vazios.append("campos")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")
        return redirect(url_for(".categoria_edit", categoria_id=categoria_id))

    # Preparar dados para atualização
    update_data = {
        "nome": nome,
        "campos": campos,
    }

    try:
        # Atualização única no banco de dados
        result = categoria_collections.update_one(
            {"_id": ObjectId(categoria_id)},
            {"$set": update_data}
        )

        if result.modified_count == 1:
            flash("Categoria atualizada com sucesso!", "success")
        else:
            flash("Nenhuma alteração foi detectada.", "warning")

    except Exception as e:
        print(f"Erro na atualização: {e}")
        flash("Erro crítico na atualização da categoria!", "danger")

    return redirect(url_for(".categoria_index"))


'''
@categoria.route("/admin/categoria/delete/<string:categoria_id>")
@login_required
def categoria_delete(categoria_id):
    categoria_collections.delete_one({"_id": ObjectId(categoria_id)})
    return redirect(url_for(".categoria_index"))
'''


@categoria.route("/api/categoria/<id>")
@login_required
@session_expired
def get_categoria(id):
    categoria = categoria_collections.find_one({"_id": ObjectId(id)})
    if not categoria:
        flash("Categoria não encontrada", "danger")
    return jsonify({
        "_id": str(categoria["_id"]),
        "nome": categoria["nome"],
        "campos": categoria["campos"]
    })
