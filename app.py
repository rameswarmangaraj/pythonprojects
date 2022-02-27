from flask import Flask, render_template, request, session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import math
# from flask_mail import Mail
from werkzeug.utils import secure_filename
# from SQLAlchemy import create_engine
# from sqlalchemy.engine import url as sa_url

# import cx_Oracle
with open(os.path.dirname(__file__)+"/config.json", "r") as c:
    params = json.load(c)["param"]

app = Flask(__name__)
app.secret_key = 'my_secrete_key'
app.config['UPLOAD_FOLDER']=params['upload_path']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_TLS=True,
    MAIL_USERNAME=params['user'],
    MAIL_PASSWORD=params['pwd']
)
# mail = Mail(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\h419399\\ProjectData\\Software\\sqlite-tools\\testDB.db'
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_db_url']
'''start of config oracle '''
# dnsStr = cx_Oracle.makedsn('localhost', '1521', 'XEPDB1')
# dnsStr = dnsStr.replace('SID', 'SERVICE_NAME')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle://hr:hr' + dnsStr
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# db=SQLAlchemy(app)
# user='hr'
# pwd='hr'
# host='localhost'
# port='1521'
# service='XEPDB1'
db = SQLAlchemy(app)
# db.create_engine(URI)
# db.create_engine('oracle+cx_oracle://' + user + ':' + pwd + '@' + host + ':' + port + '/?service_name=' + service,{})
'''End of oracle'''


class Contact(db.Model):
    '''sno NUMBER,name varchar2(10),email varchar2(20),phone varchar2(12),msg varchar2(30)'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(120), unique=False, nullable=False)
    msg = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=False)


class Post(db.Model):
    '''sno int(11),title text,slug varchar(25),content text,date datetime'''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(120), unique=False, nullable=False)
    content = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=False)
    subtitel = db.Column(db.String(80), unique=False, nullable=False)
    img_url = db.Column(db.String(80), unique=False, nullable=False)


@app.route("/")
def home():
    flash("This is flash message","success")
    flash("This is 2nd flash message","danger")
    db.create_all()
    posts = Post.query.filter_by().all()
    last=len(posts)/params['no_of_post']
    page=request.args.get('page')
    if page==None:
        page='1'
    # pagination logic
    if page=='#':
        page=1
    page=int(page)
    posts=posts[(page-1)*params['no_of_post']:(page-1)*params['no_of_post']+params['no_of_post']]
    if page==1:
        prev='#'
        next="/?page="+str(page+1)
    elif page==last:
        prev="/?page="+str(page-1)
        next='#'
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)
    

    # posts = Post.query.filter_by().all()[0:params['no_of_post']]
    return render_template('index.html', params=params, posts=posts,prev=prev,next=next)


@app.route("/about")
def about():
    return render_template('about.html', params=params)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'user' in session and session['user'] == params['username']:
        posts = Post.query.filter_by().all()
        return render_template('dashbord.html', params=params, posts=posts)

    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('pwd')
        if(uname == params['username'] and password == params['password']):
            session['user'] = uname
            session['pwd'] = password
            posts = Post.query.filter_by().all()
            return render_template('dashbord.html', params=params, posts=posts)

    return render_template('login.html', params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to database '''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('message')
        entry = Contact(name=name, email=email, phone=phone,
                        msg=msg, date=datetime.now())
        db.create_all()#if table is not present then will help in creating table
        db.session.add(entry)
        db.session.commit()
        # mail.send_message("New message from "+name,
        # sender=email,
        # recipients=[params['user']],
        # body=msg+'\n'+phone)
        # db.session.flush()
        print("insertion done")
    return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def postData(post_slug):
    postRes = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, postRes=postRes)


@app.route("/edit/<int:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['username']:
        print(request.method)
        if request.method == 'POST':
            title=request.form.get('title')
            slug=request.form.get('slug')
            content=request.form.get('content')
            subtitel=request.form.get('subtitel')
            img=request.form.get('img')
            date=datetime.now()
            if sno==0:
                post=Post(title=title,slug=slug,content=content,date=date,subtitel=subtitel,img_url=img)
                print(sno)
                db.create_all()
                db.session.add(post)
                db.session.commit()
                print("post done")
            else:
                post=Post.query.filter_by(sno=sno).first()
                post.title=title
                post.slug=slug
                post.content=content
                post.date=date
                post.subtitel=subtitel
                post.img_url=img
                db.session.commit()
                return redirect('/edit/'+str(sno))
    post=Post.query.filter_by(sno=sno).first()
    return render_template("edit.html",params=params,post=post,sno=sno)

@app.route("/delete/<int:sno>", methods=['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['username']:
        post=Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')



@app.route("/post")
def post():
    return render_template('post.html', params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')

@app.route("/upload", methods=['GET', 'POST'])
def uploder():
    if 'user' in session and session['user'] == params['username']:
        if request.method=='POST':
            f=request.files['imgfile']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return 'uploaded successfully'
if __name__ == '__main__':
    app.run(debug=True)
