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

def _process_tag_list (s):
    tag_list = [t.strip () for t in s.split (",")]
    if tag_list == ['']:
        return []
    else:
        return tag_list

def _report_new_tags (tag_list, prefix = ""):
    for tag in tag_list:
        cur.execute ("SELECT {0}tags.tag FROM {0}tags "
                     "WHERE {0}tags.tag = {1};".format (prefix, con.escape (tag)));
        numrows = cur.rowcount
        if numrows == 0:
            print (tag + " is new in the system.")

def _report_new_people (people_list):
    for person in people_list:
        cur.execute ("SELECT person.person FROM person "
                     "WHERE person.person = {};".format (con.escape (person)));
        numrows = cur.rowcount
        if numrows == 0:
            print (person + " is new in the system.")

check_length = True
con = None
cur = None
default_full_length = True
global_tag_list = []

def open ():
    '''Open the database connection'''
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

def new_dvd ():
    '''Create a new dvd in the system, returning the dvd_id'''
    dvd_name = input ("Please enter the name of the DVD (set): ")
    escaped_dvd_name = con.escape (dvd_name)
    cur.execute ("INSERT INTO dvd (dvd_id, title) VALUES (null, {});".format (escaped_dvd_name))
    dvd_id = con.insert_id ()
    dvd_tag_list = _process_tag_list (input ("Please input dvd tags, comma separated: "))
    print ("DVD tags will be: ", end = "")
    print (dvd_tag_list)
    _report_new_tags (dvd_tag_list, "dvd_")
    for dvd_tag in dvd_tag_list:
        cur.execute ("INSERT INTO dvd_tags (dvd_id, tag) "
                     "VALUES ({}, {});".format (dvd_id, con.escape (dvd_tag)))
    return dvd_id

def preload_movie_values ():
    '''Ask questions up front, and remember the answer for later movies'''
    global check_length, default_full_length, global_tag_list
    while (check_length == None):
        check_length_str = input ("Are any of these shorts? (Y/N): ")
        check_length = _yn_to_bool (check_length_str);
        if check_length == None:
            print ("Please answer y or n.")
    if check_length:
        all_shorts = None
        while (all_shorts == None):
            all_shorts = _yn_to_bool (input ("Are all of these shorts? (Y/N): "))
            if all_shorts:
                check_length = False
                default_full_length = False;
    global_tag_list = _process_tag_list (input ("Please input global tags, comma separated: "))
    print ("Global tags will be: ", end="")
    print (global_tag_list)
    _report_new_tags (global_tag_list)

def input_one_movie (dvd_id):
    movie_name = input ("Name of the movie, or hit enter to exit: ")
    if movie_name == "":
        return;
    escaped_movie_name = con.escape (movie_name)
    cur.execute ("SELECT iml.name, iml.year FROM imdb_movie_list iml WHERE iml.name = {};".format (escaped_movie_name));
    rows = cur.fetchall ()
    if len (rows) > 0:
        print ("The IMDB has the following matches:");
        for row in rows: 
            print (row)
    cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
    rows = cur.fetchall ()
    cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                 "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                 "WHERE amn.name = {};".format (escaped_movie_name))
    rows += cur.fetchall ()
    is_existing_movie = False;
    
    if len (rows) > 0:
        print ("We have matching entries. Are any of the following your movie?")
        for row in rows:
            print (row)
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = _yn_to_bool (input ("(Y/N) :"));
        if is_existing_movie:
            if len (rows) == 1:
                movie_id = rows [0][0];
            else:
                movie_id_str = ""
                while (not str.isdigit (movie_id_str)):
                    movie_id_str = input ("Which id? ")
                    movie_id = int (movie_id_str)
    if not is_existing_movie:
        movie_year = 0
        while (movie_year == 0):
            movie_year_str = input ("Year of the movie (1878-2020): ")
            movie_year = _parse_year (movie_year_str);
        if check_length:
            is_full_length = None;
            while (is_full_length == None):
                ifl_str = input ("Is this a full-length feature? (Y/N): ")
                is_full_length = _yn_to_bool (ifl_str)
                if is_full_length == None:
                    print ("Please answer y or n.")
        else:
            is_full_length = default_full_length;

        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        tag_list = global_tag_list + local_tag_list;
        print ("Inserting tags ", end="")
        print (tag_list)
        
        people_list = _process_tag_list (input ("Please input notable creators, comma separated: "))
        _report_new_people (people_list)
        
        hs_str = input ("Have you seen this movie? (Y/N): ")
        have_watched = _yn_to_bool (hs_str)
          
        if movie_name [0:4] == "The ":
            sort_name = con.escape (movie_name [4:] + ", The")
        elif movie_name [0:2] == "A ":
            sort_name = con.escape (movie_name [2:] + ", A")
        elif movie_name [0:3] == "An ":
            sort_name = con.escape (movie_name [3:] + ", An")
        else:
            sort_name = con.escape (movie_name)

        if have_watched == None:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, sort_name) "
                         "VALUES (null, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, 
                                     is_full_length, sort_name))
        else:
            cur.execute ("INSERT INTO movie "
                         "(movie_id, name, year, is_full_length, have_watched, sort_name) "
                         "VALUES (null, {}, {}, {}, {}, {})"
                         ";".format (escaped_movie_name, movie_year, is_full_length,
                                     have_watched, sort_name))

        movie_id = con.insert_id ()
        for tag in tag_list:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
        for person in people_list:
            cur.execute ("INSERT INTO person (movie_id, person) "
                         "VALUES ({}, {});".format (movie_id, con.escape (person)))
    else:
        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (movie_id))
        old_tags_return = cur.fetchall ()
        old_tags = [otag [0] for otag in old_tags_return];
        print ("Existing tags: ", end = "")
        print (old_tags)
        local_tag_list = _process_tag_list (input ("Please input tags, comma separated: "))
        _report_new_tags (local_tag_list)
        all_tag_list = global_tag_list + local_tag_list
        tag_list = [tag for tag in all_tag_list if tag not in old_tags]
        print ("Inserting tags ", end="")
        print (tag_list)
        for tag in tag_list:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))
        cur.execute ("SELECT person.person FROM person WHERE person.movie_id = {};".format (movie_id))
        old_people_return = cur.fetchall ()
        old_people = [opeop [0] for opeop in old_people_return]
        print ("Existing creators: ", end = "")
        print (old_people)
        local_people_list = _process_tag_list (input ("Please input notable creators, comma separated: "))
        _report_new_people (local_people_list)
        people_list = [person for person in local_people_list if person not in old_people]
        for person in people_list:
            cur.execute ("INSERT INTO person (movie_id, person) "
                         "VALUES ({}, {});".format (movie_id, con.escape (person)))

    cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                 "VALUES ({}, {});".format (dvd_id, movie_id))
    cur.execute ("SELECT * FROM has_been_retagged WHERE movie_id = {};".format (movie_id));
    if cur.rowcount == 0:
        cur.execute ("INSERT INTO has_been_retagged VALUES ({});".format (movie_id));
    return movie_id;

def close_dvd (dvd_id):
    cur.execute ("SELECT dvd.title FROM dvd WHERE dvd.dvd_id = {};".format (dvd_id))
    dvd_name = cur.fetchone ()[0]
    print ("Successful insertion of movies for {}, dvd_id {}.".format (dvd_name, dvd_id))
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM movie "
                 "INNER JOIN dvd_contents ON dvd_contents.movie_id = movie.movie_id "
                 "INNER JOIN dvd ON dvd_contents.dvd_id = dvd.dvd_id WHERE dvd.dvd_id = {};".format (dvd_id))
    rows = cur.fetchall ()
    for row in rows:
        print (row)

def close_database ():
    con.commit ()
    con.close ()

def abort_database ():
    con.rollback ()
    con.close ()

def display_dvd (dvd_id):
    cur.execute ("SELECT dvd.title from dvd WHERE dvd.dvd_id = {}"
                 ";".format (dvd_id))
    rows = cur.fetchall ()
    for row in rows:
        print (row[0])

def display_movie (movie_id):
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.sort_name, "
                 "movie.is_full_length, movie.have_watched "
                 "FROM movie "
                 "WHERE movie.movie_id = {};".format (movie_id))
    row = cur.fetchone ()
    print ("{} ({}) (ID: {}) (Sorted as {})".format (row[1], row[2], row[0], row[3]))
    print ("Full length: {}; Has been watched: {}".format (row[4], row[5]))
    cur.execute ("SELECT dvd.title FROM dvd "
                 "INNER JOIN dvd_contents dc ON dc.dvd_id = dvd.dvd_id "
                 "WHERE dc.movie_id = {};".format (row [0]))
    rows = cur.fetchall ()
    DVDs_list = [x[0] for x in rows]
    print ("On DVDs: {}".format (DVDs_list))
    cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {};".format (row[0]))
    rows = cur.fetchall ()
    tags_list = [x[0] for x in rows]
    print ("Tagged: {}".format (tags_list))

def get_movie_id ():
    while (True):
        movie_name = input ("Name of the movie, or hit enter to exit: ")
        if movie_name == "":
            actually_quit = input (
                "If you don't want to exit, type no; any other key to continue. ")
            if actually_quit [0:1].lower() == "n":
                continue
            else:
                return
        escaped_movie_name = con.escape (movie_name)
        cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
        rows = cur.fetchall ()
        cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                     "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                     "WHERE amn.name = {};".format (escaped_movie_name))
        rows += cur.fetchall ()
        is_existing_movie = False;
        if len (rows) == 0:
            escaped_move_name = con.escape (movie_name);
            cur.execute ("SELECT * FROM movie WHERE movie.name "
                         "LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
            rows = cur.fetchall ()
            cur.execute ("SELECT movie.movie_id, movie.name, amn.name, movie.year, movie.is_full_length "
                         "FROM alternate_movie_names amn INNER JOIN movie ON amn.movie_id = movie.movie_id "
                         "WHERE amn.name LIKE CONCAT ('%', {}, '%');".format (escaped_movie_name))
            rows += cur.fetchall ()
        if len (rows) == 0:
            print ("No matching entries found. Please try again.");
            continue;
        if len (rows) == 1:
            print (rows[0])
            is_existing_movie = None
            while is_existing_movie == None:
                is_existing_movie = _yn_to_bool (input ("Is this your movie? (Y/N) "));
            if not is_existing_movie:
                continue;
            movie_id = rows [0][0];
        else:
            print ("We have matching entries. Are any of the following your movie?")
            for row in rows:
                print (row)
            is_existing_movie = None
            while is_existing_movie == None:
                is_existing_movie = _yn_to_bool (input ("(Y/N): "));
            if not is_existing_movie:
                continue;
            movie_id_str = ""
            while (not str.isdigit (movie_id_str)):
                movie_id_str = input ("Which id? ")
            movie_id = int (movie_id_str);
        if movie_id in [movie[0] for movie in rows]:
            return movie_id

def markwatched (movie_id):
    cur.execute ("UPDATE movie SET have_watched = true WHERE movie_id = {};".format (movie_id))


#except mdb.Error as e:
#
#    print (e)
#    sys.exit(1)
#
#finally:
#
#    if con:
#        con.rollback ()
#        con.close()
