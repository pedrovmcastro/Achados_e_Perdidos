from flask import Blueprint, request, redirect, url_for, session
from bson.codec_options import CodecOptions
import secret
import pymongo
from datetime import timezone


client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))

funcionarios_collections = db['objetos']
logon = Blueprint("logon", __name__)


@logon.route("/logon", methods=["POST"])
def logon_action():
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")

    funcionario = funcionarios_collections.find_one({
        "matricula": matricula,
        "senha": senha,
    })

    if funcionario:
        session['funcionario_id'] = str(funcionario['_id'])
        session['nome'] = funcionario['nome']
        session['administrador'] = funcionario.get('administrador', False)

    return redirect(url_for('admin'))


@logon.route('/logout')
def logout():
    session.pop('funcionario_id', None)
    session.pop('nome', None)
    session.pop('administrador', None)
    return redirect(url_for('login'))
