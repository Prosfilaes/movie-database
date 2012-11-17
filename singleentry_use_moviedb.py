#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

def parse_year (s):
    '''Parse a four digit year from 1878 to 2020'''
    if len (s) != 4:
        return 0
    if not str.isdigit (s):
        return 0;
    movie_year = int (s)
    if 1878 > movie_year or movie_year > 2020:
        return 0;
    return movie_year

def yn_to_bool (s):
    '''Turn a string starting with y(j) or n into a boolean'''
    if s [0:1].lower() == "n":
        return False
    elif s [0:1].lower() == "y" or s[0:1].lower() == "j":
        return True
    return None

def process_tag_list (s):
    tag_list = [t.strip () for t in s.split (",")]
    if tag_list == ['']:
        return []
    else:
        return tag_list

def report_new_tags (tag_list, prefix = ""):
    for tag in tag_list:
        cur.execute ("SELECT {0}tags.tag FROM {0}tags WHERE {0}tags.tag = {1};".format (prefix, con.escape (tag)));
        numrows = cur.rowcount
        if numrows == 0:
            print (tag + " is new in the system.")

con = None

try:
    cur_execute = print
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    dvd_name = input ("Please enter the name of the DVD (set): ");
    escaped_dvd_name = con.escape (dvd_name)
    cur.execute ("INSERT INTO dvd (dvd_id, title) VALUES (null, {});".format (escaped_dvd_name))
    dvd_id = con.insert_id ();

    dvd_tag_list = process_tag_list (input ("Please input dvd tags, comma separated: "))
    print ("DVD tags will be: ", end="")
    print (dvd_tag_list)
    report_new_tags (dvd_tag_list, "dvd_")
    for dvd_tag in dvd_tag_list:
        cur.execute ("INSERT INTO dvd_tags (dvd_id, tag) "
                     "VALUES ({}, {});".format (dvd_id, con.escape (dvd_tag)));
        
    movie_name = input ("Name of the movie, or hit enter to exit: ")
    if movie_name == "":
        sys.exit (0)
    escaped_movie_name = con.escape (movie_name)
    cur.execute ("SELECT * FROM movie WHERE movie.name = {};".format (escaped_movie_name))
    rows = cur.fetchall ()
    cur.execute ("SELECT m.movie_id, m.name, amn.name, m.year, m.is_full_length "
                 "FROM alternate_movie_names amn "
                 "INNER JOIN movie m ON amn.movie_id = m.movie_id "
                 "WHERE amn.name = {};".format (escaped_movie_name))
    rows += cur.fetchall ()
    is_existing_movie = False;

    if len (rows) > 0:
        print ("We have matching entries. Are any of the following your movie?")
        for row in rows:
            print (row)
        is_existing_movie = None
        while is_existing_movie == None:
            is_existing_movie = yn_to_bool (input ("(Y/N) :"));

    if is_existing_movie == False:
        movie_year = 0
        while (movie_year == 0):
            movie_year_str = input ("Year of the movie (1878-2020): ")
            movie_year = parse_year (movie_year_str);
        is_full_length = None;
        while (is_full_length == None):
            ifl_str = input ("Is this a full-length feature? (Y/N): ")
            is_full_length = yn_to_bool (ifl_str)

        local_tag_list = process_tag_list (input ("Please input tags, comma separated: "))
        report_new_tags (local_tag_list)
        print ("Inserting tags ", end="")
        print (local_tag_list)
        
        hs_str = input ("Have you seen this movie? (Y/N): ")
        has_seen = yn_to_bool (hs_str)

        if movie_name.startswith ("The "):
            sort_name = con.escape (movie_name [4:] + ", The")
        elif movie_name.startswith ("A "):
            sort_name = con.escape (movie_name [2:] + ", A")
        elif movie_name.startswith ("An "):
            sort_name = con.escape (movie_name [3:] + ", An")
        else:
            sort_name = con.escape (movie_name)
 
        if has_seen == None:
            cur.execute 
            ("INSERT INTO movie "
             "(movie_id, name, year, is_full_length, sort_name) "
             "VALUES (null, {}, {}, {}, {})"
             ";".format (escaped_movie_name, movie_year, 
                         is_full_length, sort_name))
        else:
            cur.execute 
            ("INSERT INTO movie "
             "(movie_id, name, year, is_full_length, have_watched, sort_name) "
             "VALUES (null, {}, {}, {}, {})"
             ";".format (escaped_movie_name, movie_year, has_watched,
                         is_full_length, sort_name))
        movie_id = con.insert_id ()
        for tag in local_tag_list:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)));
    else:
        if len (rows) == 1:
            movie_id = rows [0][0];
        else:
            movie_id_str = ""
            while (not str.isdigit (movie_id_str)):
                movie_id_str = input ("Which id? ")
                movie_id = int (movie_id_str);

        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {}"
                     ";".format (movie_id))
        old_tags_return = cur.fetchall ()
        old_tags = [];
        for otag in old_tags_return:
            old_tags.append (otag [0])
        print ("Existing tags: ", end = "")
        print (old_tags)
        local_tag_list = process_tag_list (input ("Please input tags, comma separated: "))
        report_new_tags (local_tag_list)
        tag_list = [tag for tag in local_tag_list if tag not in old_tags];
        print ("Inserting tags ", end="")
        print (tag_list)
        for tag in tag_list:
            cur.execute ("INSERT INTO tags (movie_id, tag) "
                         "VALUES ({}, {});".format (movie_id, con.escape (tag)))

    cur.execute ("INSERT INTO dvd_contents (dvd_id, movie_id) "
                 "VALUES ({}, {});".format (dvd_id, movie_id))
    con.commit ()

    print ("Successful insertion of movie for {}, dvd_id {}.".format (dvd_name, dvd_id))
    cur.execute ("SELECT m.movie_id, m.name, m.year, m.is_full_length FROM movie m "
                 "INNER JOIN dvd_contents dc ON dc.movie_id = m.movie_id "
                 "INNER JOIN dvd ON dc.dvd_id = dvd.dvd_id "
                 "WHERE dvd.dvd_id = {};".format (dvd_id))
    rows = cur.fetchall ()
    for row in rows:
        print (row)

except mdb.Error as e:

    print (e)
    sys.exit(1)

finally:

    if con:
        con.rollback ()
        con.close()
