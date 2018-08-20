from flask import Blueprint, url_for, redirect, render_template
from flask_wtf import Form
from werkzeug import secure_filename
from wtforms import StringField,TextAreaField, Field
from wtforms.widgets import TextInput
from models import db, Post, Tag
import datetime
from app import basic_auth
loading = Blueprint('upload', __name__, template_folder='templates')

class TagListField(Field):
    widget = TextInput()
    
    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

class UploadForm(Form):
    file = StringField("HTML")
    image= StringField("Image")
    title=StringField("Title")
    url=StringField("URL")
    description=TextAreaField("Description")
    tags=TagListField("Tags")

@loading.route('/loading', methods=['GET', 'POST'])
@basic_auth.required
def upload():
    form = UploadForm()
    
    if form.validate_on_submit():

        entry = Post(
                      date=datetime.datetime.date(datetime.datetime.now()),
                      description=form.description.data,
                      file=form.file.data,
                      image=form.image.data,
                      title=form.title.data,
                      url=form.url.data
                      )
        db.session.add(entry)
        db.session.flush()
        for i in form.tags.data:
            tag_entry=Tag(
                           post_id=entry.id,
                           tag_title=i
                           )
            db.session.add(tag_entry)
        db.session.commit()
        return redirect(url_for('upload.upload'))
    
    return render_template('upload.html', form=form)

