#!/usr/bin/python3
import re
import pymysql as mdb
import sys

con = None
try:
	con = mdb.connect ('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
	cur = con.cursor ()
	cur.execute ("SET NAMES 'utf8'")

	ml = open ("short_movie_list")
	parens = set ()
	for r in ml:
		line = [f.rstrip () for f in r.split ("\t") if f != ""]
		year = line [1]
		if not str.isdigit (year):
			continue
		splits = re.split (r'\(\d\d\d\d/?I?I?I?I?V?\)', line[0])
#		print (splits[0], year)
		cur.execute ("INSERT INTO imdb_movie_list VALUES ({}, {});".format (con.escape (splits[0]), year))
	con.commit ()

except mdb.Error as e:
	print (e)
	sys.exit (1)
finally:
	if con:
		con.rollback ()
		con.close ()
