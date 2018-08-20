from loading import loading
from models import Post, Tag
from app import app,db
from flask import render_template
from sqlalchemy import desc
from flask_cors import cross_origin
from trading_simulator.simulate import simulate
def get_tags():
    tags_query=db.engine.execute("Select Count(tag_id),tag_title from Tag group by tag_title order by Count(tag_id) desc limit 8")
    return [i[1] for i in tags_query]

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

@app.route('/articles/<articlename>')
@cross_origin()
def article_show(articlename):
    query=db.engine.execute("Select file From Post Where url='"+articlename+"'")
    for i in query:
        filename=i[0]
    return render_template("/article3.html",filename=filename,tags=get_tags())

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

