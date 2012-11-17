#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb
import sqlite3
import difflib

con = None
cur = None

def mysql_open ():
    '''Open the database connection'''
    global mcon, mcur
    mcon = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    mcur = mcon.cursor()
    mcur.execute ("SET NAMES 'utf8'")

def sq_open ():
    global scon, scur
    scon = sqlite3.connect('tv_show.db')
    scur = scon.cursor()

def shows_display (name, season, movie_id, have_watched, movie_name, year):
    old_episode_name = movie_name.partition ('": ')[2].strip()
    print ()
    print (movie_name, '/', old_episode_name)
    mcur.execute ("SELECT * from director where movie_id = {};".format (movie_id))
    if (len (mcur.fetchall ()) > 0):
        print ("movie_id {} exists in director table; skipping...".format (movie_id))
        return
    mcur.execute ("SELECT * from actor where movie_id = {};".format (movie_id))        
    if (len (mcur.fetchall ()) > 0):
        print ("movie_id {} exists in actor table; skipping...".format (movie_id))
        return
    mcur.execute ("SELECT * from tv_show where movie_id = {};".format (movie_id))        
    if (len (mcur.fetchall ()) > 0):
        print ("movie_id {} exists in tv_show table; skipping...".format (movie_id))
        return    
    scur.execute ("SELECT show_name, season, episode, episode_name, year FROM episode_names "
                  "WHERE show_name LIKE ? AND season LIKE ? ORDER BY season, episode;", (name, season))
    show_list = scur.fetchall()
    if show_list == []:
        scur.execute ("SELECT show_name, season, episode, episode_name FROM episode_names "
                      "WHERE show_name LIKE ? ORDER by season, episode;", (name, ))
        show_list = scur.fetchall()
        if show_list == []:
            print ("{} has no episode information.".format (name))
        else:
            print ("{} (season {}) has no episode information, but the show does.".format (name, season))
            #print (show_list)
            print ()
    else:
        close_matches = difflib.get_close_matches (old_episode_name, [f[3] for f in show_list])
        matching_shows = []
        for f in show_list:
            if f[3] in close_matches:
                print (len(matching_shows), ': ', end='')
                matching_shows.append (f)
                print (f)
        if matching_shows == []:
            print (movie_name, " has no clear matches.")
            return
        epnum = input ("Number of matching show: ")
        if epnum == None or not (0 <= int(epnum) < len (matching_shows)):
            return
        f = matching_shows[int(epnum)]
        print ("You selected ", f)  
        #mcur.execute ("INSERT INTO movies_to_drop VALUES({});".format(movie_id))
        #mcur.execute ("SELECT dvd_id FROM dvd_contents WHERE movie_id = {};".format (movie_id))
        #dvd_ids = mcur.fetchall ()
        episode_name = f[3]
        escaped_full_name = mcon.escape ('"' + f [0] + '": ' + episode_name)
        #mcur.execute ("INSERT INTO movie VALUES (NULL, {}, {}, 0, {}, {});".format (
        #       escaped_full_name, year, have_watched, escaped_full_name))
        new_movie_id = movie_id; # don't change the movie table
        mcur.execute ("INSERT INTO tv_show VALUES ({}, {}, {}, {}, {});".format (
            new_movie_id, mcon.escape(f [0]), mcon.escape(episode_name), f[1], f[2]))
        #for dvd in dvd_ids:
        #    mcur.execute ("INSERT INTO dvd_contents VALUES ({}, {});".format (dvd[0], new_movie_id))
        scur.execute ("SELECT director FROM episode_directors "
                      "WHERE show_name = ? AND season = ? AND episode = ?;",
                      (f[0], f [1], f [2]))
        directors = scur.fetchall ()
        for director in directors:
            mcur.execute ("INSERT INTO director VALUES ({}, {});".format
                   (mcon.escape (director[0]), new_movie_id))
        scur.execute ("SELECT actor FROM episode_actors "
                      "WHERE show_name = ? AND season = ? AND episode = ?;",
                      (f[0], f [1], f [2]))
        actors = scur.fetchall ()
        for actor in actors:
            mcur.execute ("INSERT INTO actor VALUES ({}, {});".format (mcon.escape(actor[0]), new_movie_id))
        #mcur.execute ("INSERT INTO tags SELECT {}, tag FROM tags where movie_id = {};"
        #              "".format (new_movie_id, movie_id))
        return              
    #if name in show_names:
        #print ("{} in show names list.".format (name))
    #if name in show_with_episodes:
     #   print ("{} has episode information.".format (name))
      #  print ("{}".format (show_with_episodes [name]))
    #return

mysql_open()
sq_open ()
mcur.execute ("SELECT m.movie_id, t.name, season_num, have_watched, m.name, m.year FROM tv_show_old t "
              "INNER JOIN movie m on t.movie_id = m.movie_id "
              "WHERE is_season = 0 AND t.name LIKE \"Get Smart\";")
              #"WHERE is_season = 1 AND t.name LIKE \"Star Trek%\";");
shows = mcur.fetchall()

for s in shows:
    shows_display (s[1], s[2], s[0], s[3], s[4], s[5])
mcon.commit()
