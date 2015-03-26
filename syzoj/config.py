import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'test.db')
#SQLALCHEMY_DATABASE_URI = "mysql://root:*****@10.3.45.75/fortest"
