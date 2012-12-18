#!/usr/bin/python3.3
import re
import gzip
import sqlite3
import sys
import shutil

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

def parse_episode (episode):
    # Episode (#x.y) or just (#x.y)
    # Also Episode (#xx.y) or just (#xx.y)
    episode_match = re.match (r"(.*) \(#([0-9]*)\.([0-9]*)\)", episode)
    if episode_match:
        return (episode_match.group(1).strip(), episode_match.group(2), episode_match.group(3))
    else:
        episode_match = re.match (r"\(#([0-9])*\.([0-9]*)\)", episode)
        if episode_match:
            return ("", episode_match.group(1), episode_match.group(2))
        else:
            episode_match = re.match (r"\(([^)]*)\)", episode)
            if episode_match:
                return ("", episode_match.group(1), "")
            else:
                return (episode, "", "")

def process_line (line):
# returns (movie, person)
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
            new_tv_show = tv_show + " (" + version + ")"
            if tv_show in variants:
                (variants[tv_show]).add ((new_tv_show, year))
            else:
                variants[tv_show] = set([(new_tv_show, year)])
            tv_show = new_tv_show
        full_movie = (tv_show, year, episode)
    else:
        movie_match = re.match (r'"(.*)" \(([^)]*)\)', movie_part)
        if not movie_match:
            print (line, end = "")
            print ("ERROR: Can't parse movie (no episode) {}".format (movie_part))
            return
        tv_show = movie_match.group (1)
        try:
            (year, version) = parse_year_version (movie_match.group (2))
        except ValueError:
            print (line)
            print ("Error: {} (no episode) does not parse as year or year & version.".format (
                    movie_match.group(2)))
            return
        if version != "":
            new_tv_show = tv_show + " (" + version + ")"
            if tv_show in variants:
                (variants[tv_show]).add ((new_tv_show, year))
            else:
                variants[tv_show] = set([(new_tv_show, year)])
            tv_show = new_tv_show
        full_movie = (tv_show, year)    
    return (full_movie, actor)

def add_tv_show (show):
    global show_actor, show_with_episodes;
    # That is, if there is an episode component
    if len(show) == 3:
        if show[0] in show_with_episodes:
            show_with_episodes[show[0]].add (show)
        else:
            show_with_episodes[show[0]] = set([show])

name = ""
show_actor = dict ()
show_with_episodes = dict ()
show_director = dict ()
variants = dict ()
with open ("act_list", "r") as f:
#    line_num = 0
    for line in f:
        movie_person = process_line (line)
        if movie_person == None:
            continue
        add_tv_show (movie_person[0])
        if movie_person[0] in show_actor:
            show_actor[movie_person[0]].add(movie_person[1])
        else:
            show_actor[movie_person[0]] = set([movie_person[1]])
#        line_num += 1
#        if line_num > 10000:
#            break
# load in directors
name = ""
with open ("directors.list", "r") as f:
    line_num = 0
    for line in f:
        movie_person = process_line (line)
        if movie_person == None:
            continue
        add_tv_show (movie_person[0])
        if movie_person[0] in show_director:
            show_director[movie_person[0]].add(movie_person[1])
        else:
            show_director[movie_person[0]] = set([movie_person[1]])
#        line_num += 1
#        if line_num > 10000:
#            break
print (show_with_episodes)
sys.exit ()
print ("Dumping to SQLite")
shutil.move ('tv_show.db', 'tv_show.db.bak')
conn = sqlite3.connect('tv_show.db')
curr = conn.cursor()
curr.execute ("CREATE TABLE episode_names (show_name TEXT, year INTEGER, season INTEGER, episode INTEGER, episode_name TEXT, PRIMARY KEY (show_name, year, season, episode));")
curr.execute ("CREATE INDEX en_show_name_idx ON episode_names (show_name, year, season);")

curr.execute ("CREATE TABLE simple_show_actors (show_name TEXT, year INTEGER, actor TEXT, PRIMARY KEY (show_name, year, actor));")
curr.execute ("CREATE INDEX ssa_idx on simple_show_actors (show_name, year);")
curr.execute ("CREATE TABLE episode_actors (show_name TEXT, year INTEGER, season INTEGER, episode INTEGER, actor TEXT, PRIMARY KEY (show_name, year, season, episode, actor));")
curr.execute ("CREATE INDEX ea_idx ON episode_actors (show_name, year, season, episode);")

curr.execute ("CREATE TABLE simple_show_directors (show_name TEXT, year INTEGER, director TEXT, PRIMARY KEY (show_name, year, director));")
curr.execute ("CREATE INDEX ssd_idx ON simple_show_directors (show_name);")
curr.execute ("CREATE TABLE episode_directors (show_name TEXT, year INTEGER, season INTEGER, episode INTEGER, director TEXT, PRIMARY KEY (show_name, year, season, episode, director));")
curr.execute ("CREATE INDEX ed_idx ON episode_directors (show_name, year, season, episode);")

curr.execute ("CREATE TABLE variants (show_name TEXT, year INTEGER, full_name TEXT, PRIMARY KEY (show_name, year, full_name));")
curr.execute ("CREATE INDEX variant_idx ON variants (show_name);")

curr.execute ("CREATE TABLE show_no_episode_info (show_name TEXT, year INTEGER, PRIMARY KEY (show_name, year));")

for vkey in variants:
    for v in variants[vkey]:
       curr.execute ("INSERT INTO variants VALUES (?, ?, ?);", (vkey, v[0], v[1]))
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_1')

for show in show_with_episodes:
    for swe in show_with_episodes [show]:
        try:
            curr.execute ("INSERT INTO episode_names VALUES (?, ?, ?, ?, ?);",
                          (swe[0], swe[1], swe[2][1], swe[2][2], swe[2][0]))
        except sqlite3.IntegrityError:
            print ("Rejected entry from show_with_episodes: ", swe)
        curr.execute ("INSERT INTO episode_names VALUES (?, ?, ?, ?, ?);", (swe[0], swe[1], swe[2][1], swe[2][2], swe[2][0]))
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_2')

for show in show_actor:
    for actor in show_actor[show]:
        # if it doesn't have epsiode information or that information isn't labled by season (episode number ?!?)
        if len (show) == 2: # doesn't have episode information
            curr.execute ("INSERT INTO simple_show_actors VALUES (?, ?, ?);", (show[0], show[1], actor));
        # Show has no season information; drop on floor and note that we did so
        # hopefully nothing dropped was important
        elif len (show) == 3 and show[2][1] == '':
            try:
                curr.execute ("INSERT INTO show_no_episode_info VALUES (?, ?);", (show[0], show[1]))
            except sqlite3.IntegrityError:
                print ("Rejected entry from show_actor for show_no_episode_info: ", show)
        elif len (show) == 3: # has episode information
            # I hate to use IGNORE here, but there can be multiple epsiodes with the same season/episode and different names
            # I hate this data.
            try:
                curr.execute ("INSERT INTO episode_actors VALUES (?, ?, ?, ?, ?);", (show[0], show[1], show[2][1], show[2][2], actor))
            except sqlite3.IntegrityError:
                print ("Rejected entry from show_actor for episode_actors: ", show)
        else:
            print ("ERROR: {} is a malformed key in show_actor.".format (show))
            sys.exit ()
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_3')

for show in show_director:
    for director in show_director[show]:
        # if it doesn't have epsiode information or that information isn't labled by season (episode number ?!?)
        if len (show) == 2: # doesn't have episode information
            curr.execute ("INSERT INTO simple_show_directors VALUES (?, ?, ?);", (show[0], show[1], director));
        # Show has no season information; drop on floor and note that we did so
        # hopefully nothing dropped was important
        # IGNORE here because it was probably already entered in in the actor data
        elif len (show) == 3 and show[2][1] == '':
            curr.execute ("INSERT OR IGNORE INTO show_no_episode_info VALUES (?, ?);", (show[0], show[1]))
        elif len (show) == 3: # has episode information
            # I hate to use IGNORE here, but there can be multiple epsiodes with the same season/episode and different names
            # I hate this data.
            try:
                curr.execute ("INSERT INTO episode_directors VALUES (?, ?, ?, ?, ?);", (show[0], show[1], show[2][1], show[2][2], director))
            except sqlite3.IntegrityError:
                print ("Rejected entry from show_director for episode_directors: ", show)            
        else:
            print ("ERROR: {} is a malformed key in show_director.".format (show))
            sys.exit ()
conn.commit ()
shutil.copy ('tv_show.db', 'tv_show.db_4')

conn.commit ()
curr.close ()


