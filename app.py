from flask import Flask
from views import main
from models import db
from fill_db import add_fake_data #for development purposes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


app.register_blueprint(main)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
        add_fake_data()

    app.run(debug=True)
