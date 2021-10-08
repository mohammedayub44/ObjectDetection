## Technologies Used: 

[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - It's a Flask wrapper around SQLAlchemy which is a popular Python SQL toolkit and Object Relational Mapping (ORM) wrappers for developing database operations. 

[Flask-Marshmallow](https://flask-marshmallow.readthedocs.io/en/latest/) - wrapper for Flask apps to do serialization/deserialization to display Python objects in JSON format (also used for Swagger UI).

[Swagger UI](https://swagger.io/tools/swagger-ui/) - visualize and interact with your DB endpoints seemlessly. Makes backend implemenation easy and client-side consumption easy.

[Connexion](https://connexion.readthedocs.io/en/latest/index.html) - built on top of Flask to handle connection requests from Swagger UI design to database endpoints.  


## Backend Service Details:

**`config.py`** - Defines the configuration required for the Flask-App. This includes initializations for `SQLAlchemy`, `Marshmallow` and `connexion` objects.

**`models.py`** - Defines ORM of Table level classes and column level attributes for the components stored in DB. They are Video, Snapshot and OccupancyType. 

**`video.py`** - Describes the video functions that run against `Video` endpoints. Like `create`, `delete`, `update` etc.

**`snapshot.py`** - Describes the snapshot functions that run against `Snapshot` endpoints. Like `get_weekly_data`, `get_daily_data` etc.

**`occupancytype.py`** -  Function to display all Occupancy types available.

**`app.py`** -
- It stiches all the above functionalities together into one driver application. 
- Its containes functionality for fethcing required video and snapshot information from the client.
- Coordinating with `TensorFlow` and `Torchserve` model servers.
- Creating all the necessary DB tables if not already present and load Occupancy data from static CSV file.
             
 ## Swagger Details - 
 
 The Swagger UI is driven by the `swagger.yaml` present in the root folder. The connexion config in `config.py` picks up this file using `basedir` during the start.
 UI is available at `http://<publicIPv4>:8081/api/ui/` after the application has started.
 
 It should look something like this : (feel free to play around)
 
 <img src="https://github.com/NFPA/Crowd_Detection/blob/development/images/Swagger.PNG" width="800" height="520">

