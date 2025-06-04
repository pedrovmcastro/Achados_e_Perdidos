from flask import Blueprint, request, redirect, url_for, session, flash
from bson.codec_options import CodecOptions
import secret
import pymongo
import hashlib
from datetime import timezone
from time import time

client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client['achadoseperdidos'].with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))

funcionarios_collections = db['funcionarios']
logon = Blueprint("logon", __name__)


@logon.route("/logon", methods=["POST"])
def logon_action():
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")

    if matricula and senha:
        funcionario = funcionarios_collections.find_one({
            "matricula": matricula,
            "senha": hashlib.sha256(senha.encode('utf-8')).hexdigest(),
        })

        if funcionario and not funcionario.get("desligado"):
            session['funcionario_id'] = str(funcionario['_id'])
            session['nome'] = funcionario['nome']
            session['administrador'] = funcionario.get('administrador', False)
            session['logado'] = int(time())

            flash("Login com sucesso!", "success")
            return redirect(url_for('admin'))

    flash("Login Inválido!", "danger")
    return redirect(url_for('login'))


@logon.route('/logout')
def logout():
    session.pop('funcionario_id', None)
    session.pop('nome', None)
    session.pop('administrador', None)
    session.pop('logado', None)
    return redirect(url_for('login'))
