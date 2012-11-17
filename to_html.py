#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import re

def is_full_length (b):
    if b:
        return ""
    else:
        return " (short)"

def process_name (n):
    ''' Right now this only turns & into &amp; '''
    return n.replace ('&', '&amp;');

def print_header (id_tag, name):
    print ("<h2 id=\"{}\">{}</h2>\n".format (id_tag, name))

def print_movie_table (is_full_length, watchedonly):
    if watchedonly:
        cur.execute("SELECT movie.name, movie.year FROM movie WHERE movie.is_full_length = {} "
                    "AND movie.have_watched = true "
                    "ORDER BY movie.year, movie.sort_name;".format (is_full_length))
    else:
        cur.execute("SELECT movie.name, movie.year FROM movie WHERE movie.is_full_length = {} " 
                    "ORDER BY movie.year, movie.sort_name;".format (is_full_length))
    rows = cur.fetchall()
    curr_year = 0
    curr_decade = 0
    first_year = True
    for row in rows:
        if (row [1] - (row[1] % 10)) != curr_decade:
            if not first_year: 
                print ("<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td></td></tr>")
                print ("</table>")
            else:
                first_year = False
            print ("<table>")
            curr_decade = row[1] - (row[1] % 10)
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
#    id_string = id_string.replace ("0", "zero");
#    id_string = id_string.replace ("1", "one");
#    id_string = id_string.replace ("2", "two");
#    id_string = id_string.replace ("3", "three");
#    id_string = id_string.replace ("4", "four");
#    id_string = id_string.replace ("5", "five");
#    id_string = id_string.replace ("6", "six");
#    id_string = id_string.replace ("7", "seven");
#    id_string = id_string.replace ("8", "eight");
#    id_string = id_string.replace ("9", "nine");
    return id_string;
    
con = None

try:

    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    print ('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">''')

    print ("<html>\n<head>\n<META http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
           "<title>David's Movies</title>\n</head>\n<body>"
           "<h1>David's Movies</h1>\n")
    
    tableofcontents = {"dvd":"List by DVD", 
		       "dvdbytag": "List of DVDs by tag",
		       "movie": "List by movie",
                       "yearfull": "List of full-length movies by year",
                       "yearshort": "List of shorts by year",
                       "watchedyearfull": "List of watched full-length movies by year",
                       "watchedyearshort": "List of watched shorts by year",
                       "moviesbytag": "List of movies by tag",
                       "altnames": "Alternate movie names",
                       "people": "People working on these movies",
                       "majortags": "Major tags"};
    # We can't just extract the keys, because we need the order for the table of contents at start
    toc_list = ("dvd", "dvdbytag", "movie", "yearfull", "yearshort", "watchedyearfull", 
                "watchedyearshort", "moviesbytag", "majortags", "people", "altnames")
   
    print ("<ul>")
    for short_id in toc_list:
        print ("<li><a href=\"#{}\">{}</a></li>".format (short_id, tableofcontents [short_id]))
    print ("</ul>")

    print_header ("dvd", tableofcontents ["dvd"])

    cur.execute ("SELECT dvd.dvd_id, dvd.name FROM dvd ORDER by dvd.name;")
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
        cur.execute ("SELECT movie.name, movie.year, movie.is_full_length, movie.movie_id FROM movie "
                      "INNER JOIN dvd_contents ON movie.movie_id = dvd_contents.movie_id "
                      "WHERE dvd_contents.dvd_id = {} "
                      "ORDER BY movie.is_full_length DESC, movie.sort_name, movie.year;".format (dvd[0]))
        movie_list = cur.fetchall ()
        print ("<ul>")
        if len (movie_list) == 0:
            print ("<li>ERROR: DVD has no contents!</li>")
        else:
            for movie in movie_list:
                print ("<li><a href=\"#movie{}\">{} ({})</a>{}</li>".format
                       (movie [3], process_name (movie [0]), movie[1], is_full_length (movie[2])))
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
    cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM movie "
                 "ORDER BY movie.sort_name, movie.year;")
    movie_list = cur.fetchall ()
    for movie in movie_list:
#        print ("<h3 id=\"movie{}\">{} ({}){}</h3>".format (movie[0], process_name (movie[1]), movie[2], is_full_length (movie[3])));
        print ("<p id=\"movie{}\"><b>{} ({}){}</b></p>".format (movie[0], process_name (movie[1]), movie[2], is_full_length (movie[3])));
        print ("<ul>")
        cur.execute ("SELECT dvd.name, dvd.dvd_id FROM dvd INNER JOIN dvd_contents "
                     "ON dvd.dvd_id = dvd_contents.dvd_id "
                     "WHERE dvd_contents.movie_id = {} "
                     "ORDER BY dvd.name;".format (movie[0]));
        dvd_list = cur.fetchall ()
        if len (dvd_list) == 0:
            print ("<li>ERROR: not found on any DVD!</li>")
        for dvd in dvd_list:
            print ("<li>on <i><a href=\"#dvd{}\">{}</a></i></li>".format (dvd [1], process_name (dvd[0])))
        cur.execute ("SELECT person FROM movie_people NATURAL JOIN person_name "
                     "WHERE movie_people.movie_id = {} ORDER BY person;".format (movie [0]))
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
    print_movie_table (is_full_length = True, watchedonly = False);
        
    print_header ("yearshort", tableofcontents ["yearshort"]) 
    print_movie_table (is_full_length = False, watchedonly = False);

# List of watched full-length movies by year, then shorts by year
    print_header ("watchedyearfull", tableofcontents ["watchedyearfull"]) 
    print_movie_table (is_full_length = True, watchedonly = True);
        
    print_header ("watchedyearshort", tableofcontents ["watchedyearshort"]) 
    print_movie_table (is_full_length = False, watchedonly = True);

# Movies by tag
    print_header ("moviesbytag", tableofcontents ["moviesbytag"])
    cur.execute ("SELECT tags.tag FROM tags GROUP BY tags.tag HAVING count(*) > 1 ORDER BY tags.tag;")
    tag_list = cur.fetchall ()
    for tag in tag_list:
#        print ("<h3>" + process_name (tag[0]) + "</h3>")
        print ("<p id=\"{}\"><b>{}</b></p>".format (labeltoid (tag[0], "tag"), process_name (tag[0])))
        cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM tags "
                     "INNER JOIN movie ON movie.movie_id = tags.movie_id "
                     "WHERE tags.tag = \"{}\" "
                     "ORDER BY movie.is_full_length DESC, movie.sort_name, movie.year;".format (tag[0]))
        print ("<ul>")
        movie_list = cur.fetchall ()
        for movie in movie_list:
            print ("<li><a href=\"#movie{}\">{} ({})</a>{}</li>"
                   " ".format (movie[0], process_name (movie[1]), movie [2], is_full_length (movie [3])))
        print ("</ul>")

# Movies by major tag
    print_header ("majortags", tableofcontents ["majortags"])
    cur.execute ("select COUNT(*), tag from tags GROUP BY tag HAVING count(*) > 3 ORDER BY count(*) DESC, tag;")
    rows = cur.fetchall ()
    print ("<ul>")
    for row in rows:
        print ("<li>{}: <a href=\"#{}\">{}</a></li>".format(row[1], labeltoid (row [1], "tag"), row[0]))
    print ("</ul>")

# People
    print_header ("people", tableofcontents ["people"])
    cur.execute ("CREATE TEMPORARY TABLE people_count "
                 "(arbitrary smallint(5) unsigned NOT NULL AUTO_INCREMENT, "
                 "movie_id smallint(5) unsigned, "
                 "person_id int(10) unsigned, "
                 "person varchar(180) NOT NULL, PRIMARY KEY (arbitrary)) DEFAULT CHARSET=utf8mb4;")
#    print ("<p>1</p>")
    cur.execute ("INSERT INTO people_count "
                 "(SELECT null, null, person_id, person FROM person_name p "
                 "NATURAL JOIN movie_people "
                 "NATURAL JOIN tv_show ts "
                 "GROUP BY person, ts.name, season_num);")
#    print ("<p>2</p>")
    cur.execute ("INSERT INTO people_count "
                 "(SELECT null, movie_id, person_id, person FROM person_name "
                 "NATURAL JOIN movie_people "
                 "NATURAL JOIN movie m "
                 "WHERE movie_id NOT IN (SELECT movie_id FROM tv_show));");
#    print ("<p>3</p>")
    cur.execute ("select COUNT(*), person, person_id from people_count GROUP BY person HAVING count(*) > 5 "
                 "ORDER BY count(*) DESC, person;")
#    print ("<p>4</p>");
    rows = cur.fetchall ()
    for row in rows:
        print ("<p id=\"{}\">{} ({} entries)</p>".format(labeltoid (row[1], "person"), row [1], row[0]))
        cur.execute ('SELECT movie_id, name, year FROM movie '
                     'NATURAL JOIN movie_people '
                     'WHERE person_id = {0} AND movie_id NOT IN (SELECT movie_id FROM tv_show) '
                     'ORDER BY sort_name, year;'.format (row [2]))
        movies = cur.fetchall ()
        cur.execute ('select CONCAT("episodes from ", ts.name, " season ", ts.season_num), MIN(m.year) '
                     'FROM movie m '
                     'INNER JOIN tv_show ts on ts.movie_id = m.movie_id '
                     'INNER JOIN movie_people mp ON mp.movie_id = m.movie_id '
                     'WHERE mp.person_id = {0} GROUP BY ts.name, ts.season_num'
                     ';'.format (row [2]))
        tv_shows = cur.fetchall ()
        print ("<ul>")
        for movie in movies:
# XXX: We need to create and link to a section detailing work in each episode of a TV series 
# The Current links are broken.
            print ("<li>Found in <a href=\"#movie{}\">{} ({})</a>".format (movie[0], movie[1], movie[2]))
        for tv_show in tv_shows:
            print ("<li>Found in {} ({})".format (tv_show [0], tv_show [1]))
        print ("</ul>")
#    print ("</ul>")

# Alternate Movie Names
    print_header ("altnames", tableofcontents ["altnames"])   
    cur.execute("SELECT amn.name, m.name, m.year, m.movie_id FROM alternate_movie_names amn "
                "INNER JOIN movie m ON amn.movie_id = m.movie_id "
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

