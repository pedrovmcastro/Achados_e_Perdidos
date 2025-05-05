from flask import Blueprint, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
import secret
import pymongo
from datetime import datetime, timezone


client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
objetos_collections = db['objetos']
objeto = Blueprint("objeto", __name__)


@objeto.route("/admin/objeto")
def objeto_index():
    pipeline = [
        {
            "$lookup": {
                "from": "categorias",
                "localField": "categoria",
                "foreignField": "_id",
                "as": "categoria"
            }
        },
        {"$unwind": "$categoria"},
        {"$sort": {"data_encontrado": -1}}
    ]
    objetos = list(db.objetos.aggregate(pipeline))
    
    # Busca todas as categorias do banco
    categorias = list(db.categorias.find())   

    return render_template("objeto.html",
                           objetos=objetos,
                           categorias=categorias)


@objeto.route("/admin/objeto/add", methods=["POST"])
def objeto_add():
    # Buscar a categoria pelo ID
    categoria_id = request.form.get("categoria")
    categoria = db.categorias.find_one({"_id": ObjectId(categoria_id)})

    if not categoria:
        flash("Categoria inválida", "bad")
        return redirect(url_for(".objeto_index"))
    
    # Inserir no banco
    data_encontrado = request.form.get('data_encontrado')
    local_encontrado = request.form.get('local_encontrado')

    if data_encontrado and local_encontrado:
        objetos_collections.insert_one({
            "descricao": request.form.get("descricao"),
            "imagem": request.form.get("imagem"),
            "categoria": ObjectId(categoria_id),
            "data_insercao": datetime.now(timezone.utc),
            "data_encontrado": data_encontrado,
            "identificacao": request.form.get('identificacao'),
            "local_encontrado": local_encontrado,
            "resolvido": False,
            "status": "perdido"
        })
        flash("Cadastrado com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".objeto_index"))
