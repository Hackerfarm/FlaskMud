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

@app.route('/admin/create_object', methods=['POST'])
@requires_auth
def create_object():
    db = get_db()
    auth_user = request.authorization.username
    if auth_user not in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    print(request.form)
    cur.execute("INSERT INTO objects (`short_desc`, `location`, `pickable`) VALUES (?, ?, ?)",
                                    [request.form["desc"],
                                     request.form["location"],
                                     request.form["pickable"]])
    db.commit()
    return redirect("/")

@app.route('/admin/teleport_people', methods=['POST'])
@requires_auth
def teleport_people():
    db = get_db()
    auth_user = request.authorization.username
    if auth_user not in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    print(request.form)
    cur.execute("UPDATE characters SET location=? WHERE id=?",
                [request.form["location"],
                 request.form["person"]])
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

@app.route('/pick_up/<obj_id>', methods=['GET'])
@requires_auth
def pick_up(obj_id):
    db = get_db()
    cur = db.cursor()
    auth_user = request.authorization.username

    cur.execute("""SELECT users.id, characters.location 
                        FROM users 
                        INNER JOIN characters ON users.username=? AND characters.owner=users.id""", (auth_user,))
    (uid, cloc) = cur.fetchall()[0]

    cur.execute("""UPDATE objects
                    SET location=-1, picked_by=?  
                    WHERE location=? AND id=? AND pickable=1 AND picked_by=-1""",
                (uid, cloc, obj_id))
    db.commit()
    cur.close()
    return redirect("/")

@app.route('/drop/<obj_id>', methods=['GET'])
@requires_auth
def drop(obj_id):
    db = get_db()
    cur = db.cursor()
    auth_user = request.authorization.username

    cur.execute("""SELECT users.id, characters.location 
                        FROM users 
                        INNER JOIN characters ON users.username=? AND characters.owner=users.id""", (auth_user,))
    (uid, cloc) = cur.fetchall()[0]

    cur.execute("""UPDATE objects
                    SET location=?, picked_by=-1  
                    WHERE picked_by=? AND id=?""",
                (cloc, uid, obj_id))
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

    cur.execute("""SELECT characters.id, characters.name, U.id, characters.location
                              FROM characters 
                              INNER JOIN users U ON characters.owner = U.id AND U.username=?;""", (auth_user,))
    charac_id, cname, auth_id, charac_loc = cur.fetchall()[0]

    cur.execute("SELECT name FROM locations WHERE id = ?;", (charac_loc,))

    lname = cur.fetchall()[0][0]

    access = list()
    cur.execute("""SELECT L.name, L.id, paths.desc FROM paths
                      INNER JOIN locations L ON (paths.src = L.id AND paths.dst=? AND paths.both_ways=1) OR 
                                                (paths.dst = L.id AND paths.src=?);""",
                (charac_loc,charac_loc,))

    for row in cur.fetchall():
        access.append((row[0], row[1], row[2]))

    objects = list()
    cur.execute("SELECT id, short_desc, pickable FROM objects WHERE location=?", (charac_loc,))
    for row in cur.fetchall():
        objects.append({'id': row[0],
                        'desc': row[1],
                        'pickable': row[2]})

    people = list()
    cur.execute("SELECT name FROM characters WHERE location=? AND id!=?", (charac_loc, charac_id))
    for row in cur.fetchall():
        people.append({'name': row[0]})

    inventory = list()
    cur.execute("SELECT id, short_desc FROM objects WHERE picked_by=?", (charac_id,))
    for row in cur.fetchall():
        inventory.append({'id': row[0],
                          'desc': row[1]})

    context = {'username': auth_user,
               'characname': cname,
               'location': lname,
               'access': access,
               'objects': objects,
               'people': people,
               'inventory': inventory}

    if auth_user in ADMINS:
        context['places'] = list()
        cur.execute("SELECT * FROM locations;")
        for row in cur.fetchall():
            context['places'].append(row)
        context['characters'] = list()
        cur.execute("SELECT * FROM characters;")
        for row in cur.fetchall():
            context['characters'].append(row)
        cur.close()
        return render_template('index.tpl', **context) + render_template('admin.tpl', **context)
    else:
        cur.close()
        return render_template('index.tpl', **context)


if __name__ == '__main__':
    app.run(host='localhost', port=8088, debug=True)
