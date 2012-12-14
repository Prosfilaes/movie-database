#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline


def _parse_year (s):
    '''Parse a four digit year from 1878 to 2020'''
    if len (s) != 4:
        return 0
    if not str.isdigit (s):
        return 0;
    movie_year = int (s)
    if 1878 > movie_year or movie_year > 2020:
        return 0;
    return movie_year

def _yn_to_bool (s):
    '''Turn a string starting with y(j) or n into a boolean'''
    if s [0:1].lower() == "n":
        return False
    elif s [0:1].lower() == "y" or s[0:1].lower() == "j":
        return True
    return None

check_length = True
con = None
cur = None
default_full_length = True
global_tag_list = []
tv_show = None

def open_database ():
    '''Open the database connection'''
    global con, cur
    with open ("password", "r") as pass_file:
        l = pass_file.readline().split()
        username = l[0]
        password = l[1]
    con = mdb.connect('localhost', username, password, 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")


def close_database ():
    con.commit ()
    con.close ()

def abort_database ():
    con.rollback ()
    con.close ()

try:
    digraph = False
    year = 2000
    open_database ()
    cur.execute ("SELECT movie_id FROM movie "
                 "NATURAL JOIN moviebacon "
                 "WHERE year > {} AND is_full_length;".format(year))
    s = cur.fetchall ()
    id_list = set([t[0] for t in s])
    if digraph:
        print ("digraph G {")
    else:
        print ("graph G {")
    print ("graph [fontsize=10];")
    print ("node [fontsize=10];")
    print ("edge [len=3];")
    #print ("size=\"32, 44\";")
    #print ("page=\"8.5, 11\";")
    for i in id_list:
        cur.execute ("SELECT name FROM movie where movie_id = {};"
                     "".format (con.escape (i)))
        name = cur.fetchone ()[0]
        # abuse of con.escape here; gross hack that doesn't work too well
        print ("n{} [ label = \"{}\" ];".format (i, con.escape(name)))
    for i in id_list:
        cur.execute ("SELECT DISTINCT a2.movie_id FROM actor a "
                     "INNER JOIN movie m ON a.movie_id = m.movie_id "
                     "INNER JOIN actor a2 ON a.person = a2.person "
                     "INNER JOIN movie m2 ON a2.movie_id = m2.movie_id "
                     "  AND m2.year > {} "
                     "  AND (m.year < m2.year OR (m.year = m2.year AND m.movie_id < m2.movie_id)) "
                     "  AND m2.is_full_length "
                     "WHERE a.movie_id = {};".format (year, i))
        ids = set([t[0] for t in cur.fetchall ()])
        for i2 in ids:
            if digraph:
                print ("n{} -> n{};".format (i, i2))
            else:
                print ("n{} -- n{};".format (i, i2))              
    print ("}")
except mdb.Error as e:
    print (e)
    sys.exit(1)
finally:
    if con:
        con.rollback ()
        con.close()
