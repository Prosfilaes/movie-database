#!/usr/bin/python3.3
import re
import gzip
import pickle
import sys

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
    episode_match = re.match (r"(.*) \(#([0-9])*\.([0-9]*)\)", episode)
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
    # Split chunks
    if 'A' <= movie_part[1] <= 'G':
        chunk_val = 1;
    elif 'H' <= movie_part[1] <= 'R':
        chunk_val = 2;
    elif 'S' <= movie_part[1] <= 'Z':
        chunk_val = 3;
    else:
        chunk_val = 4
    if chunk_val != chunk_id:
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
        full_movie = (tv_show, year, version, episode)
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
        full_movie = (tv_show, year, version)    
        
    return (full_movie, actor)


def add_tv_show (show):
    global show_names, show_actor, show_with_episodes;
    # That is, if there is an episode component
    if len(show) == 4:
        if show[0] in show_with_episodes:
            show_with_episodes[show[0]].add (show)
        else:
            show_with_episodes[show[0]] = set([show])
    else:
        if show[0] in show_names:
            show_names[show[0]].add(show)
        else:
            show_names[show[0]] = set ([show])

name = ""
show_names = dict ()
show_actor = dict ()
show_with_episodes = dict ()
show_director = dict ()
chunk_id = 2
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
movie_director = dict()
with open ("directors.list", "r") as f:
#    line_num = 0
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
print ("Starting to pickle")
with gzip.open ("show_pickle{}.gz".format(chunk_id), "wb") as f_out:
    pickle.dump (show_names, f_out)
    pickle.dump (show_with_episodes, f_out)
    pickle.dump (show_actor, f_out)
    pickle.dump (show_director, f_out)

