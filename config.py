import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'test.db')
UPLOAD_FOLDER=os.path.join(BASE_DIR,"syzoj\\static\\uploads")
JUDGE_TOKEN="77783949202395150352388871624955475980489287735056"
#SQLALCHEMY_DATABASE_URI = "mysql://root:*****@10.3.45.75/fortest"
