import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "mysql://dev:fordev@192.168.3.15/syzoj"
UPLOAD_FOLDER = os.path.join(BASE_DIR, "syzoj", "static", "uploads")
JUDGE_TOKEN = "77783949202395150352388871624955475980489287735056"

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
