#!/usr/bin/python3.3
import re
import gzip
import sqlite3

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
        or "{{SUSPENDED}}" in movie_part or movie_part[0] == '"'):
        return
    movie_match = re.match (r"(.*) \(([12][0-9][0-9][0-9])\)", movie_part)
    if not movie_match:
        movie_match = re.match (r"(.*) \(([12][0-9][0-9][0-9])/([^)]*)\)", movie_part)
        if not movie_match:
            print ("ERROR: year not found in {}".format (movie_part))
            return
        else:
            movie = movie_match.group (1)
            year = movie_match.group (2)
            version = movie_match.group (3)
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
    #line_num = 0
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
        #line_num += 1
        #if line_num > 10000:
        #    break
# load in directors
name = ""
movie_director = dict()
with open ("directors.list", "r") as f:
    #line_num = 0
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
        #line_num += 1
        #if line_num > 100000:
        #    break
#with gzip.open ("act_pickle.gz", "wb") as f_out:
    #pickle.dump (movie_names, f_out)
    #pickle.dump (movie_actor, f_out)
    #pickle.dump (movie_director, f_out)

print ("Dumping to SQLite")
conn = sqlite3.connect('movies.db')
curr = conn.cursor()
curr.execute ("CREATE TABLE movie (movie_id INTEGER PRIMARY KEY, movie_name TEXT, year INTEGER, variant TEXT, UNIQUE (movie_name, year, variant));")
curr.execute ("CREATE INDEX movie_idx on movie (movie_name);")

curr.execute ("CREATE TABLE movie_actors (movie_id INTEGER, actor TEXT, PRIMARY KEY (movie_id, actor), FOREIGN KEY (movie_id) REFERENCES movie(movie_idx));")
curr.execute ("CREATE INDEX ma_idx ON movie_actors (movie_id);")

curr.execute ("CREATE TABLE movie_directors (movie_id INTEGER, director TEXT, PRIMARY KEY (movie_id, director), FOREIGN KEY (movie_id) REFERENCES movie(movie_idx));")
curr.execute ("CREATE INDEX md_idx ON movie_directors (movie_id);")

for m in movie_names:
    for movie in movie_names [m]:
#        print (movie)
        if len(movie) == 2:
            curr.execute ("INSERT INTO movie values (NULL, ?, ?, NULL);", (movie[0], movie[1]))
        else:
            curr.execute ("INSERT INTO movie values (NULL, ?, ?, ?);", (movie[0], movie[1], movie[2]))

for movie in movie_actor:
    for a in movie_actor[movie]:
        #print (a)
        curr.execute ("SELECT movie_id FROM movie where movie_name = ? AND year = ?;", (movie[0], movie[1]))
        mids = curr.fetchall ()
        if len (mids) < 1:
            curr.execute ("SELECT movie_id FROM movie where movie_name = ? and year = ? and variant = ?;", (movie[0], movie[1], movie[2]))
            mids = curr.fetchall ()
        #print (mids)
        curr.execute ("INSERT OR IGNORE INTO movie_actors values (?, ?);", (mids[0][0], a))

for movie in movie_director:
    for a in movie_director[movie]:
        curr.execute ("SELECT movie_id FROM movie where movie_name = ? AND year = ?;", (movie[0], movie[1]))
        mids = curr.fetchall ()
        if len (mids) > 1:
            if len (movie) != 3:
                print ("ERROR: movie is returning multiple mids despite not having a variant.")
                print (a, movie, mids)
                curr.execute ("SELECT * FROM movie where movie_name = ? AND year = ?;", (movie[0], movie[1]))
                print (curr.fetchall())
                continue
            curr.execute ("SELECT movie_id FROM movie where movie_name = ? and year = ? and variant = ?;", (movie[0], movie[1], movie[2]))
            mids = curr.fetchall ()
#        print (a, movie, mids)
        curr.execute ("INSERT INTO movie_directors values (?, ?);", (mids[0][0], a))
conn.commit()
