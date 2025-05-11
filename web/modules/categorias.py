from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
import secret
import .decorators
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
categoria_collections = db['categorias']
categoria = Blueprint("categoria", __name__)

@categoria.route("/admin/categoria")
def categoria_index():
    categorias = []
    for c in categoria_collections.find():
        categorias.append({
            "id": str(c['_id']),
            "nome": c['nome'],
        })

    return render_template("categoria.html",
                           categorias=categorias)

@categoria.route("/admin/categoria/add", methods=["POST"])
def categoria_add():
    nome = request.form.get("nome")

    campos = request.form.getlist('campos[]')

    if nome and campos:
        categoria_collections.insert_one({
            "nome": nome,
            "campos": campos,
        })
        flash("Cadastrada com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".categoria_index"))

@categoria.route("/admin/categoria/edit/<string:categoria_id>")
def categoria_edit(categoria_id):
    return render_template("categoria_editar.html",
                           categoria=categoria_collections.find_one({"_id": ObjectId(categoria_id)}))


@categoria.route("/admin/categoria/edit/<string:categoria_id>/form", methods=["POST"])
def categoria_edit_action(categoria_id):
    
    # Coletar dados do formulário
    nome = request.form.get("nome")
    campos = request.form.getlist('campos[]')

    campos = [c.strip() for c in campos if c.strip()]  # remove vazios e espaços
    campos = list(dict.fromkeys(campos))  # remove duplicatas

    # Validação server-side
    if not nome or not campos:
        flash("Todos os campos obrigatórios devem ser preenchidos!", "bad")
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
            flash("Categoria atualizada com sucesso!", "good")
        else:
            flash("Nenhuma alteração foi detectada.", "warning")
            
    except Exception as e:
        print(f"Erro na atualização: {e}")
        flash("Erro crítico na atualização da categoria!", "bad")

    return redirect(url_for(".categoria_index"))


@categoria.route("/admin/categoria/delete/<string:categoria_id>")
def categoria_delete(categoria_id):
    categoria_collections.delete_one({"_id": ObjectId(categoria_id)})
    return redirect(url_for(".categoria_index"))


@categoria.route("/api/categoria/<id>")
def get_categoria(id):
    categoria = categoria_collections.find_one({"_id": ObjectId(id)})
    if not categoria:
       flash("Categoria não encontrada", "bad")
    return jsonify({
        "_id": str(categoria["_id"]),
        "nome": categoria["nome"],
        "campos": categoria["campos"]
    })
