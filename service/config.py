import os
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# Get Parent Directory
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

print("Basedir: " + basedir)

# Create the connexion instance, it creates a Flask App in the background
connex_app = connexion.FlaskApp(__name__, specification_dir=basedir)

# Get underlying flask app
app = connex_app.app

# Set SQLAlchemy Specific Configs
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crowd_counter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['SNAPSHOT_FOLDER'] = '../images/snapshots'
app.config['HEATMAP_FOLDER'] = '../images/heatmaps'
app.config['CLASSIFY_MODEL_FILE'] = '../serving_models/classify_model.pkl'

# Create a DB instance
db= SQLAlchemy(app,session_options={"autoflush": False})

# Initialize Marshmallow
ma = Marshmallow(app)
