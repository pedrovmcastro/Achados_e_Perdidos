from bson.codec_options import CodecOptions
from flask import Blueprint, request, redirect, url_for, session, flash
from hashlib import sha256
from datetime import datetime, timezone
from time import time
import secret
import pymongo


client = pymongo.MongoClient(secret.ATLAS_CONNECTION_STRING)
db = client["achadoseperdidos"].with_options(
    codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc)
)
funcionarios_collections = db["funcionarios"]

logon = Blueprint("logon", __name__)


def data_valida(s):
    try:
        datetime.strptime(s, r"%Y-%m-%d")
        return True
    except ValueError:
        return False


@logon.route("/logon", methods=["POST"])
def logon_action():
    matricula = request.form.get("matricula")
    senha = request.form.get("senha")

    if matricula and senha:
        funcionario = funcionarios_collections.find_one(
            {
                "matricula": matricula,
                "senha": sha256(senha.encode("utf-8")).hexdigest(),
            }
        )

        if funcionario and not funcionario.get("desligado"):
            session["funcionario_id"] = str(funcionario["_id"])
            session["nome"] = funcionario["nome"]
            session["administrador"] = funcionario.get("administrador", False)
            session["logado"] = int(time())

            flash("Login com sucesso!", "success")
            return redirect(url_for("admin"))

    flash("Login Inválido!", "danger")
    return redirect(url_for("login"))


@logon.route("/logout")
def logout():
    session.pop("funcionario_id", None)
    session.pop("nome", None)
    session.pop("administrador", None)
    session.pop("logado", None)
    return redirect(url_for("login"))
