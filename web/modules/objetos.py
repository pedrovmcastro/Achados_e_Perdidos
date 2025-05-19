from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from decorators import login_required
import secret
import pymongo
from datetime import datetime, timezone


client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
objetos_collections = db['objetos']
objeto = Blueprint("objeto", __name__)


@objeto.route("/admin/objeto")
@login_required
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

    for obj in objetos:
        valores = obj.get('campos_valores', {})
        obj['campos'] = {
            campo: valores.get(campo, '') for campo in obj['categoria'].get('campos', [])
        }
    
    # Busca todas as categorias do banco
    categorias = list(db.categorias.find())  

    # Converta os ObjectId em strings para evitar erro no `tojson`
    for cat in categorias:
        if isinstance(cat["_id"], ObjectId):
            cat["_id"] = str(cat["_id"])
        cat["campos"] = cat.get("campos", [])
    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }

    return render_template("objeto.html",
                           objetos=objetos,
                           categorias=categorias,
                           sessao=sessao,
                           )


@objeto.route("/admin/objeto/add", methods=["POST"])
@login_required
def objeto_add():
    # Buscar a categoria pelo ID
    print()
    categoria_id = request.form.get("categoria", None)

    if not categoria_id:
        flash("Alguma coisa deu errado!", "danger")
        return redirect(url_for(".objeto_index"))
    
    categoria = db.categorias.find_one({"_id": ObjectId(categoria_id)})

    if not categoria:
        flash("Alguma coisa deu errado!", "danger")
        return redirect(url_for(".objeto_index"))
    
    # Dados fixos
    descricao = request.form.get("descricao")
    data_encontrado = request.form.get('data_encontrado')
    local_encontrado = request.form.get('local_encontrado')

    # Extrair campos dinâmicos de acordo com a categoria
    valores_campos = {}
    for campo in categoria.get('campos', []):
        # o nome do campo no form é 'campos_valores[<campo>]'
        key = f"campos_valores[{campo}]"
        valor = request.form.get(key)
        # só adiciona se houver valor (pode querer armazenar string vazia também)
        if valor is not None:
            valores_campos[campo] = valor
    
    # Monta o documento para inserir
    if data_encontrado and local_encontrado:
        objetos_collections.insert_one({
            "descricao": descricao,
            "imagem": request.form.get("imagem"),
            "categoria": ObjectId(categoria_id),
            "data_insercao": datetime.now(timezone.utc),
            "data_encontrado": data_encontrado,
            "identificacao": request.form.get('identificacao'),
            "local_encontrado": local_encontrado,
            "campos_valores": valores_campos,
            "resolvido": False,
            "status": "perdido"
        })
        flash("Cadastrado com sucesso!", "success")
    else:
        flash("Alguma coisa deu errado!", "danger")

    return redirect(url_for(".objeto_index"))


@objeto.route("/admin/objeto/edit/<string:objeto_id>")
@login_required
def objeto_edit(objeto_id):
    pipeline = [
        {"$match": {"_id": ObjectId(objeto_id)}},
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
    resultado = list(db.objetos.aggregate(pipeline))
    objeto = resultado[0]
    sessao = {
        "id": session.get("funcionario_id", ""),
        "nome": session.get("nome", ""),
        "administrador": session.get("administrador", ""),
    }
    return render_template("objeto_editar.html",
                           objeto=objeto,
                           sessao=sessao,
                           )


@objeto.route("/admin/objeto/edit/<string:objeto_id>/form", methods=["POST"])
@login_required
def objeto_edit_action(objeto_id):
    # Coletar dados do formulário
    descricao = request.form.get("descricao")
    data_encontrado = request.form.get('data_encontrado')
    local_encontrado = request.form.get('local_encontrado')
    imagem = request.form.get("imagem")
    identificacao = request.form.get("identificacao")
    resolvido = request.form.get("resolvido")
    status = request.form.get("status")
    
    if not all([data_encontrado, local_encontrado]):
        flash("Todos os campos obrigatórios devem ser preenchidos!", "danger")
        return redirect(url_for(".objeto_edit", objeto_id=objeto_id))
    
    # Preparar dados para atualização
    update_data = {
        "descricao": descricao,
        "data_encontrado": data_encontrado,
        "local_encontrado": local_encontrado,
        "imagem": imagem,
        "identificacao": identificacao,
        "resolvido": resolvido == "on",
        "status": status,
        "resolucao": request.form.get("resolucao"),
        "destinatario_nome": request.form.get("destinatario_nome"),
        "destinatario_nome": request.form.get("destinatario_documento"),
        "destinatario_nome": request.form.get("destinatario_contato"),
    }

    if valores_campos := db.objetos.find_one({"_id": ObjectId(objeto_id)}).get("campos_valores", {}):
        for campo in valores_campos.keys():
            key = f"campos_valores[{campo}]"
            valor = request.form.get(key)
            if valor is not None:
                valores_campos[campo] = valor
                update_data["campos_valores"] = valores_campos

    try:
        # Atualização única no banco de dados
        result = objetos_collections.update_one(
            {"_id": ObjectId(objeto_id)},
            {"$set": update_data}
        )

        if result.modified_count == 1:
            flash("Objeto atualizado com sucesso!", "success")
        else:
            flash("Nenhuma alteração foi detectada.", "warning")
            
    except Exception as e:
        print(f"Erro na atualização: {e}")
        flash("Erro crítico na atualização do objeto!", "danger")

    return redirect(url_for(".objeto_index"))



@objeto.route("/admin/objeto/<string:objeto_id>/delete")
@login_required
def objeto_deletar(objeto_id):
    objetos_collections.delete_one({"_id": ObjectId(objeto_id)})
    return redirect(url_for(".objeto_index"))
