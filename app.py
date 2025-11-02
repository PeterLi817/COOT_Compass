from flask import Flask
from views import main
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.register_blueprint(main)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables

        # Add fake admin user if it doesn't exist
        if not User.query.filter_by(email='admin@colby.edu').first():
            admin = User(email='admin@colby.edu', role='admin')
            admin.set_password('1234')
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)
