#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
#from bottle import route, run, view, post, request, static_file, redirect, auth_basic, template
#import bottle
from flask import Flask, redirect, request, render_template
import hashlib

# Should be in config
SALT = u'yuryoujhflhsv,.sbuireveruivn rio2316+54849+62"";efqqwfrqw#$@R$EWF#C FFSDC./12213232312'
ADMINS = ['yves']


app = Flask("RPG server")

def check(user, pw):
    sha = hashlib.new('SHA256')
    sha.update((user + pw + SALT).encode('utf-8'))
    h = sha.hexdigest()
    print(h)
    db = sqlite3.connect("jdr.db")
    cur = db.cursor()
    cur.execute("SELECT username FROM users WHERE username=? AND password=?;", (user,h))
    ret = cur.fetchall();
    cur.close()
    return len(ret) > 0


@app.route('/admin/create_path', methods=['POST'])
def create_path():
    db = sqlite3.connect("jdr.db")
    auth_user = 'yves'
    if not auth_user in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    cur.execute("INSERT INTO paths (`src`, `dst`, `desc`) VALUES (?, ?, ?);",
                [request.forms["src"],
                 request.forms["dst"],
                 request.forms["desc"]])
    db.commit()
    return redirect("/")


@app.route('/admin/create_place', methods=['POST'])
def create_place():
    db = sqlite3.connect("jdr.db")
    auth_user = 'yves'
    if not auth_user in ADMINS:
        return "Teuteuteu"
    cur = db.cursor()
    cur.execute("INSERT INTO locations (`name`) VALUES (?)", [request.forms["name"]])
    db.commit()
    return redirect("/")


@app.route('/go/<direction>', methods=['GET'])
def go(direction):
    db = sqlite3.connect("jdr.db")
    # TODO: Check if legit
    cur = db.cursor()
    auth_user = 'yves'
    cur.execute("""UPDATE characters 
						SET location=?  
						WHERE characters.owner IN (SELECT Id FROM users WHERE users.username=?)""", (int(direction),auth_user))
    db.commit()
    cur.close()
    return redirect("/")


@app.route('/')
def index():
    db = sqlite3.connect("jdr.db")

    auth_user = 'yves'
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
    			          	  INNER JOIN characters ON characters.owner=? AND characters.location = paths.src;""", (auth_id,))

    for row in cur.fetchall():
        access.append((row[0], row[1], row[2]))
        print(row)

    print()
    cur.execute("""SELECT L2.name, L2.id, paths.desc
                              FROM paths
                              INNER JOIN locations L1 ON paths.dst = L1.id
                              INNER JOIN locations L2 ON paths.src = L2.id
                              INNER JOIN characters ON characters.id=? AND characters.location = paths.dst AND paths.both_ways=1;""", (charac_id,))

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
