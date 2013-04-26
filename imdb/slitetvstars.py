#!/usr/bin/python3.3
import re
import gzip
import sqlite3
import sys
import shutil
from collections import namedtuple

def remove_comma (name):
    s = name.split (",", 1)
    if len (s) == 1:
        return name.strip ()
    name_match = re.match (r"(.*) (\([IVXLCDM]*\))", s[1])
    if not name_match:
        return s[1].strip () + " " + s[0].strip()
    else:
        return name_match.group(1).strip() + " " + s[0].strip() + " " + name_match.group(2).strip()

name = ""

def parse_year_version (year_version):
    year_match = re.match (r'([12][0-9][0-9][0-9])/(.*)', year_version)
    if year_match:
        year = year_match.group (1)
        version = year_match.group (2)
    else:
        year_match = re.match (r'([12][0-9][0-9][0-9])', year_version)
        if year_match:
            year = year_version
            version = ""
        else:
            raise ValueError
    return (year, version)

def parse_episode (episode): # return Episode
    # Episode (#x.y) or just (#x.y)
    episode_match = re.match (r"(.*) \(#([0-9])*\.([0-9]*)\)", episode)
    if episode_match:
        return Episode(name=episode_match.group(1).strip(), season_num=episode_match.group(2),
                       episode_num=episode_match.group(3))
    else:
        episode_match = re.match (r"\(#([0-9])*\.([0-9]*)\)", episode)
        if episode_match:
            return Episode(name="", season_num=episode_match.group(1),
                           episode_num=episode_match.group(2))
        else:
            # If we lack episode_num or season_num, just raise ValueError
            raise ValueError

def process_line (line):
# returns (Full_Movie, person string)
    global actor
    s = line.split('\t')
    new_actor = s.pop(0)
    if new_actor != "":
        actor = remove_comma (new_actor)
    # if it was a blank line, new_actor = "\n" and remove_comma turned it into ""
    if actor == "":
        if len (s) == 0:
            return
        else:
            print (line, end = "")
            print ("ERROR: Missing actor name")
            return
    movie_part = ""
    while movie_part == "":
        movie_part = s.pop(0).strip()
    if ("(VG)" in movie_part or "(archive footage)" in movie_part 
        or "(????)" in movie_part or "(scenes deleted)" in movie_part
        or movie_part[0] != '"'):
        return
    # TV shows 
    # Format "Show" (xxxx) {Episode (#x.y)} ... or
    # Format "Show" (xxxx) {(#x.y)} or
    # Format "Show" (xxxx) 
    # where all (xxxx) can be (xxxx/VARIANT)
    # Regexp below: group 1 is show, group 2 is year possibly with variant (parse later), 
    # group 3 is episode stuff
    movie_match = re.match (r'"(.*)" \(([^)]*)\) \{([^}]*)\}', movie_part)
    if movie_match:
        tv_show = movie_match.group (1)
        try:
            (year, version) = parse_year_version (movie_match.group (2))
        except ValueError:
            print (line, end = "")
            print ("Error: {} does not parse as year or year & version.".format (
                    movie_match.group(2)))
            return
        try:
            episode = parse_episode (movie_match.group (3))
        except ValueError:
            print (line, end = "")
            print ("Error: {} does not parse as episode information.".format (
                    movie_match.group (3)))
            return
        if version != "":
           return
        full_movie = Full_Movie(show_name=tv_show, year=year, episode=episode)
    else:
        return
        
    return (full_movie, actor)


def add_tv_show (show):
    # show is a Full_Movie
    global show_names, show_actor, show_with_episodes;
    # That is, if there is an episode component
    if len(show) == 3:
        if show.show_name in show_with_episodes:
            show_with_episodes[show.show_name].add (show)
        else:
            show_with_episodes[show.show_name] = set([show])
    else:
        if show.show_name in show_names:
            show_names[show.show_name].add(show)
        else:
            show_names[show.show_name] = set ([show])

Episode = namedtuple ("Episode", "name season_num episode_num")
Full_Movie = namedtuple ("Full_Movie", "show_name year episode")
name = ""
show_names = dict ()
show_actor = dict ()
show_with_episodes = dict ()
show_director = dict ()
#variants = dict ()
count = 0
with open ("act_list", "r") as f:
    for line in f:
        count = count + 1
        movie_person = process_line (line)
        if movie_person == None:
            continue
        (movie, actor) = movie_person
        add_tv_show (movie)

        if movie in show_actor:
            show_actor[movie].add(actor)
        else:
            show_actor[movie] = set([actor])
        #if count > 10000:
        #    break
# load in directors
name = ""
count = 0
with open ("directors.list", "r") as f:
    for line in f:
        count = count + 1
        movie_person = process_line (line)
        if movie_person == None:
            continue
        (movie, director) = movie_person
        add_tv_show (movie)

        if movie in show_director:
            show_director[movie].add(director)
        else:
            show_director[movie] = set([director])
        #if count > 10000:
        #    break

print ("Dumping to SQLite")
conn = sqlite3.connect('tv_show.db')
curr = conn.cursor()
curr.execute ("CREATE TABLE episode_names (show_name TEXT, season INTEGER, episode INTEGER, "
              "episode_name TEXT, year INTEGER, PRIMARY KEY (show_name, year, season, episode));")
curr.execute ("CREATE INDEX en_show_name_idx ON episode_names (show_name, season);")

curr.execute ("CREATE TABLE episode_actors (show_name TEXT, year INTEGER, season INTEGER,  "
              "episode INTEGER, actor TEXT, PRIMARY KEY (show_name, year, season, episode, actor));")
curr.execute ("CREATE INDEX ea_idx ON episode_actors (show_name, season, episode);")

curr.execute ("CREATE TABLE episode_directors (show_name TEXT, year INTEGER, season INTEGER, "
              "episode INTEGER, director TEXT, "
              "PRIMARY KEY (show_name, year, season, episode, director));")
curr.execute ("CREATE INDEX ed_idx ON episode_directors (show_name, season, episode);")

#curr.execute ("CREATE TABLE variants (show_name TEXT, full_name TEXT, "
#              "PRIMARY KEY (show_name, full_name));")
#curr.execute ("CREATE INDEX variant_idx ON variants (show_name);")

curr.execute ("CREATE TABLE show_no_episode_info (show_name TEXT, year INTEGER, PRIMARY KEY (show_name, year));")

#for vkey in variants:
#    for v in variants[vkey]:
#        curr.execute ("INSERT INTO variants VALUES (?, ?);", (vkey, v))
#conn.commit ()
#shutil.copy ('tv_show.db', 'tv_show.db_1')

for show in show_with_episodes:
    for swe in show_with_episodes [show]: #swe is a Full_Movie
        curr.execute ("SELECT * FROM episode_names WHERE show_name = ? and season = ? and episode = ? and year = ?;",
                      (swe.show_name, swe.episode.season_num, swe.episode.episode_num, swe.year))
        matches = curr.fetchall ()
        if len (matches) > 0:
            print ("Clashing entries for episode_names!")
            print (matches)
            print (swe)
        else:   
            curr.execute ("INSERT INTO episode_names VALUES (?, ?, ?, ?, ?);",
                          (swe.show_name, swe.episode.season_num, swe.episode.episode_num, swe.episode.name, swe.year))
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_2')

for show in show_actor: # show is Full_Movie
    for actor in show_actor[show]:
        # Show has no season information; drop on floor and note that we did so
        # hopefully nothing dropped was important
        if show.episode.season_num == '':
            curr.execute ("INSERT OR IGNORE INTO show_no_episode_info VALUES (?, ?);", (show.show_name, show.year))
        else: # has episode information
            # Instead of using IGNORE, we'll check
            curr.execute ("SELECT * FROM episode_actors WHERE show_name = ? and season = ? and episode = ? and year = ? and actor = ?;",
                         (show.show_name, show.episode.season_num, show.episode.episode_num, show.year, actor))
            matches = curr.fetchall ()
            if len (matches) > 0:
                print ("Clashing entries for episode_actors!")
                print (matches)
                print (show, actor)
            else:   
                curr.execute ("INSERT INTO episode_actors VALUES (?, ?, ?, ?, ?);",
                              (show.show_name, show.year, show.episode.season_num, show.episode.episode_num, actor))
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_3')

for show in show_director:
    for director in show_director[show]:
        # Show has no season information; drop on floor and note that we did so
        # hopefully nothing dropped was important
        if show.episode.season_num == '':
            curr.execute ("INSERT OR IGNORE INTO show_no_episode_info VALUES (?, ?);", (show.show_name, show.year))
        else: # has episode information
            # Instead of using IGNORE, we'll check
            curr.execute ("SELECT * FROM episode_directors WHERE show_name = ? and season = ? and episode = ? and year = ? and director = ?;",
                         (show.show_name, show.episode.season_num, show.episode.episode_num, show.year, director))
            matches = curr.fetchall ()
            if len (matches) > 0:
                print ("Clashing entries for episode_directors!")
                print (matches)
                print (show, director)
            else:              
                curr.execute ("INSERT INTO episode_directors VALUES (?, ?, ?, ?, ?);",
                            (show.show_name, show.year, show.episode.season_num, show.episode.episode_num, director))
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_4')

conn.commit ()
curr.close ()
