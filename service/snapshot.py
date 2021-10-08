from flask import make_response, abort
from config import db
import os
import datetime
from models import Snapshot, SnapshotSchema


def read_all():
    """
    This function responds to a request for /api/snapshot
    with the complete lists of snapshots in database
    :return:        json string of list of snapshots
    
    """
    
    # Create the list of snapshots from our data
    all_snapshots = Snapshot.query.order_by(Snapshot.id).all()
    
    # Serialize the date for the response
    snapshot_schema = SnapshotSchema(many=True)
    
    data = snapshot_schema.dump(all_snapshots)
    return data


def read_all_from_video(video_id):
    """
    This function responds to a request for /api/snapshot/{video_id}
    with all matching snapshots for a video
    
    :param video_id:   Id of snapshot to find
    :return:            matched Snapshot array of objects
    
    """
    
    # Read snapshot from our data
    snapshot = Snapshot.query.filter(Snapshot.video_id == video_id).all()
    
    # if found
    if snapshot is not None:
        
        # Serialize the date for the response
        snapshot_schema = SnapshotSchema(many=True)
        data = snapshot_schema.dump(snapshot)
        return data
    
    else:
        # Snapshot not found
        abort(
            404,
            "Snapshots not found for Video ID : {video_id}".format(video_id=video_id),
        )

def read_one_from_video(video_id,snapshot_id):
    """
    This function responds to a request for /api/snapshot/{video_id}/{snapshot_id}
    with one matching snapshot for a video
    
    :param video_id:   Id of video to find
    :param snapshot_id:  Id of snapshot to find
    :return:            matched snapshot 
    
    """
    
    # Read snapshot from our data
    snapshot = Snapshot.query.filter(Snapshot.video_id == video_id,Snapshot.id == snapshot_id).one_or_none()
    
    # if found
    if snapshot is not None:
        
        # Serialize the date for the response
        snapshot_schema = SnapshotSchema()
        data = snapshot_schema.dump(snapshot)
        return data
    
    else:
        # Snapshot not found
        abort(
            404,
            "Snapshot not found for video {video_id} and snapshot: {snapshot_id}".format(video_id=video_id,snapshot_id=snapshot_id),
        )


# def create(snapshot):
#     """
#     This function creates a new snapshot in the database with
#     provide snapshot data. 
    
#     :param snapshot:  snapshot to create in snapshot structure
#     :return:        201 on success, 406 on snapshot exists

#     """
#     vname = snapshot.get("video_name")

#     existing_video = (
#         Snapshot.query.filter(Snapshot.video_name == vname)
#         .one_or_none()
#     )
    
#     # Check to insert snapshot
#     if existing_video is None:

#         # Create a snapshot instance using the schema
#         schema = VideoSchema()
#         new_video = schema.load(snapshot, session=db.session)

#         # Add the snapshot to the database
#         db.session.add(new_video)
#         db.session.commit()

#         # Serialize and return the newly created snapshot in the response
#         data = schema.dump(new_video)

#         return data, 201

#     # Otherwise, snapshot exists already
#     else:
#         abort(
#             409,
#             "Snapshot with {vname} exists already".format(
#                 vname=vname
#             ),
#         )


def delete(video_id,snapshot_id):
    """
    This function deletes a snapshot for a given video_id
    :param video_id:    Id of the video
    :param snapshot_id:    Id of the snapshot to delete
    :return:            200 on successful delete, 404 if not found
    
    """
    # Get the snapshot requested
    snapshot = Snapshot.query.filter(Snapshot.video_id == video_id, Snapshot.id == snapshot_id).one_or_none()

    # Check if found
    if snapshot is not None:
        os.remove(os.path.join(snapshot.heatmap))
        os.remove(os.path.join(snapshot.snap))
        db.session.delete(snapshot)
        db.session.commit()
        return make_response(
            "Snapshot with video: {video_id} and snapshot: {snapshot_id} deleted".format(video_id=video_id, snapshot_id = snapshot_id), 200
        )

    # Otherwise, nope, didn't find that snapshot
    else:
        abort(
            404,
            "Snapshot not found for video: {video_id} and snapshot {snapshot_id} ".format(video_id=video_id, snapshot_id = snapshot_id),
        )


def update(video_id, snapshot_id, snapshot):
    """
    This function updates a particular snapshot for a given video_id
    :param video_id:    Id of the video
    :param snapshot_id:    Id of the snapshot to update
    :param snapshot       Snapshot instance to update
    :return:            200 on successful update, 404 if not found and 409 is already exists
    
    """
    # Get the video_id to update
    update_vid = Snapshot.query.filter(Snapshot.video_id == video_id, Snapshot.id == snapshot_id).one_or_none()

    # If Id does not exist
    if update_vid is None:
        abort(
            404,
            "Snapshot not found for video : {video_id} and snapshot : {snapshot_id}".format(video_id=video_id, snapshot_id = snapshot_id),
        )

    # Check for duplicate creation of another snapshot already existing
    elif (
        update_vid is not None and (update_vid.snap == snapshot.get("snap") or update_vid.heatmap == snapshot.get("heatmap")) and update_vid.date_clicked == snapshot.get("date_clicked")
    ):
        abort(
            409,
            "Snapshot with same image or heatmap location {snap}  / {heatmap} exists already".format(
                snap=update_vid.snap, heatmap=update_vid.heatmap
            ),
        )

    # Now update!
    else:

        # turn the passed in snapshot into a db object
        schema = SnapshotSchema()
        update = schema.load(snapshot, session=db.session)

        # Set the id to the snapshot we want to update
        update.id = snapshot_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated snapshot in the response
        data = schema.dump(update_vid)

        return data, 200

def get_last_week(video_id):
    """
    This function retuns all snapshots of a video for last weeks time interval
    :param video_id:    Id of the video 
    :return:            200 on successful delete, 404 if not found
    
    """
    current_time = datetime.datetime.utcnow()
    week_ago = current_time - datetime.timedelta(weeks=1)
    
    snapshot_schema = SnapshotSchema(many=True)
    snaps_within_last_week = Snapshot.query.filter(Snapshot.video_id == video_id, Snapshot.date_clicked > week_ago).all()
    data = snapshot_schema.dump(snaps_within_last_week)
    
    return data, 200
    

def get_last_month(video_id):
    """
    This function retuns all snapshots of a video for last month time interval
    :param video_id:    Id of the video 
    :return:            200 on successful delete, 404 if not found
    
    """
    current_time = datetime.datetime.utcnow()
    month_ago = current_time - datetime.timedelta(weeks=4)
    
    snapshot_schema = SnapshotSchema(many=True)
    snaps_within_last_month = Snapshot.query.filter(Snapshot.video_id == video_id, Snapshot.date_clicked > month_ago).all()
    data = snapshot_schema.dump(snaps_within_last_month)
    
    return data, 200
    
def get_last_day(video_id):
    """
    This function retuns all snapshots of a video for one day time interval
    :param video_id:    Id of the video 
    :return:            200 on successful delete, 404 if not found
    
    """
    current_time = datetime.datetime.utcnow()
    day_ago = current_time - datetime.timedelta(days=1)
    
    snapshot_schema = SnapshotSchema(many=True)
    snaps_within_last_day = Snapshot.query.filter(Snapshot.video_id == video_id, Snapshot.date_clicked > day_ago).all()
    data = snapshot_schema.dump(snaps_within_last_day)
    
    return data, 200