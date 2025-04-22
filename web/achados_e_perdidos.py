from flask import Flask, render_template

from modules.fatecs import fatecs
from modules.fatecs_cursos import fatecs_cursos
from modules.cursos import cursos
from modules.notas import notas
from modules.notassimples import notassimples

app = Flask(__name__)
app.secret_key = '-\x06\xb3\xbd\x15/\xc3\xef~\xd8]\xb3\xef\xd8\xa3\xe5\xa5Sn\xf3SNx\xa9'

app.register_blueprint(fatecs)
app.register_blueprint(fatecs_cursos)
app.register_blueprint(cursos)
app.register_blueprint(notas)
app.register_blueprint(notassimples)


# ----- #
# Index #
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
