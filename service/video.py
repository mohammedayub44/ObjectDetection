import os
from flask import make_response, abort
from config import db
from models import Video, VideoSchema, Occupancytype, Snapshot, SnapshotSchema
from datetime import datetime

def read_all():
    """
    This function responds to a request for /api/video
    with the complete lists of videos in database
    :return:        json string of list of videos
    
    """
    
    # Create the list of videos from our data
    all_videos = Video.query.order_by(Video.url).all()
    
    # Serialize the date for the response
    video_schema = VideoSchema(many=True)
    
    data = video_schema.dump(all_videos)
    return data


def read_one(video_id):
    """
    This function responds to a request for /api/video/{video_id}
    with one mathcing video from videos
    
    :param video_id:   Id of video to find
    :return:            matched video 
    
    """
    
    # Read video from our data
    video = Video.query.filter(Video.id == video_id).one_or_none()
    
    # if found
    if video is not None:
        
        # Serialize the date for the response
        video_schema = VideoSchema()
        data = video_schema.dump(video)
        return data
    
    else:
        # Video not found
        abort(
            404,
            "Video not found for Id: {video_id}".format(video_id=video_id),
        )


def create(video):
    """
    This function creates a new video in the database with
    provide video data. 
    
    :param video:  video to create in video structure
    :return:        201 on success, 406 on video exists

    """
    vname = video.get("url")

    existing_video = (
        Video.query.filter(Video.url == vname)
        .one_or_none()
    )
    
    # Check to insert video
    if existing_video is None:

        # Create a video instance using the schema
        schema = VideoSchema()
        new_video = schema.load(video, session=db.session)

        # Add the video to the database
        db.session.add(new_video)
        db.session.commit()

        # Serialize and return the newly created video in the response
        data = schema.dump(new_video)

        return data, 201

    # Otherwise, video exists already
    else:
        existing_video.last_updated = datetime.utcnow()
        # db.session.merge(update)
        db.session.commit()
        abort(
            409,
            "Video with {vname} exists already".format(
                vname=vname
            ),
        )


def delete(video_id):
    """
    This function deletes a video using the video_id
    :param video_id:    Id of the video to delete
    :return:            200 on successful delete, 404 if not found
    
    """
    # Get the video requested
    video = Video.query.filter(Video.id == video_id).one_or_none()

    # Check if found
    if video is not None:
        # Get all Snapshots related to the video, delete static files stored for a video
        all_snapshots = Snapshot.query.filter(Snapshot.video_id == video_id).all()
        snapshot_schema = SnapshotSchema(many=True)
        all_snaps = snapshot_schema.dump(all_snapshots)
        print(str(all_snaps))
        for pic in all_snaps:
            os.remove(os.path.join(pic['heatmap']))
            os.remove(os.path.join(pic['snap']))
        db.session.delete(video)
        db.session.commit()
        return make_response(
            "Video with ID: {video_id} deleted".format(video_id=video_id), 200
        )

    # Otherwise, nope, didn't find that video
    else:
        abort(
            404,
            "Video not found for Id: {video_id}".format(video_id=video_id),
        )


def update(video_id, video):
    """
    This function deletes a video using the video_id
    :param video_id:    Id of the video to delete
    :return:            200 on successful delete, 404 if not found
    
    """
    # Get the video_id to update
    update_vid = Video.query.filter(Video.id == video_id).one_or_none()
    print("Update: "+ str(update_vid))
    
    # Get details to check uniqueness
    vname = video.get("url")
    load_id = video.get("vid_load_ref")
    occ_ref = Occupantload.query.filter(Occupantload.id == load_id).one_or_none()
    
    existing_video = (
        Video.query.filter(Video.url == vname, Video.vid_load_ref == occ_ref).one_or_none()
    )

    # If Id does not exist
    if update_vid is None:
        abort(
            404,
            "Video not found for Id: {video_id}".format(video_id=video_id),
        )

    # # Check for duplicate creation of another video already existing (not required)
    # elif (
    #     existing_video is not None 
    #                     and existing_video.id != video_id 
    #                     and existing_video.video_name == vname
    #                     and existing_video.vid_load_ref == load_id
    # ):
    #     abort(
    #         409,
    #         "Video with {vname} and {loadid} exists already".format(
    #             vname=vname,loadid=load_id
    #         ),
    #     )

    # Now update!
    else:

        # turn the passed in video into a db object
        schema = VideoSchema()
        update = schema.load(video, session=db.session)
        print("Update: "+ str(update))
        
        # Set the id to the video we want to update
        update.id = update_vid.id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated video in the response
        data = schema.dump(update_vid)

        return data, 200
