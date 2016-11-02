#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
from bottle import route, run, view, post, request, static_file, redirect


TEMPLATE_PATH = "templates/"
db = MySQLdb.connect(host="localhost", user="yves", passwd="toto", db="jdr1")
cur = db.cursor()
cur.execute("SET NAMES 'utf8';")
cur.close()

@route('/go/<direction>', method='GET')
def go(direction):
	# TODO: Check if legit
	cur = db.cursor()
	print direction
	#cur.begin()
	cur.execute("""UPDATE characters SET location=%s WHERE id=%s""", (int(direction), 1))
	cur.execute("""SELECT * FROM characters;""")
	for r in cur.fetchall():
		print r
	db.commit()
	cur.close()
	redirect("/")

@route('/')
@view(TEMPLATE_PATH + 'index.tpl')
def index():
	cur = db.cursor()
	cur.execute("""SELECT U.username, characters.name , locations.name 
			          	  FROM characters 
			          	  INNER JOIN users U ON characters.owner = U.id 
			          	  INNER JOIN locations ON locations.id = characters.location;""")

	username, cname, lname = cur.fetchall()[0]
	s="Bienvenue {0},\n{1} se trouve en ce moment à {2}. Il a accès à:".format(username, cname, lname) 

	cur.execute("""SELECT L2.name, L2.id 
			          	  FROM paths 
			          	  INNER JOIN locations L1 ON paths.from = L1.id
			          	  INNER JOIN locations L2 ON paths.to = L2.id
			          	  INNER JOIN characters ON characters.location = paths.from
			          	  ;""")

	access = list()
	for row in cur.fetchall():
		access.append((row[0], row[1]))
	context = {'username' : username,
			   'characname' : cname,
			   'location' : lname,
			   'access' : access}
	cur.close()
	return context


if __name__ == '__main__':
    run(host='localhost', port=8080, reloader = True)
