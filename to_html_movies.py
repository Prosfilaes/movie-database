#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import re

def process_name (n):
    ''' Right now this only turns & into &amp; '''
    return n.replace ('&', '&amp;');

def print_header (id_tag, name):
    print ("<h2 id=\"{}\">{}</h2>\n".format (id_tag, name))

def print_movie_table (watchedonly):
    if watchedonly:
        cur.execute("SELECT movie.name, movie.year FROM movie WHERE movie.is_full_length = TRUE "
                    "AND movie.have_watched = true "
                    "ORDER BY movie.year, movie.sort_name;")
    else:
        cur.execute("SELECT movie.name, movie.year FROM movie WHERE movie.is_full_length = TRUE " 
                    "ORDER BY movie.year, movie.sort_name;")
    rows = cur.fetchall()
    curr_year = 0
    print ("<table>")
    for row in rows:
        if row [1] != curr_year:
            print ("<tr><td>{}</td><td>{}</td></tr>".format (row [1], process_name (row [0])))
            curr_year = row[1]
        else:
            print ("<tr><td></td><td>{}</td></tr>".format (process_name (row [0])))
    print ("<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td></td></tr>")
    print ("</table>")

def labeltoid (tag, labletype):
    expanded_tag = re.split ('[^a-z0-9]', tag.lower())
    id_string = labletype + "_"
    for word in expanded_tag:
        id_string = id_string + word;
    return id_string;
    
con = None

try:

    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    print ('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">''')

    print ("<html>\n<head>\n<META http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
           "<title>David's Movies (full-length)</title>\n</head>\n<body>"
           "<h1>David's Movies (full-length)</h1>\n")
    
    tableofcontents = {"dvd":"List by DVD", 
		       "dvdbytag": "List of DVDs by tag",
		       "movie": "List by movie",
                       "yearfull": "List of full-length movies by year",
                       "watchedyearfull": "List of watched full-length movies by year",
                       "moviesbytag": "List of movies by tag",
                       "altnames": "Alternate movie names",
                       "people": "People working on these movies",
                       "majortags": "Major tags"};
    # We can't just extract the keys, because we need the order for the table of contents at start
    toc_list = ("dvd", "dvdbytag", "movie", "yearfull", "watchedyearfull", 
                "moviesbytag", "majortags", "people", "altnames")
    
    print ("<ul>")
    for short_id in toc_list:
        print ("<li><a href=\"#{}\">{}</a></li>".format (short_id, tableofcontents [short_id]))
    print ("</ul>")

    print_header ("dvd", tableofcontents ["dvd"])

    cur.execute ("SELECT DISTINCT dvd.dvd_id, dvd.name FROM dvd "
                 "INNER JOIN dvd_contents dc ON dc.dvd_id = dvd.dvd_id "
                 "INNER JOIN movie m ON m.movie_id = dc.movie_id "
                 "WHERE m.is_full_length = TRUE ORDER BY dvd.name;")
    dvd_list = cur.fetchall ()
    for dvd in dvd_list:
#        print ("<h3 id=\"dvd{}\">{}</h3>".format (dvd[0], process_name (dvd[1])))
        print ("<p id=\"dvd{}\"><b>{}</b></p>".format (dvd[0], process_name (dvd[1])))
#        print ("<h3>{}</h3>".format (process_name (dvd[1])))  
        cur.execute ("SELECT tag FROM dvd_tags where dvd_id = {};".format (dvd[0]));
        tags_list = cur.fetchall ()
        if len (tags_list) > 0:
            print ("<p>Tagged ", end = "")
            for tag in tags_list:
                if tag == tags_list [-1]:
                    print (tag [0], end = "</p>\n")
                else:
                    print (tag[0], end = ", ")
        cur.execute ("SELECT movie.name, movie.year, movie.movie_id FROM movie "
                      "INNER JOIN dvd_contents ON movie.movie_id = dvd_contents.movie_id "
                      "WHERE dvd_contents.dvd_id = {} AND movie.is_full_length "
                      "ORDER BY movie.sort_name, movie.year;".format (dvd[0]))
        movie_list = cur.fetchall ()
        print ("<ul>")
        if len (movie_list) == 0:
            print ("<li>ERROR: DVD has no contents!</li>")
        else:
            for movie in movie_list:
                print ("<li><a href=\"#movie{}\">{} ({})</a></li>".format
                       (movie [2], process_name (movie [0]), movie[1]))
        print ("</ul>")
        
# DVDs by tag
    print_header ("dvdbytag", tableofcontents ["dvdbytag"])
    cur.execute ("SELECT dvd_tags.tag FROM dvd_tags GROUP BY dvd_tags.tag HAVING count(*) > 1 ORDER BY dvd_tags.tag;")
    tag_list = cur.fetchall ()
    for tag in tag_list:
        cur.execute ("SELECT dvd.dvd_id, dvd.name FROM dvd_tags INNER JOIN dvd "
                     "ON dvd.dvd_id = dvd_tags.dvd_id "
                     "WHERE dvd_tags.tag = \"{}\" ORDER BY dvd.name;".format (tag[0]))
        dvd_list = cur.fetchall ()
        print ("<p><b>" + process_name (tag[0]) + "</b></p>")
        print ("<ul>")
        for dvd in dvd_list:
            print ("<li><a href=\"#dvd{}\"><i>{}</i></a></li>".format (dvd[0], process_name (dvd[1])))
        print ("</ul>")
        
# List by Movie
    curr_movie_id = 0;
    inside_dvd_list = False;
    dvd_omitted = False;
    print_header ("movie", tableofcontents ["movie"])
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year FROM movie "
                 "WHERE movie.is_full_length "
                 "ORDER BY movie.sort_name, movie.year;")
    movie_list = cur.fetchall ()
    for movie in movie_list:
#        print ("<h3 id=\"movie{}\">{} ({}){}</h3>".format (movie[0], process_name (movie[1]), movie[2], is_full_length (movie[3])));
        print ("<p id=\"movie{}\"><b>{} ({})</b></p>".format (movie[0], process_name (movie[1]), movie[2]));
        print ("<ul>")
        cur.execute ("SELECT dvd.name, dvd.dvd_id FROM dvd "
                     "INNER JOIN dvd_contents ON dvd.dvd_id = dvd_contents.dvd_id "
                     "WHERE dvd_contents.movie_id = {} "
                     "ORDER BY dvd.name;".format (movie[0]));
        dvd_list = cur.fetchall ()
        if len (dvd_list) == 0:
            print ("<li>ERROR: not found on any DVD!</li>")
        for dvd in dvd_list:
            print ("<li>on <i><a href=\"#dvd{}\">{}</a></i></li>".format (dvd [1], process_name (dvd[0])))
        cur.execute ("SELECT person.name FROM person WHERE person.movie_id = {} ORDER BY person.name;".format (movie [0]))
        person_list = cur.fetchall ()
        if len (person_list) > 0:
            print ("<li>starring ", end="")
            first = True;
            for person in person_list:
                if first:
                    print (process_name (person [0]), end = "")
                    first = False;
                else:
                    print (", " + process_name (person [0]), end = "")
            print ("</li>")
        cur.execute ("SELECT tags.tag FROM tags WHERE tags.movie_id = {} ORDER BY tags.tag;".format (movie [0]))
        tag_list = cur.fetchall ()
        if len (tag_list) > 0:
            print ("<li>tagged ", end = "")
            first = True;
            for tag in tag_list:
                if first:
                    print (process_name (tag[0]), end = "")
                    first = False;
                else:
                    print (", " + process_name (tag[0]), end = "");
            print ("</li>")
        cur.execute ("SELECT amn.name FROM alternate_movie_names amn WHERE amn.movie_id = {} ORDER BY amn.name;".format (movie [0]))
        amn_list = cur.fetchall ()
        for amn in amn_list:
            print ("<li>AKA: {}</li>".format (process_name (amn [0])))
        print ("</ul>")

# List of full-length movies by year, then shorts by year
    print_header ("yearfull", tableofcontents ["yearfull"]) 
    print_movie_table (watchedonly = False);

# List of watched full-length movies by year, then shorts by year
    print_header ("watchedyearfull", tableofcontents ["watchedyearfull"]) 
    print_movie_table (watchedonly = True);

# Movies by tag
    print_header ("moviesbytag", tableofcontents ["moviesbytag"])
    cur.execute ("SELECT tags.tag FROM tags "
                 "INNER JOIN movie ON tags.movie_id = movie.movie_id WHERE movie.is_full_length "
                 "GROUP BY tags.tag HAVING count(*) > 1 ORDER BY tags.tag;")
    tag_list = cur.fetchall ()
    for tag in tag_list:
#        print ("<h3>" + process_name (tag[0]) + "</h3>")
        print ("<p id=\"{}\"><b>{}</b></p>".format (labeltoid (tag[0], "tag"), process_name (tag[0])))
        cur.execute ("SELECT movie.movie_id, movie.name, movie.year FROM tags "
                     "INNER JOIN movie ON movie.movie_id = tags.movie_id "
                     "WHERE tags.tag = \"{}\" AND movie.is_full_length "
                     "ORDER BY movie.sort_name, movie.year;".format (tag[0]))
        print ("<ul>")
        movie_list = cur.fetchall ()
        for movie in movie_list:
            print ("<li><a href=\"#movie{}\">{} ({})</a></li>"
                   " ".format (movie[0], process_name (movie[1]), movie [2]))
        print ("</ul>")

# Movies by major tag
    print_header ("majortags", tableofcontents ["majortags"])
    cur.execute ("select COUNT(*), tag FROM tags "
                 "INNER JOIN movie ON tags.movie_id = movie.movie_id WHERE movie.is_full_length "
                 "GROUP BY tag HAVING count(*) > 3 ORDER BY count(*) DESC, tag;")
    rows = cur.fetchall ()
    print ("<ul>")
    for row in rows:
        print ("<li>{}: <a href=\"#{}\">{}</a></li>".format(row[1], labeltoid (row [1], "tag"), row[0]))
    print ("</ul>")

# People
    print_header ("people", tableofcontents ["people"])
    cur.execute ("select COUNT(*), person.name FROM person "
                 "INNER JOIN movie ON person.movie_id = movie.movie_id WHERE movie.is_full_length "                 
                 "GROUP BY person.name HAVING count(*) > 1 ORDER BY count(*) DESC, name;")
    rows = cur.fetchall ()
    for row in rows:
        print ("<p id=\"{}\">{} ({} entries)</p>".format(labeltoid (row[1], "person"), row [1], row[0]))
        cur.execute ("select m.movie_id, m.name, m.year FROM movie m INNER JOIN person p ON p.movie_id = m.movie_id "
                     "WHERE p.name = {} AND m.is_full_length ORDER BY m.year, m.sort_name;".format(con.escape (row [1])))
        movies = cur.fetchall ()
        print ("<ul>")
        for movie in movies:
            print ("<li>Found in <a href=\"#movie{}\">{} ({})</a>".format (movie[0], movie[1], movie[2]))
        print ("</ul>")
#    print ("</ul>")

# Alternate Movie Names
    print_header ("altnames", tableofcontents ["altnames"])   
    cur.execute("SELECT amn.name, m.name, m.year, m.movie_id FROM alternate_movie_names amn "
                "INNER JOIN movie m ON amn.movie_id = m.movie_id "
                "WHERE m.is_full_length "
                "ORDER BY amn.name, m.sort_name, m.year;")
    rows = cur.fetchall()
    print ("<ul>")
    for row in rows:
        print ("<li>{}: see <a href=\"#movie{}\"><i>{}</i> ({})</a></li>".format
               (process_name (row [0]), row[3], process_name (row[1]), row[2]))
    print ("</ul>\n")

    print ('''<p><a href="http://validator.w3.org/check?uri=referer">''' 
           '''<img src="http://www.w3.org/Icons/valid-html401" ''' 
           '''alt="Valid HTML 4.01 Strict" height="31" width="88"></a></p>''')
    print ("</body>\n</html>")
    
    # This should be a no-op. Include here anyway.
    con.rollback ()    
    
except mdb.Error as e:
  
    print (e)
    sys.exit(1)
    
finally:    
        
    if con:
        con.rollback ()
        con.close()

