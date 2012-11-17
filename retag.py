#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline
import moviedb

con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
cur = con.cursor()
moviedb.con = con
moviedb.cur = cur
cur.execute ("SET NAMES 'utf8'")
try:
    cur.execute ("SELECT m.movie_id, m.name, m.year FROM movie m LEFT OUTER JOIN has_been_retagged h "
                 "ON h.movie_id = m.movie_id where h.movie_id IS NULL and m.is_full_length and m.year > 1979 ORDER BY m.year, m.sort_name;")
    movie_list = cur.fetchall ()
    for movie in movie_list:
        movie_id = movie [0]
        movie_name = movie [1]
        movie_year = movie [2]

        cur.execute ("SELECT dvd.title FROM dvd INNER JOIN dvd_contents dc ON dc.dvd_id = dvd.dvd_id "
                     "WHERE dc.movie_id = {};".format (movie_id))
        dvd_list = cur.fetchall ()
        print ("{} ({}) is found on ".format (movie_name, movie_year), end = "")
        if len (dvd_list) == 1:
            print ("{}.".format (dvd_list [0][0]))
        else:
            for dvd in dvd_list [0:-1]:
                print ("\"{}\", ".format (dvd [0]), end = "")
            print ("and \"{}\".".format (dvd_list [-1][0]))
        cur.execute ("SELECT name FROM alternate_movie_names amn WHERE movie_id = {};".format (movie_id))
        other_names = [amn[0] for amn in cur.fetchall ()]
        if len (other_names) == 0:
            pass
        elif len (other_names) == 1:
            print ("AKA \"{}\".".format (other_names.pop (0)))
        else:
            print ("AKA ", end = "")
            while len (other_names) > 1:
                print ("\"{}\", ".format (other_names.pop (0)), end = "")
            print ("and \"{}\".".format (other_names.pop (0)))

        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (movie_id));
        tags = [tag[0] for tag in cur.fetchall ()]
        print ("Tagged: ", end = "")
        if len (tags) == 0:
            print ("No tags!")
        elif len (tags) == 1:
            print ("{}.".format (tags [0]))
        else:
            for tag in tags [0:-1]:
                print ("\"{}\", ".format (tag), end = "")
            print ("and \"{}\".".format (tags [-1]))

        cur.execute ("SELECT person.person FROM person WHERE person.movie_id = {};".format (movie_id))
        people = [person[0] for person in cur.fetchall ()]
        print ("Stars: ", end = "")
        if len (people) == 0:
            print ("No stars noted!")
        elif len (people) == 1:
            print ("{}.".format (people [0]))
        else:
            for person in people [0:-1]:
                print ("\"{}\", ".format (person), end = "")
            print ("and \"{}\".".format (people [-1]))
    
        tag_list = moviedb._process_tag_list (input ("Please input tags, comma separated: "))
        moviedb._report_new_tags (tag_list)
        print ("Inserting tags ", end="")
        print (tag_list)
        
        people_list = moviedb._process_tag_list (input ("Please input notable creators, comma separated: "))
        moviedb._report_new_people (people_list)
        
        hs_str = input ("Have you seen this movie? (Y/N): ")
        have_watched = moviedb._yn_to_bool (hs_str)
    
        if not have_watched == None:
            cur.execute ("UPDATE movie "
                         "SET have_watched = {} "
                         "WHERE movie_id = {};".format (have_watched, movie_id));
        for tag in tag_list:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
        for person in people_list:
            cur.execute ("INSERT INTO person (movie_id, person) "
                         "VALUES ({}, {});".format (movie_id, con.escape (person)))
        cur.execute ("INSERT INTO has_been_retagged VALUES ({});".format (movie_id))
        con.commit ()
        print ("Updated.\n")

except mdb.Error as e:

    print (e)
    sys.exit(1)

finally:

    if con:
        con.rollback ()
        con.close()
