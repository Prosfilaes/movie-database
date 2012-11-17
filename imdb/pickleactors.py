#!/usr/bin/python3.3
import re
import gzip
import pickle

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
            print ("ERROR: Missing actor name");
            return
    movie_part = ""
    while movie_part == "":
        movie_part = s.pop(0).strip()
    if ("(VG)" in movie_part or "(archive footage)" in movie_part 
        or "(????)" in movie_part or "(scenes deleted)" in movie_part
        or movie_part[0] == '"'):
        return
    movie_match = re.match (r"(.*) \(([12][0-9][0-9][0-9])\)", movie_part)
    if not movie_match:
        movie_match = re.match (r"(.*) \(([12][0-9][0-9][0-9])/([^)]*)\)", movie_part)
        if not movie_match:
            print ("ERROR: year not found in {}".format (movie_part))
            return
        else:
            movie = movie_match.group (1)
            version = movie_match.group (3)
            year = movie_match.group (2)
            full_movie = (movie, year, version)
    else:
        movie = movie_match.group (1)
        year = movie_match.group (2)
        full_movie = (movie, year)    
    return (full_movie, actor)

name = ""
movie_names = dict ()
movie_actor = dict ()
with open ("act_list", "r") as f:
#    line_num = 0
    for line in f:
        movie_person = process_line (line)
        if movie_person == None:
            continue
        if movie_person[0][0] in movie_names:
            movie_names[movie_person[0][0]].add(movie_person[0])
        else:
            movie_names[movie_person[0][0]] = set ([movie_person[0]])

        if movie_person[0] in movie_actor:
            movie_actor[movie_person[0]].add(movie_person[1])
        else:
            movie_actor[movie_person[0]] = set([movie_person[1]])
#        line_num += 1
#        if line_num > 10000:
#            break
# load in directors
name = ""
movie_director = dict()
with open ("directors.list", "r") as f:
#    line_num = 0
    for line in f:
        movie_person = process_line (line)
        if movie_person == None:
            continue
        if movie_person[0][0] in movie_names:
            movie_names[movie_person[0][0]].add(movie_person[0])
        else:
            movie_names[movie_person[0][0]] = set ([movie_person[0]])

        if movie_person[0] in movie_director:
            movie_director[movie_person[0]].add(movie_person[1])
        else:
            movie_director[movie_person[0]] = set([movie_person[1]])
#        line_num += 1
#        if line_num > 10000:
#            break
#with gzip.open ("act_pickle.gz", "wb") as f_out:
    #pickle.dump (movie_names, f_out)
    #pickle.dump (movie_actor, f_out)
    #pickle.dump (movie_director, f_out)

print ("Dumping to SQLite")
conn = sqlite3.connect('movies.db')
curr = conn.cursor()
curr.execute ("CREATE TABLE movie_actors (show_name TEXT, year INTEGER, actor TEXT, PRIMARY KEY (show_name, actor));")
curr.execute ("CREATE INDEX ssa_idx on simple_show_actors (show_name);")
curr.execute ("CREATE TABLE episode_actors (show_name TEXT, season INTEGER, episode INTEGER, actor TEXT, PRIMARY KEY (show_name, season, episode, actor));")
curr.execute ("CREATE INDEX ea_idx ON episode_actors (show_name, season, episode);")

curr.execute ("CREATE TABLE simple_show_directors (show_name TEXT, director TEXT, PRIMARY KEY (show_name, director));")
curr.execute ("CREATE INDEX ssd_idx ON simple_show_directors (show_name);")
curr.execute ("CREATE TABLE episode_directors (show_name TEXT, season INTEGER, episode INTEGER, director TEXT, PRIMARY KEY (show_name, season, episode, director));")
curr.execute ("CREATE INDEX ed_idx ON episode_directors (show_name, season, episode);")

curr.execute ("CREATE TABLE variants (show_name TEXT, full_name TEXT, PRIMARY KEY (show_name, full_name));")
curr.execute ("CREATE INDEX variant_idx ON variants (show_name);")

curr.execute ("CREATE TABLE show_no_episode_info (show_name TEXT PRIMARY KEY);")
