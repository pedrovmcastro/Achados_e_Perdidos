from flask import Blueprint, render_template, request, redirect, url_for, flash

import pymongo

fatecs = Blueprint("fatecs", __name__)
fatecs.secret_key = "-\x06\xb3\xbd\x15/\xc3\xef~\xd8]\xb3\xef\xd8\xa3\xe5\xa5Sn\xf3SNx\xa9"


@fatecs.route("/fatec/")
def fatecs_index():
    conn, c = open_db("convocados.db")

    sql = '''
    SELECT fatecs.*,
           cidades.nome AS cidade,
           regioes.nome AS regiao
    FROM fatecs
    INNER JOIN cidades ON fatecs.cidade_id = cidades.id
    INNER JOIN regioes ON fatecs.regiao_id = regioes.id
    ORDER BY nome COLLATE NOCASE
    '''

    c.execute(sql)
    fatecs = c.fetchall()

    sql = '''
    SELECT *
    FROM cidades
    ORDER BY nome COLLATE NOCASE
    '''

    c.execute(sql)
    cidades = c.fetchall()

    sql = '''
    SELECT *
    FROM regioes
    ORDER BY nome COLLATE NOCASE
    '''

    c.execute(sql)
    regioes = c.fetchall()

    close_db(conn, c)

    return render_template("fatec.html",
                           fatecs=fatecs,
                           cidades=cidades,
                           regioes=regioes)


@fatecs.route("/fatec/add", methods=["POST"])
def fatec_add():
    nome = request.form.get("nome")
    nome_legal = request.form.get("nome_legal")
    cidade_id = request.form.get("cidade")
    regiao_id = request.form.get("regiao")

    if len(nome) > 5 and cidade_id and regiao_id:
        if not nome_legal:
            nome_legal = None

        conn, c = open_db("convocados.db")

        sql = '''
        INSERT INTO fatecs (nome, nome_legal, cidade_id, regiao_id)
        VALUES (?, ?, ?, ?)
        '''

        c.execute(sql, (nome, nome_legal, cidade_id, regiao_id))
        conn.commit()

        close_db(conn, c)

        flash("Cadastrado com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".fatecs_index"))


@fatecs.route("/fatec/edit/<int:fatec_id>")
def fatec_edit(fatec_id):
    conn, c = open_db("convocados.db")

    sql = '''
    SELECT *
    FROM fatecs
    WHERE id = ?
    '''

    c.execute(sql, (fatec_id,))
    fatec = c.fetchone()

    sql = '''
    SELECT *
    FROM cidades
    ORDER BY nome COLLATE NOCASE
    '''

    c.execute(sql)
    cidades = c.fetchall()

    sql = '''
    SELECT *
    FROM regioes
    ORDER BY nome COLLATE NOCASE
    '''

    c.execute(sql)
    regioes = c.fetchall()

    close_db(conn, c)

    return render_template("fatec_edit.html",
                           fatec=fatec,
                           cidades=cidades,
                           regioes=regioes)


@fatecs.route("/fatec/edit", methods=["POST"])
def fatec_edit_action():
    fatec_id = request.form.get("fatec_id")

    nome = request.form.get("nome")
    nome_legal = request.form.get("nome_legal")
    cidade_id = request.form.get("cidade")
    regiao_id = request.form.get("regiao")

    if fatec_id and len(nome) > 5 and cidade_id and regiao_id:
        if not nome_legal:
            nome_legal = None

        conn, c = open_db("convocados.db")

        sql = '''
        UPDATE fatecs
        SET nome = ?,
            nome_legal = ?,
            cidade_id = ?,
            regiao_id = ?
        WHERE id = ?
        '''

        c.execute(sql, (nome, nome_legal, cidade_id, regiao_id, fatec_id))
        conn.commit()

        close_db(conn, c)

        flash("Editado com sucesso!", "good")
    else:
        flash("Alguma coisa deu errado!", "bad")

    return redirect(url_for(".fatecs_index"))


@fatecs.route("/fatec/remove/<int:fatec_id>")
def fatec_remove(fatec_id):
    conn, c = open_db("convocados.db")

    sql = '''
    DELETE FROM notas
    WHERE fatec_id = ?
    '''

    c.execute(sql, (fatec_id,))
    conn.commit()

    sql = '''
    DELETE FROM fatecs_cursos
    WHERE fatec_id = ?
    '''

    c.execute(sql, (fatec_id,))
    conn.commit()

    sql = '''
    DELETE FROM fatecs
    WHERE id = ?
    '''

    c.execute(sql, (fatec_id,))
    conn.commit()

    close_db(conn, c)

    flash("Removido com sucesso!", "good")

    return redirect(url_for(".fatecs_index"))
