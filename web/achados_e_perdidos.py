from flask import Flask, render_template

from decorators import login_required
from zoneinfo import ZoneInfo    # fuso horário

from modules.funcionarios import funcionario
from modules.categorias import categoria
from modules.objetos import objeto
from modules.logon import logon

app = Flask(__name__)
app.secret_key = '-\x06\xb3\xbd\x15/\xc3\xef~\xd8]\xb3\xef\xd8\xa3\xe5\xa5Sn\xf3SNx\xa9'

app.register_blueprint(categoria)
app.register_blueprint(objeto)
app.register_blueprint(funcionario)
app.register_blueprint(logon)


# Filtros #
@app.template_filter('format_datetime')
def jinja_format_datetime(value):
    if value is None:
        return ""
    # Converte para o fuso horário de São Paulo
    local_tz = ZoneInfo("America/Sao_Paulo")
    value_local = value.astimezone(local_tz)
    return value_local.strftime("%d/%m/%Y %H:%M")


# ----- #
# Index #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')


@app.route('/login/')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
