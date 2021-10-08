from flask import make_response, abort
from config import db
import os
import datetime
from models import Occupancytype, OccupancytypeSchema


def read_all():
    """
    This function responds to a request for /api/occupancytype/all
    with the complete lists of occupancy load into data from database
    :return:        json string of list of occupancy load info
    
    """
    
    # Create the list of snapshots from our data
    all_rows = Occupancytype.query.order_by(Occupancytype.id).all()
    
    # Serialize the date for the response
    occload_schema = OccupancytypeSchema(many=True)
    
    data = occload_schema.dump(all_rows)
    return data