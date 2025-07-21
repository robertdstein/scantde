from flask import Flask, request, redirect, url_for, session, render_template_string
from scantde.paths import sym_dir
from scantde.server.login import login_required

from dotenv import load_dotenv
import os

def create_app():
    app = Flask(
        __name__,
        static_folder=str(sym_dir)
    )
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    # db.init_app(app)

    load_dotenv()
    password = os.getenv("SCANTDE_PASSWORD")
    secret_key = os.getenv("SCANTDE_SECRET_KEY")

    if password is None or secret_key is None:
        raise ValueError("Environment variables SCANTDE_PASSWORD and SCANTDE_SECRET_KEY must be set.")

    app.secret_key = secret_key

    login_form = '''
    <form method="post">
      Password: <input type="password" name="password">
      <input type="submit" value="Login">
      {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    </form>
    '''

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            if request.form['password'] == password:
                session['logged_in'] = True
                return redirect(url_for('index.index'))
            else:
                error = 'Incorrect password.'
        return render_template_string(login_form, error=error)

    from .index import index_bp
    app.register_blueprint(index_bp)
    from .by_name import name_bp
    app.register_blueprint(name_bp)
    from .by_date import date_bp
    app.register_blueprint(date_bp)

    return app