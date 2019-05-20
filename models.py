from flask import Flask
from app import db
from hashutils import makePWH

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(1000))
    pwHash = db.Column(db.String(120))
    owner = db.relationship('Blog', backref='owner')

    def __init__(self, username, email, description, password):
        self.username = username
        self.email = email
        self.description = description
        self.pwHash = makePWH(password)
    
    def __repr__(self):
        return '<User %r>' % self.email
    
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    tagline = db.Column(db.String(140))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, tagline, body, owner):
        self.title = title
        self.tagline = tagline
        self.body = body
        self.owner = owner
    
    def __repr__(self):
        return '<Blog %r>' % self.title 
