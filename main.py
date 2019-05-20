from flask import Flask, request, redirect, render_template, session, flash
import cgi
from app import app, db
from models import User, Blog
from hashutils import verifyPWH
import re

#Login and Registration Paths
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    #add allowed route to blog without registering, but cannot add or edit content.
    if request.endpoint not in allowed_routes and 'username' not in session: 
        return redirect('/login')

@app.route('/login', methods=["POST", "GET"])
def login():
    error = "Please check your username and password and try again"
    if request.method == "POST": 
        username = request.form["username"]
        user = User.query.filter_by(username=username).first()
        if user == None: 
            return render_template('login.html', error=error, username=username)
        verification = verifyPWH(request.form['password'], user.pwHash)
        if user and verification: 
            session['username'] = username
            session['logged_in'] = True
            return redirect('/userdashboard')
        return render_template('login.html', error=error, username=username)
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        #make option for user to use e-mail as username
        email = request.form['email']
        description = request.form['description']
        if description == None: 
            description = "" 
        password = request.form['password']
        verify = request.form['verify']
        
        #sets errors to be passed through if not accurate
        errorUsername = isUsername(username)
        errorEmail = isEmail(email)
        if email == "":
            errorEmail = "";
        errorPassword = isPassword(password)
        errorVerify = isVerify(verify, password)
        errorDBCountUN = isDBCountUN(username)
        errorDBCountEM = isDBCountEM(email)

        for i in [errorUsername, errorEmail, errorPassword, errorVerify, errorDBCountUN, errorDBCountEM]:
            if i != "":
                return render_template("register.html", 
                username=username, 
                email=email, 
                description=description, 
                errorUsername=errorUsername, 
                errorEmail=errorEmail, 
                errorPassword=errorPassword, 
                errorVerify=errorVerify, 
                errorDBCountUN=errorDBCountUN,
                errorDBCountEM=errorDBCountEM) 
        user = User(username=username, email=email, description=description, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        session['logged_in'] = True
        return redirect('/')
    return render_template('register.html')
        
def isEmail(email):
    emailLower = email.lower()
    if not re.match(r"[a-z][a-z\d.-_&]*[@][a-z\d.-_]+[.][a-z]{2,5}", emailLower):
        return "Fool, that's not an e-mail!"
    return  ""

def isPassword(password):
    if len(password)> 3 and len(password) < 20: 
        return ""
    return "Please choose a password between 3 and 20 characters, thank you!"

def isUsername(username):
    if len(username) > 3 and len(username) < 40: 
        return ""
    return "Please choose a name between 3 and 40 characters, thank you!"

def isVerify(verify, password):
    if verify == password:
        return ""
    return "Your passwords did not match, please try again!"

def isDBCountUN(username):
    usernameDBCount = User.query.filter_by(username=username).count()
    if usernameDBCount > 0:
        return "Your username has been TAKEN!!!!!! But it is okay, just create another"
    return ""

def isDBCountEM(email):
    emailDBCount = User.query.filter_by(email=email).count()
    if emailDBCount > 0:
        return "Your email has been TAKEN!!!!!! But it is okay, just create another"
    return "" 

@app.route("/logout")
def logout():
    session['logged_in'] = False
    del session['username']
    return redirect("/login")

@app.route("/")
def index():
    users = User.query.all()
    return render_template("mainpage.html", users=users, username=session['username'])

endpointsWithoutLogin = ['login', 'register']

@app.route("/addentry", methods=["POST", "GET"])
def addEntry():
    if request.method == "POST":
        title = request.form['title']
        titleError = verifyTitle(title)
        entry = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        entryError = veryifyEntry(entry)
        if title != titleError:
            return render_template('addentry.html', titleError=titleError, entry=entry, entryError=entryError)
        tagline = verifyTag(request.form['tagline'], entry)
        newEntry = Blog(title, tagline, entry, owner)
        db.session.add(newEntry)
        db.session.commit()
        return redirect("/thankyou?title=" + title)
    return render_template('addentry.html', username=session['username'])

def veryifyEntry(entry):
    if len(entry) < 1: 
        return "Please enter a body"
    return "" 

def verifyTitle(title): 
    if len(title) < 1: 
        return "Please enter a title"    
    return title

def verifyTag(tagline, entry):
    if len(tagline) < 1: 
        entry = entry[:40]+"..."
        return entry
    return tagline

@app.route("/userblogs/blog")
def blogpage():
    blogid = request.args.get("id")
    blog = Blog.query.get(blogid)
    return render_template("blog.html", blog=blog, username=session['username'])

@app.route("/thankyou")
def thankyou():
    title = request.args.get("title")
    return render_template('thankyou.html', title=title, username=session['username'])

@app.route("/userdashboard")
def userdashboard():
    user = User.query.filter_by(username=session['username']).first()
    userid = user.id
    entries = Blog.query.filter_by(owner_id=userid).all()
    return render_template('userdashboard.html', entries=entries, username=session['username'])

@app.route("/blog")
def mainpage():
    users = User.query.all()
    return render_template('mainpage.html', users=users, username=session['username'])

@app.route("/userblogs")
def userBlogs():
    userid= request.args.get("userid")
    entries = Blog.query.filter_by(owner_id=userid).all()
    return render_template('userblogs.html', entries=entries, username=session['username'])

@app.route("/editentry", methods=["GET", "POST"])
def editentry():
    user = User.query.filter_by(username=session['username']).first()
    userid = user.id
    entryid = request.args.get("id")
    blog = Blog.query.filter_by(id=entryid).first()
    if blog.owner_id != userid: 
        return redirect("/userdashboard")
    if request.method == "POST":
        blog.title = request.form['title']
        titleError = verifyTitle(blog.title)
        blog.body = request.form['body']
        entryError = veryifyEntry(blog.body)
        if blog.title != titleError:
            return render_template('editentry.html', titleError=titleError, entry=blog.body, entryError=entryError)
        blog.tagline = verifyTag(request.form['tagline'], blog.body)
        db.session.commit()
        return redirect("/userdashboard")
    return render_template("editentry.html", blog=blog, username=session['username'])
        

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()


