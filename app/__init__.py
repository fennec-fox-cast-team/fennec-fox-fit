from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import Config
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
login = LoginManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models
