from flask import Flask, render_template, request, redirect, url_for
from db_setup import session, User, Paper, Topic
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Needed for form security

# Define Forms
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Add User')

class PaperForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author_id = IntegerField('Author ID', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Paper')

class TopicForm(FlaskForm):
    name = StringField('Topic Name', validators=[DataRequired()])
    paper_id = IntegerField('Paper ID', validators=[DataRequired()])
    submit = SubmitField('Add Topic')

@app.route("/", methods=["GET", "POST"])
def home():
    user_form = UserForm()
    paper_form = PaperForm()
    topic_form = TopicForm()
    search_form = SearchForm()

    # Default: Show all records
    users = session.query(User).all()
    papers = session.query(Paper).all()
    topics = session.query(Topic).all()

    if search_form.validate_on_submit():
        query = search_form.query.data.lower()
        users = session.query(User).filter(User.name.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")).all()
        papers = session.query(Paper).filter(Paper.title.ilike(f"%{query}%")).all()
        topics = session.query(Topic).filter(Topic.name.ilike(f"%{query}%")).all()

    return render_template("index.html", users=users, papers=papers, topics=topics,
                           user_form=user_form, paper_form=paper_form, topic_form=topic_form, search_form=search_form)

# Route to Edit a User
@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = session.get(User, user_id)
    if not user:
        return redirect(url_for("home"))

    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        session.commit()
        return redirect(url_for("home"))

    return render_template("edit_user.html", form=form, user=user)

# Route to Edit a Paper
@app.route("/edit_paper/<int:paper_id>", methods=["GET", "POST"])
def edit_paper(paper_id):
    paper = session.get(Paper, paper_id)
    if not paper:
        return redirect(url_for("home"))

    form = PaperForm(obj=paper)

    if form.validate_on_submit():
        paper.title = form.title.data
        paper.author_id = form.author_id.data
        paper.content = form.content.data
        session.commit()
        return redirect(url_for("home"))

    return render_template("edit_paper.html", form=form, paper=paper)

# Route to Edit a Topic
@app.route("/edit_topic/<int:topic_id>", methods=["GET", "POST"])
def edit_topic(topic_id):
    topic = session.get(Topic, topic_id)
    if not topic:
        return redirect(url_for("home"))

    form = TopicForm(obj=topic)

    if form.validate_on_submit():
        topic.name = form.name.data
        topic.paper_id = form.paper_id.data
        session.commit()
        return redirect(url_for("home"))

    return render_template("edit_topic.html", form=form, topic=topic)

# Route to Delete a User
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
    return redirect(url_for("home"))

# Route to Delete a Paper
@app.route("/delete_paper/<int:paper_id>")
def delete_paper(paper_id):
    paper = session.get(Paper, paper_id)
    if paper:
        session.delete(paper)
        session.commit()
    return redirect(url_for("home"))

# Route to Delete a Topic
@app.route("/delete_topic/<int:topic_id>")
def delete_topic(topic_id):
    topic = session.get(Topic, topic_id)
    if topic:
        session.delete(topic)
        session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
