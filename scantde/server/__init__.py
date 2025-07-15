from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from scantde.paths import sym_dir, db_path

db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__,
        static_folder=str(sym_dir)
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db.init_app(app)

    from .index import index_bp
    app.register_blueprint(index_bp)
    from .by_name import name_bp
    app.register_blueprint(name_bp)
    from .by_date import date_bp
    app.register_blueprint(date_bp)

    # import and register other blueprints as needed

    return app