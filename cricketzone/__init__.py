"""
cricketzone/__init__.py — Application Factory
"""

import os
from flask import Flask, render_template
from flask_mail import Mail

from config import get_config

mail = Mail()


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Load config
    app.config.from_object(get_config())

    # Ensure instance/ folder exists
    instance_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "instance"
    )
    os.makedirs(instance_path, exist_ok=True)

    # Init extensions
    mail.init_app(app)

    # Register Blueprints
    from cricketzone.routes.main     import main_bp
    from cricketzone.routes.products import products_bp
    from cricketzone.routes.orders   import orders_bp
    from cricketzone.routes.contact  import contact_bp
    from cricketzone.routes.admin    import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)

    # Init DB
    from cricketzone.database import init_db, close_db
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app