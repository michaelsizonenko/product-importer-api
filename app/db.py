from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

conn = SQLAlchemy()
migrate = Migrate(directory="app/migrations")
