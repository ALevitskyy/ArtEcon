from loading import loading
from flask_wtf import Form
from wtforms import StringField,IntegerField,TextField,TextAreaField
from models import Post, Tag,Comment
from app import app,db
from flask import render_template,redirect,request
from sqlalchemy import desc
from flask_cors import cross_origin
from trading_simulator.simulate import simulate
import datetime
def get_tags():
    tags_query=db.engine.execute("Select Count(tag_id),tag_title from Tag group by tag_title order by Count(tag_id) desc limit 8")
    return [i[1] for i in tags_query]

class CommentForm(Form):
    author=StringField("Author",render_kw={'maxlength': 32})
    comment_text=TextAreaField("Comment Text",render_kw={"cols":"60", "rows":"7"})
    parent_id=IntegerField("Parent Comment")


app.register_blueprint(loading, url_prefix='/upload')
app.register_blueprint(simulate, url_prefix='/simulator')

@app.context_processor
def utility_processor():
    def remove_whitespace(mystring):
        return mystring.replace(" ", "_")
    return dict(remove_whitespace=remove_whitespace)

@app.route('/')
def index():
    query=reversed(Post.query.all())
    return render_template("/new_index.html",posts=query,tags=get_tags())

@app.route('/articles/<articlename>',methods=['GET', 'POST'])
@cross_origin()
def article_show(articlename):
    query=db.engine.execute("Select file,id From Post Where url='"+articlename+"'")
    comment_form=CommentForm()
    for i in query:
        filename=i[0]
        post_id=i[1]
    query2=db.engine.execute("""WITH RECURSIVE nodes_cte(comment_id, post_id, comment_author, timestamp, comment_text,parent_id,depth,path) AS (
        SELECT tn.comment_id, tn.post_id, tn.comment_author, tn.timestamp::timestamp(0), tn.comment_text,tn.parent_id, 1::INT AS depth, tn.comment_id::TEXT AS path FROM comment AS tn WHERE tn.post_id =""" +str(post_id)+"""AND tn.parent_id is null UNION ALL
        SELECT c.comment_id, c.post_id, c.comment_author, c.timestamp::timestamp(0), c.comment_text,c.parent_id, p.depth + 1 AS depth, (p.path || '->' || c.comment_id::TEXT) FROM nodes_cte AS p, comment AS c WHERE c.parent_id = p.comment_id
        )
        SELECT * FROM nodes_cte ORDER  BY path, timestamp;""")
    if comment_form.validate_on_submit():
        if comment_form.parent_id.data=="99999999999999999" or comment_form.parent_id.data==99999999999999999:
            entry = Comment(
                     post_id=post_id,
                     comment_author=comment_form.author.data,
                     timestamp=datetime.datetime.now(),
                     comment_text=comment_form.comment_text.data,
                     )
        else:
            entry = Comment(
                            post_id=post_id,
                            comment_author=comment_form.author.data,
                            timestamp=datetime.datetime.now(),
                            comment_text=comment_form.comment_text.data,
                            parent_id=comment_form.parent_id.data,
                            )
        db.session.add(entry)
        db.session.flush()
        db.session.commit()
        return(redirect(request.url))
    return render_template("/article3.html",filename=filename,
                           tags=get_tags(),
                           comment_form=comment_form,
                           query2=query2)

@app.route('/category/<categoryname>')
def categorypage(categoryname):
    query=Tag.query.filter_by(tag_title=categoryname).order_by(desc(Tag.tag_id))
    return render_template("/category.html",posts=query,tags=get_tags())

@app.route('/about')
def about():
    return render_template("/about_page2.html",tags=get_tags())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_ready.html',tags=get_tags()), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html',tags=get_tags()), 500

@app.route('/allcategories')
def all_cater():
    tags_query=db.engine.execute("Select Count(tag_id),tag_title from Tag group by tag_title order by Count(tag_id) desc")
    return render_template(
                "/all_categories.html",
                tags=get_tags(),
                caters=tags_query
                           )

