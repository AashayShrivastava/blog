from flask import Flask,render_template,redirect,url_for,request,session
from flask_wtf import FlaskForm
from flask_login import LoginManager,login_required,login_user,current_user,UserMixin,logout_user
from wtforms import StringField,SubmitField,PasswordField,BooleanField,TextAreaField,DateTimeField
from wtforms.validators import DataRequired,Email,EqualTo,Length,ValidationError
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app=Flask(__name__)
app.config['SECRET_KEY']="sdhvdsgydvsygvg"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm_password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('SignIn')
class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('SignUp')
class UpdateForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Update')
    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("yo")
                
class AddForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    content=TextAreaField("Content",validators=[DataRequired()])
    submit=SubmitField("Add")
class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()])
    content=TextAreaField("Content",validators=[DataRequired()])
    submit=SubmitField("Update")
class FilterForm(FlaskForm):
    wordsearch=StringField("",validators=[DataRequired()])
    submit=SubmitField("Search")

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=False,unique=True)
    username=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(20),nullable=False)
    password=db.Column(db.String(20),nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)
class Post(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True,nullable=False,unique=True)
    title=db.Column(db.String(20),nullable=False)
    content=db.Column(db.String(600),nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.now())
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/",methods=['GET','POST'])
def index():
    form=FilterForm()
    page=request.args.get('page',1,type=int)

    post1=Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=3)
    
   
    
    for post2 in post1:
        print(post2.title)
        print(post2.author.username)
        print(post2.date_posted)
        print(post1.page)
        
    if form.validate_on_submit():
        print(form.wordsearch.data)
        print(page)
        return redirect(url_for('filter_posts',query=form.wordsearch.data,page1=page))
        
    return render_template("home.html",posting=post1,form=form)
    
@app.route("/register",methods=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data,password=form.password.data)
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        with app.app_context():
            user3=User.query.all()
            for i in range(len(user3)):
                print(user3[i].email," ",user3[i].password," ",user3[i].username)
        return redirect(url_for('index'))
    return render_template("register.html",form=form)
@app.route("/login",methods=['GET','POST'])
def login():
    
    form=LoginForm()
    if form.validate_on_submit():
        print(form.email.data)
        user2=User.query.filter_by(email=form.email.data).first()
        
        if user2:
            if user2.password==form.password.data:
                login_user(user2)
                print(current_user.username)
                print(next)
                next_page=request.args.get('next')
                if next_page:
                    print(next_page)
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))

            
        
    return render_template("login.html",form=form)
@app.route("/updates",methods=['GET','POST'])
@login_required
def updates():
    print(current_user.username)
    form=UpdateForm()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        print(current_user.username)
        print(current_user.password)
        return redirect(url_for('index'))
    if request.method=="GET":
        form.username.data=current_user.username
        form.email.data=current_user.email
    return render_template("update.html",form=form)
@app.route("/logout",methods=['GET','POST'])  
def logout(): 
    print(current_user.username)
    logout_user()
    return redirect(url_for('index'))
@app.route("/add",methods=['GET','POST'])
@login_required
def add_post():
    form=AddForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        with app.app_context(): 
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template("add.html",form=form)
@app.route("/add/<int:post_id>",methods=['GET','POST']) 
@login_required
def update_post(post_id):
    post=Post.query.get(post_id)
    if post.author!=current_user:
        return redirect(url_for('index'))
    
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        print(post.title)
        post1=Post.query.all()
        for post2 in post1:
            print(post2.title)
        return redirect(url_for('index'))
    if request.method=="GET":
        form.title.data=post.title
        form.content.data=post.content


    return render_template("post.html",form=form,posts=post)
@app.route("/delete/<int:post_id>",methods=['GET','POST']) 
@login_required
def delete_post(post_id):
    post=Post.query.get(post_id)
    if post.author!=current_user:
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    post1=Post.query.all()
    for post2 in post1:
        print(post2.title)
    return redirect(url_for('index'))
@app.route("/user/<string:username>",methods=['GET','POST']) 

def user_posts(username):
    form=FilterForm()
    page=request.args.get('page',1,type=int)

    if form.validate_on_submit():
        print(form.wordsearch.data)
        return redirect(url_for('filter_posts1',query=form.wordsearch.data,username=username,page1=page))
    
    user=User.query.filter_by(username=username).first()
    page=request.args.get('page',1,type=int)

    post=Post.query.filter_by(author=user).order_by(Post.id.desc()).paginate(page=page,per_page=3)
    return render_template("user_post.html",posts=post,form=form,username=username)


@app.route("/post1/<string:query>/<string:username>/<int:page1>",methods=['GET','POST']) 
def filter_posts1(query,username,page1):
    
    form=FilterForm()
    if query:
        page=request.args.get('page',page1,type=int)
        post1=Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=3)
        filtered_posts = []
        for c in post1:
            print(post1.page)
            print("hii")
            if c.author.username==username:
                if query.lower() in (c.title + c.content).lower() and page1==post1.page:
                    filtered_posts.append(c)
        if len(filtered_posts)!=0:
            return render_template("user_post1.html",posts=filtered_posts)
        else:
            return redirect(url_for('user_posts',username=username))

    
@app.route("/post/<string:query>/<int:page1>",methods=['GET','POST']) 
def filter_posts(query,page1):
    
    form=FilterForm()
    if query:
        
        page=request.args.get('page',page1,type=int)
        post1=Post.query.order_by(Post.id.desc()).paginate(page=page,per_page=3)
        filtered_posts2 = []
        for c in post1:
            print(c.title)
            
            print("hii")
            
            if query.lower() in (c.title + c.content+c.author.username).lower() and page1==post1.page:
                filtered_posts2.append(c)
        print(filtered_posts2)
        if len(filtered_posts2)!=0:
            return render_template("user_post1.html",posts=filtered_posts2)
        else:
            return "The word you entered is not in current page"
if __name__=='__main__':
    app.run(debug=True)
