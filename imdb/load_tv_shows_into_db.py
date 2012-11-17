#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb
import sqlite3

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

def shows_display (name, season, movie_id, have_watched):
    print (name)
    lacks_episode_name = False
    if name == "This is Wonderland":
        lacks_episode_name = True
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
            print (show_list)
            print ()
    else:
        mcur.execute ("INSERT INTO movies_to_drop VALUES({});".format(movie_id))
        mcur.execute ("SELECT dvd_id FROM dvd_contents WHERE movie_id = {};".format (movie_id))
        dvd_ids = mcur.fetchall ()
        for show in show_list:
            if lacks_episode_name:
                episode_name = str(show[1]) + '/' + str (show[2])
            else:
                episode_name = show[3]
            escaped_full_name = mcon.escape ('"' + show [0] + '": ' + episode_name)
            mcur.execute ("INSERT INTO movie VALUES (NULL, {}, {}, 0, {}, {});".format (
                   escaped_full_name, show[4], have_watched, escaped_full_name))
            new_movie_id = mcon.insert_id ()
            mcur.execute ("INSERT INTO tv_show VALUES ({}, {}, {}, {}, {});".format (
                new_movie_id, mcon.escape(show [0]), mcon.escape(episode_name), show[1], show [2]))
            for dvd in dvd_ids:
                mcur.execute ("INSERT INTO dvd_contents VALUES ({}, {});".format (dvd[0], new_movie_id))
            scur.execute ("SELECT director FROM episode_directors "
                          "WHERE show_name = ? AND season = ? AND episode = ?;",
                          (show[0], show [1], show [2]))
            directors = scur.fetchall ()
            for director in directors:
                mcur.execute ("INSERT INTO director VALUES ({}, {});".format
                       (mcon.escape (director[0]), new_movie_id))
            scur.execute ("SELECT actor FROM episode_actors "
                          "WHERE show_name = ? AND season = ? AND episode = ?;",
                          (show[0], show [1], show [2]))
            actors = scur.fetchall ()
            for actor in actors:
                mcur.execute ("INSERT INTO actor VALUES ({}, {});".format (mcon.escape(actor[0]), new_movie_id))
            mcur.execute ("INSERT INTO tags SELECT {}, tag FROM tags where movie_id = {};"
                          "".format (new_movie_id, movie_id))
                      
    #if name in show_names:
        #print ("{} in show names list.".format (name))
    #if name in show_with_episodes:
     #   print ("{} has episode information.".format (name))
      #  print ("{}".format (show_with_episodes [name]))
    #return

mysql_open()
sq_open ()
mcur.execute ("SELECT m.movie_id, t.name, season_num, have_watched FROM tv_show_old t "
              "INNER JOIN movie m on t.movie_id = m.movie_id "
              "WHERE is_season = 1;")
              #"WHERE is_season = 1 AND t.name LIKE \"Star Trek%\";");
shows = mcur.fetchall()

for s in shows:
    shows_display (s[1], s[2], s[0], s[3])
mcon.commit()
