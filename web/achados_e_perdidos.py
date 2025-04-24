from flask import Flask, render_template

from modules.funcionarios import funcionario

app = Flask(__name__)
app.secret_key = '-\x06\xb3\xbd\x15/\xc3\xef~\xd8]\xb3\xef\xd8\xa3\xe5\xa5Sn\xf3SNx\xa9'

#app.register_blueprint(categorias)
#app.register_blueprint(objetos)
app.register_blueprint(funcionario)

# ----- #
# Index #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
