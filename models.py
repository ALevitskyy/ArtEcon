from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(512))
    file = db.Column(db.String(32), unique=True)
    image = db.Column(db.String(32), unique=True)
    title = db.Column(db.String(128), unique=True)
    url = db.Column(db.String(32), unique=True)
    tags = db.relationship("Tag", back_populates="post")
    comment = db.relationship("Comment", back_populates="post")

    def __repr__(self):
        return "<Post %r>" % self.url


class Tag(db.Model):
    __tablename__ = "tag"
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), nullable=False)
    tag_title = db.Column(db.String(32))
    post = db.relationship("Post", foreign_keys="Tag.post_id", back_populates="tags")

    def __repr__(self):
        return "<Tag %r>" % self.tag_title


class Comment(db.Model):
    __tablename__ = "comment"
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey(Post.id), nullable=False)
    comment_author = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    comment_text = db.Column(db.UnicodeText())
    post = db.relationship(
        "Post", foreign_keys="Comment.post_id", back_populates="comment"
    )
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.comment_id"))

    def __repr__(self):
        return "<Tag %r>" % self.tag_title
