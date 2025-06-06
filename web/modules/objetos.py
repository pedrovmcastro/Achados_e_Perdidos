from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
from decorators import login_required, admin_required, session_expired
from upload import salvar_arquivo
import secret
import pymongo
from datetime import datetime, timezone

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
objetos_collections = db['objetos']
categorias_collections = db['categorias']
objeto = Blueprint("objeto", __name__)


def get_objetos_perdidos():
    query = {"status": "perdido"}
    objetos = list(objetos_collections.find(query).sort("data_encontrado", -1))

    objetos_perdidos = []

    for obj in objetos:
        categoria = categorias_collections.find_one({"_id": obj['categoria']})
        objetos_perdidos.append({
            'categoria': categoria['nome'],
            'identificacao': obj['identificacao'],
            'local_encontrado': obj['local_encontrado'],
            'data_encontrado': obj['data_encontrado']
        })

    return objetos_perdidos


@objeto.route("/admin/objeto")
@login_required
@session_expired
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
        obj["_id"] = str(obj["_id"])
        obj["categoria"]["_id"] = str(obj["categoria"]["_id"])
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
@session_expired
def objeto_add():
    categoria_id = request.form.get("categoria", None)

    if not categoria_id:
        flash("Não tem o como pegar a categoria!", "danger")
        return redirect(url_for(".objeto_index"))

    categoria = db.categorias.find_one({"_id": ObjectId(categoria_id)})

    if not categoria:
        flash("Categoria inválida!", "danger")
        return redirect(url_for(".objeto_index"))

    caminho_da_imagem = None
    if 'imagem' in request.files:
        imagem = request.files['imagem']

        if imagem.filename:
            caminho_da_imagem = salvar_arquivo(imagem)

            if not caminho_da_imagem:
                flash('Tipo de arquivo da imagem não permitido ou falha ao salvar.', 'danger')

    # Dados fixos
    descricao = request.form.get("descricao")
    data_encontrado = request.form.get('data_encontrado')
    local_encontrado = request.form.get('local_encontrado')
    identificacao = request.form.get('identificacao')

    # Extrair campos dinâmicos de acordo com a categoria
    valores_campos = {}
    for campo in categoria.get('campos', []):
        # o nome do campo no form é 'campos_valores[<campo>]'
        valor = request.form.get(f"campos_valores[{campo}]")
        if valor is not None:
            valores_campos[campo] = valor

    # Monta o documento para inserir
    if descricao and data_encontrado and local_encontrado:
        objetos_collections.insert_one({
            "descricao": descricao,
            "imagem": caminho_da_imagem,
            "categoria": ObjectId(categoria_id),
            "data_insercao": datetime.now(timezone.utc),
            "data_encontrado": data_encontrado,
            "identificacao": identificacao,
            "local_encontrado": local_encontrado,
            "campos_valores": valores_campos,
            "resolvido": False,
            "status": "perdido"
        })
        flash("Cadastrado com sucesso!", "success")
    else:
        vazios = []
        if not descricao:
            vazios.append("descrição")
        if not data_encontrado:
            vazios.append("Data Encontrado")
        if not local_encontrado:
            vazios.append("Local Encontrado")
        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")

        flash("Alguma coisa deu errado!", "danger")

    return redirect(url_for(".objeto_index"))


@objeto.route("/admin/objeto/edit/<string:objeto_id>")
@login_required
@session_expired
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
@session_expired
def objeto_edit_action(objeto_id):
    descricao = request.form.get("descricao")
    data_encontrado = request.form.get('data_encontrado')
    local_encontrado = request.form.get('local_encontrado')
    identificacao = request.form.get("identificacao")
    resolvido = request.form.get("resolvido")
    status = request.form.get("status")
    resolucao = request.form.get("resolucao")
    destinatario_nome = request.form.get("destinatario_nome")
    destinatario_documento = request.form.get("destinatario_documento")
    destinatario_contato = request.form.get("destinatario_contato")
    remover_imagem = request.form.get("removerImagem")

    if not status:
        flash(f"Status não pode ser vazio!", "danger")
        return redirect(url_for(".objeto_edit", objeto_id=objeto_id))

    valido = 1
    if not all([descricao, data_encontrado, local_encontrado]):
        vazios = []
        if not descricao:
            vazios.append("Descrição")
        if not data_encontrado:
            vazios.append("Data encontrado")
        if not local_encontrado:
            vazios.append("Local encontrado")
        if not status:
            vazios.append("Local encontrado")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Campo{plural} não preenchido{plural}:  {', '.join(vazios)}!", "danger")
        valido = 0

    if status != "perdido" and not resolucao and not destinatario_nome and not destinatario_documento and not destinatario_contato:
        vazios = []
        if not resolucao:
            vazios.append("Resolução")
        if not destinatario_nome:
            vazios.append("Nome do destinatário")
        if not destinatario_documento:
            vazios.append("Documento do destinatário")
        if not destinatario_contato:
            vazios.append("Contato do destinatário")

        plural = 's' if len(vazios) > 1 else ''
        flash(f"Status não é perdido assim os campo{plural} devem ser preenchido{plural}:  {', '.join(vazios)}!", "danger")
        valido = 0

    if not valido:
        return redirect(url_for(".objeto_edit", objeto_id=objeto_id))

    objeto = db.objetos.find_one({"_id": ObjectId(objeto_id)})

    caminho_da_imagem = None
    if not remover_imagem:
        if 'imagem' in request.files:
            imagem = request.files['imagem']

            if imagem.filename:
                caminho_da_imagem = salvar_arquivo(imagem)

                if not caminho_da_imagem:
                    flash('Tipo de arquivo da imagem não permitido ou falha ao salvar.', 'danger')

        if not caminho_da_imagem:
            caminho_da_imagem = objeto.get("imagem")

    # Preparar dados para atualização
    update_data = {
        "descricao": descricao,
        "data_encontrado": data_encontrado,
        "local_encontrado": local_encontrado,
        "imagem": caminho_da_imagem,
        "identificacao": identificacao,
        "resolvido": resolvido == "on",
        "status": status,
        "resolucao": resolucao,
        "destinatario": {
            "nome": destinatario_nome,
            "documento": destinatario_documento,
            "contato": destinatario_contato,
        }
    }

    valores_campos = objeto.get("campos_valores", {})
    if valores_campos:
        for campo in valores_campos.keys():
            key = f"campos_valores[{campo}]"
            valor = request.form.get(key)
            if valor is not None:
                valores_campos[campo] = valor
                update_data["campos_valores"] = valores_campos

    try:
        result = objetos_collections.update_one(
            {"_id": ObjectId(objeto_id)},
            {"$set": update_data}
        )

        if result.modified_count == 1:
            flash("Objeto atualizado com sucesso!", "success")
        else:
            flash("Nenhuma alteração foi detectada.", "warning")

    except Exception as e:
        flash("Erro crítico na atualização do objeto!", "danger")

    return redirect(url_for(".objeto_index"))


@objeto.route("/admin/objeto/<string:objeto_id>/delete")
@login_required
@session_expired
@admin_required
def objeto_deletar(objeto_id):
    objetos_collections.delete_one({"_id": ObjectId(objeto_id)})
    return redirect(url_for(".objeto_index"))
