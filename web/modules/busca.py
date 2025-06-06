from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime, timezone
import pymongo
import secret

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos']
objetos_collections = db['objetos']
categorias_collections = db['categorias']

busca = Blueprint("busca", __name__)


def data_valida(s):
    try:
        datetime.strptime(s, r'%Y-%m-%d')
        return True
    except ValueError:
        return False


@busca.route("/busca", methods=["GET"])
def buscar_objetos():
    data_encontrado = request.args.get('data_encontrado')
    categoria_id = request.args.get('categoria_id')
    identificacao = request.args.get('identificacao')
    local_encontrado = request.args.get('local_encontrado')
    backend = request.args.get('backend')

    query = {}

    if data_encontrado:
        if not data_valida(data_encontrado):
            return jsonify({"error": "Data inválida"}), 400

        hoje = datetime.now()
        encontrada = datetime.strptime(data_encontrado, r'%Y-%m-%d')

        if encontrada > hoje:
            return jsonify({"error": "Data inválida"}), 400

        query['data_encontrado'] = data_encontrado

    if categoria_id:
        categoria = db.categorias.find_one({'_id': ObjectId(categoria_id)})

        if not categoria:
            return jsonify({"error": "Categoria inválida"}), 400

    if identificacao:
        query['identificacao'] = {"$regex": identificacao, "$options": "i"}

    if local_encontrado:
        query['local_encontrado'] = {"$regex": local_encontrado, "$options": "i"}

    if not backend:
        query['status'] = 'perdido'

    pipeline = []

    if query:
        pipeline.append({"$match": query})

    project = {
        "data_encontrado": 1,
        "categoria_nome": "$categoria.nome",
        "identificacao": 1,
        "local_encontrado": 1,
    }

    if backend:
        project.extend({
            "_id": {"$toString": "$_id"},
            "status": 1,
            "categoria_id": {"$toString": "$categoria._id"},
        })

    pipeline.extend([
        {
            "$lookup": {
                "from": "categorias",
                "localField": "categoria",
                "foreignField": "_id",
                "as": "$categoria"
            }
        },
        {
            "$unwind": "$categoria"
        },
        {
             "$project": project
        }
        {"$sort": {"data_encontrado": -1}}
    ])

    objetos_encontrados = list(objetos_collections.aggregate(pipeline))

    for obj in objetos_encontrados:
        obj['categoria_nome'] = obj['categoria']['nome']
        obj['data_encontrado'] = obj['data_encontrado'].strftime("%Y-%m-%d")

    return jsonify(objetos_encontrados)
