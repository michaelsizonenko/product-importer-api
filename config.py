import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(dotenv_path):
    raise Exception('.env file does not exist')

load_dotenv(dotenv_path)


SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_BROKER_URL')
UPLOAD_EXTENSIONS = ['.csv']
UPLOAD_PATH = 'uploads'
