#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
from functools import wraps
from flask import Flask, redirect, request, Response, render_template, g
import hashlib

# Should be in a separate config file
SALT = u'yuryoujhflhsv,.sbuireveruivn rio2316+54849+62"";efqqwfrqw#$@R$EWF#C FFSDC./12213232312'
ADMINS = ['yves']


DATABASE = 'jdr.db'

app = Flask("RPG server")


def check_auth(user, pw):
    sha = hashlib.new('SHA256')
    sha.update((user + pw + SALT).encode('utf-8'))
    h = sha.hexdigest()
    print(h)
    db = sqlite3.connect("jdr.db")
    cur = db.cursor()
    cur.execute("SELECT username FROM users WHERE username=? AND password=?;", (user, h))
    ret = cur.fetchall()
    cur.close()
    return len(ret) > 0


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        '''Could not verify your access level for that URL.
        You have to login with proper credentials''', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.commit()
        db.close()


@app.route('/admin/create_path', methods=['POST'])
@requires_auth
def create_path():
    db = get_db()
    auth_user = request.authorization.username
    if auth_user not in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    cur.execute("INSERT INTO paths (`src`, `dst`, `desc`) VALUES (?, ?, ?);",
                [request.form["src"],
                 request.form["dst"],
                 request.form["desc"]])
    db.commit()
    return redirect("/")


@app.route('/admin/create_place', methods=['POST'])
@requires_auth
def create_place():
    db = get_db()
    auth_user = request.authorization.username
    if auth_user not in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    cur.execute("INSERT INTO locations (`name`) VALUES (?)", [request.form["name"]])
    db.commit()
    return redirect("/")


@app.route('/go/<direction>', methods=['GET'])
@requires_auth
def go(direction):
    db = get_db()
    # TODO: Check if legit
    cur = db.cursor()
    auth_user = request.authorization.username
    cur.execute("""UPDATE characters 
						SET location=?  
						WHERE characters.owner IN (SELECT Id FROM users WHERE users.username=?)""",
                (int(direction), auth_user))
    db.commit()
    cur.close()
    return redirect("/")


@app.route('/logout')
def logout():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return "Successfully disconnected"
    else:
        return "Error while logging out"

@app.route('/')
@requires_auth
def index():
    db = get_db()

    auth_user = request.authorization.username
    cur = db.cursor()

    cur.execute("""SELECT characters.id, U.id
    			          	  FROM characters 
    			          	  INNER JOIN users U ON characters.owner = U.id AND U.username=?;""", (auth_user,))
    charac_id, auth_id = cur.fetchall()[0]

    cur.execute("""SELECT characters.name , locations.name 
			          	  FROM characters 
			          	  INNER JOIN users U ON characters.owner = U.id AND U.username=? 
			          	  INNER JOIN locations ON locations.id = characters.location;""", (auth_user,))

    cname, lname = cur.fetchall()[0]

    access = list()
    cur.execute("""SELECT L2.name, L2.id, paths.desc
    			          	  FROM paths
    			          	  INNER JOIN locations L1 ON paths.src = L1.id
   			          	      INNER JOIN locations L2 ON paths.dst = L2.id
    			          	  INNER JOIN characters ON characters.owner=? AND characters.location = paths.src;""",
                (auth_id,))

    for row in cur.fetchall():
        access.append((row[0], row[1], row[2]))
        print(row)

    print()
    cur.execute("""SELECT L2.name, L2.id, paths.desc
                              FROM paths
                              INNER JOIN locations L1 ON paths.dst = L1.id
                              INNER JOIN locations L2 ON paths.src = L2.id
                              INNER JOIN characters ON characters.id=? AND characters.location = paths.dst AND paths.both_ways=1;""",
                (charac_id,))

    for row in cur.fetchall():
        access.append((row[0], row[1], row[2]))
        print(row)

    context = {'username': auth_user,
               'characname': cname,
               'location': lname,
               'access': access}

    if auth_user in ADMINS:
        context['places'] = list()
        cur.execute("SELECT * FROM locations;")
        for row in cur.fetchall():
            context['places'].append(row)
        cur.close()
        return render_template('index.tpl', **context) + render_template('admin.tpl', **context)
    else:
        cur.close()
        return render_template('index.tpl', **context)


if __name__ == '__main__':
    app.run(host='localhost', port=8088, debug=True)
