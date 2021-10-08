from datetime import datetime
from config import db, ma

class Video(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    url         = db.Column(db.String(250), nullable=False)
    units       = db.Column(db.String(20), nullable=True)
    area        = db.Column(db.Numeric(10,4), nullable=False, default=0.0)
    duration    = db.Column(db.Numeric(10,4), nullable=False, default=0.0)
    threshold   = db.Column(db.Numeric(10,4), nullable=False, default=0.0)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    load_id     = db.Column(db.Integer, db.ForeignKey('occupancytype.id'), nullable=False)
    snapshot    = db.relationship('Snapshot', backref='video_id_ref', lazy=True, cascade="all,delete-orphan",)
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('url', 'area', 'load_id', name='video_load_uc'),)
    
    def __repr__(self):
        return f"Video('{self.id}','{self.url}', '{self.area}', '{self.duration}', '{self.units}',\
                '{self.threshold}', '{self.vid_load_ref}', '{self.date_created}', '{self.last_updated}' )"


class Snapshot(db.Model):
    snap        = db.Column(db.Text, nullable=False)
    id          = db.Column(db.Integer, primary_key=True)
    heatmap     = db.Column(db.Text, nullable=False)
    pred_count  = db.Column(db.Float, nullable=False)
    pred_class  = db.Column(db.String(10), nullable=False)
    pred_count_ssdcnet = db.Column(db.Float, nullable=False)
    date_clicked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    video_id    = db.Column(db.Integer, db.ForeignKey('video.id', ondelete='CASCADE'), nullable=False)
        
    def __repr__(self):
        return f"Snapshot('{self.id}', '{self.snap}', '{self.heatmap}', '{self.pred_class}', \
                                '{self.pred_count}', '{self.pred_count_ssdcnet}', '{self.date_clicked}')"


class Occupancytype(db.Model):
    use         = db.Column(db.Text, nullable=False)
    id          = db.Column(db.Integer, primary_key=True)
    load_m2     = db.Column(db.Float, nullable=False)
    load_ft2    = db.Column(db.Float, nullable=False)
    vid         = db.relationship('Video', backref='vid_load_ref', lazy=True,cascade="save-update,merge",)
    
    def __repr__(self):
        return f"Occupancytype('{self.id}', '{self.use}', '{self.load_ft2}', '{self.load_m2}')"


class VideoSchema(ma.ModelSchema):
    class Meta:
        model = Video
        sqla_session = db.session
        

class SnapshotSchema(ma.ModelSchema):
    class Meta:
        model = Snapshot
        sqla_session = db.session


class OccupancytypeSchema(ma.ModelSchema):
    class Meta:
        model = Occupancytype
        sqla_session = db.session
