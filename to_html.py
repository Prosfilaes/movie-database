#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mysql.connector as mdb
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

def print_header (id_tag, title):
    print ("<h2 id=\"{}\">{}</h2>\n".format (id_tag, title))

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

def where (collection):
    if collection == "complete":
        return " 1 "
    elif collection == "full length":
        return "movie.is_full_length = 1 "
    elif collection == "short":
        return "movie.is_full_length = 0 "
    elif collection == "short no TV":
        return "movie.movie_id NOT IN (SELECT movie_id FROM tv_show) "
    elif collection == "TV":
        return "movie.movie_id IN (SELECT movie_id FROM tv_show) "
    elif collection == "watched fl":
        return "movie.is_full_length = 1 and movie.have_watched "
    else:
        raise missing_collection

# collection = "complete", "full length", "short", "short no TV", "watched fl" or "TV"
def printsection (section_label, collection = "full"):
    print_header (section_label, tableofcontents[section_label])
    where_clause = where (collection)
    if section_label == "dvd":
        # DVDs
        cur.execute ("SELECT dvd.dvd_id, dvd.name FROM dvd ORDER by dvd.name;")
        dvd_list = cur.fetchall ()
        for dvd in dvd_list:
            cur.execute (("SELECT movie.name, movie.year, movie.is_full_length, movie.movie_id FROM movie "
                          "INNER JOIN dvd_contents ON movie.movie_id = dvd_contents.movie_id "
                          "WHERE dvd_contents.dvd_id = {} AND " + where_clause +
                          "ORDER BY movie.is_full_length DESC, movie.sort_name, movie.year;").format (dvd[0]))
            movie_list = cur.fetchall ()
            if len (movie_list) == 0:
                continue
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

            print ("<ul>")
            for movie in movie_list:
                print ("<li><a href=\"#movie{}\">{} ({})</a>{}</li>".format
                      (movie [3], process_name (movie [0]), movie[1], is_full_length (movie[2])))
            print ("</ul>")
    elif section_label == "dvdbytag":
    # DVDs by tag
        cur.execute ("SELECT dvd_tags.tag FROM dvd_tags "
                     "WHERE dvd_tags.dvd_id IN (select dvd_id FROM dc_dvd NATURAL JOIN movie WHERE " + where_clause + ") "
                     "GROUP BY dvd_tags.tag HAVING count(*) > 1 ORDER BY dvd_tags.tag;")
        tag_list = cur.fetchall ()
        for tag in tag_list:
            cur.execute (("SELECT DISTINCT dvd.dvd_id, dvd.name FROM dvd_tags INNER JOIN dvd "
                         "ON dvd.dvd_id = dvd_tags.dvd_id "
                         "WHERE dvd_tags.tag = \"{}\" AND dvd_tags.dvd_id IN "
                          "(select dvd_id FROM dc_dvd NATURAL JOIN movie WHERE "
                          + where_clause + ") " + 
                          "ORDER BY dvd.name;").format (tag[0]))
            dvd_list = cur.fetchall ()
            print ("<p><b>" + process_name (tag[0]) + "</b></p>")
            print ("<ul>")
            for dvd in dvd_list:
                print ("<li><a href=\"#dvd{}\"><i>{}</i></a></li>".format (dvd[0], process_name (dvd[1])))
            print ("</ul>")
    elif section_label == "movie":
    # List by Movie
        curr_movie_id = 0;
        inside_dvd_list = False;
        dvd_omitted = False;
        cur.execute ("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM movie " 
                     "WHERE " + where_clause +
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
            cur.execute ("SELECT person FROM director WHERE movie_id = {} ORDER BY person;".format (movie[0]))
            director_list = cur.fetchall ()
            if len (director_list) > 0:
                print ("<li>directed by ", end="")
                first = True;
                for person in director_list:
                    if first:
                        print (process_name (person [0]), end = "")
                        first = False;
                    else:
                        print (", " + process_name (person [0]), end = "")
                print ("</li>")
            cur.execute ("SELECT person FROM actor WHERE movie_id = {} ORDER BY person;".format (movie [0]))
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
#XXX: Need to be written to use collections
# List of full-length movies by year, then shorts by year
    elif section_label == "yearfull":
        print_movie_table (is_full_length = True, watchedonly = False);
    elif section_label == "yearshort":
        print_movie_table (is_full_length = False, watchedonly = False);

# List of watched full-length movies by year, then shorts by year
    elif section_label == "watchedyearfull":
        print_movie_table (is_full_length = True, watchedonly = True);
    elif section_label == "watchedyearshort":
        print_movie_table (is_full_length = False, watchedonly = True);

# Movies by tag
    elif section_label == "moviesbytag":
        cur.execute ("SELECT tags.tag FROM tags NATURAL JOIN movie " +
                     "WHERE " + where_clause +
                     "GROUP BY tags.tag HAVING count(*) > 1 ORDER BY tags.tag;")
        tag_list = cur.fetchall ()
        for tag in tag_list:
#        print ("<h3>" + process_name (tag[0]) + "</h3>")
            # SQL injection problems, neutered only by the fact that it's our tags
            print ("<p id=\"{}\"><b>{}</b></p>".format (labeltoid (tag[0], "tag"), process_name (tag[0])))
            cur.execute (("SELECT movie.movie_id, movie.name, movie.year, movie.is_full_length FROM tags "
                         "INNER JOIN movie ON movie.movie_id = tags.movie_id "
                         "WHERE tags.tag = \"{}\" AND " + where_clause +
                         "ORDER BY movie.is_full_length DESC, movie.sort_name, movie.year;").format (tag[0]))
            print ("<ul>")
            movie_list = cur.fetchall ()
            for movie in movie_list:
                print ("<li><a href=\"#movie{}\">{} ({})</a>{}</li>"
                       " ".format (movie[0], process_name (movie[1]), movie [2], is_full_length (movie [3])))
            print ("</ul>")

# Movies by major tag
    elif section_label == "majortags":
        cur.execute ("select COUNT(*), tag from tags NATURAL JOIN movie "
                     "WHERE " + where_clause +
                     "GROUP BY tag HAVING count(*) > 3 ORDER BY count(*) DESC, tag;")
        rows = cur.fetchall ()
        print ("<ul>")
        for row in rows:
            print ("<li>{}: <a href=\"#{}\">{}</a></li>".format(row[1], labeltoid (row [1], "tag"), row[0]))
        print ("</ul>")
# Director
    elif section_label == "directors":
        cur.execute ("select COUNT(*), person from director NATURAL JOIN movie "
                     "WHERE " + where_clause +
                     "GROUP BY person HAVING count(*) > 1 ORDER BY count(*) DESC, person;")
        rows = cur.fetchall ()
        for row in rows:
            print ("<p id=\"{}\">{} ({} entries)</p>".format(labeltoid (row[1], "director"), row [1], row[0]))
            cur.execute (("select movie.movie_id, movie.name, movie.year FROM movie INNER JOIN director p ON p.movie_id = movie.movie_id "
                         "WHERE p.person = %(row)s AND " + where_clause + "ORDER BY movie.year, movie.sort_name;"), {"row": row [1]})
            movies = cur.fetchall ()
            print ("<ul>")
            for movie in movies:
                print ("<li>Directed <a href=\"#movie{}\">{} ({})</a>".format (movie[0], movie[1], movie[2]))
            print ("</ul>")
# Actor
    elif section_label == "actors":
        cur.execute ("select COUNT(*), person from actor NATURAL JOIN movie "
                     "WHERE " + where_clause +
                     "GROUP BY person HAVING count(*) > 1 ORDER BY count(*) DESC, person;")
        rows = cur.fetchall ()
        for row in rows:
            print ("<p id=\"{}\">{} ({} entries)</p>".format(labeltoid (row[1], "actor"), row [1], row[0]))
            cur.execute (("select movie.movie_id, movie.name, movie.year FROM movie INNER JOIN actor p ON p.movie_id = movie.movie_id "
                         "WHERE p.person = %(row)s AND " + where_clause + "ORDER BY movie.year, movie.sort_name;"), {"row": row [1]})
            movies = cur.fetchall ()
            print ("<ul>")
            for movie in movies:
                print ("<li>Found in <a href=\"#movie{}\">{} ({})</a>".format (movie[0], movie[1], movie[2]))
            print ("</ul>")
#    print ("</ul>")

# Alternate Movie Names
    elif section_label == "altnames":  
        cur.execute("SELECT amn.name, movie.name, movie.year, movie.movie_id FROM alternate_movie_names amn "
                    "INNER JOIN movie ON amn.movie_id = movie.movie_id "
                    "WHERE " + where_clause +
                    "ORDER BY amn.name, movie.sort_name, movie.year;")
        rows = cur.fetchall()
        print ("<ul>")
        for row in rows:
            print ("<li>{}: see <a href=\"#movie{}\"><i>{}</i> ({})</a></li>".format
                   (process_name (row [0]), row[3], process_name (row[1]), row[2]))
        print ("</ul>\n")
# TV show
    #elif section_label == "tv_show":
    #    cur.exect
    # else ... any sort of error should have been raised when we poked into the dictionary
    return

con = None

try:

    with open ("password", "r") as pass_file:
        l = pass_file.readline().split()
        username = l[0]
        password = l[1]
    con = mdb.connect(user=username, password=password, database='DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    
    profile = "full length"
    
    tableofcontents = {"dvd":"List by DVD", 
		       "dvdbytag": "List of DVDs by tag",
		       "movie": "List by movie",
                       "yearfull": "List of full-length movies by year",
                       "yearshort": "List of shorts by year",
                       "watchedyearfull": "List of watched full-length movies by year",
                       "watchedyearshort": "List of watched shorts by year",
                       "moviesbytag": "List of movies by tag",
                       "altnames": "Alternate movie names",
                       "directors": "Directors of these movies",
                       "directorsfull": "Directors of full-length movies",
                       "actors": "Actors working on these movies",
                       "actorsfull": "Actors working on full-length movies",
                       "majortags": "Major tags"};
    if profile == "full":
        header = "David's full movie list"
        toc_list = ("dvd", "dvdbytag", "movie", "yearfull", "yearshort", "watchedyearfull",                    
                    "watchedyearshort", "moviesbytag", "majortags", "directors", "actors", "altnames")
        collection = "complete"
    elif profile == "DVD":
        header = "David's DVDs"
        toc_list = ("dvd", "dvdbytag")
        collection = "complete"
    elif profile == "movie":
        header = "David's movies"
        toc_list = ("movie", "yearfull", "yearshort", "watchedyearfull", "watchedyearshort", "moviesbytag", "majortags", "altnames")
        collection = "complete"
    elif profile == "people":
        header = "Actors and directors"
        toc_list = ("directors", "actors")
        collection = "complete"
    elif profile == "full length":
        header = "David's full length films"
        toc_list = ("dvd", "dvdbytag", "movie", "yearfull", "watchedyearfull",                    
                    "moviesbytag", "majortags", "directors", "actors", "altnames")
        collection = "full length"
    elif profile == "watched full length":
        header = "David's watched full length films"
        toc_list = ("dvd", "dvdbytag", "movie", "yearfull", "watchedyearfull",                    
                    "moviesbytag", "majortags", "directors", "actors", "altnames")
        collection = "watched fl"
    else:
        print ("{} is an unknown profile.".format (profile))
        raise Major_Error
    
    print ('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">''')

    print ("<html>\n<head>\n<META http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">\n"
           "<title>{0}</title>\n</head>\n<body>"
           "<h1>{0}</h1>\n".format (header))
    print ("<ul>")
    for short_id in toc_list:
        print ("<li><a href=\"#{}\">{}</a></li>".format (short_id, tableofcontents [short_id]))
    print ("</ul>")

    for s in toc_list:
        printsection (s, collection)

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

