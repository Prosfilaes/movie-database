#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb

con = None
cur = None
NO_MATCH = 0
NAME_ONLY = 1
FULL_MATCH = 2
FULL_MATCH_VARIANTS = 3

NO_FULL_MATCH_ALT_MATCH = 4
FULL_MATCH_ALT_MATCH = 5
ALT_VARIANT_MATCH = 6

def open ():
    '''Open the database connection'''
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

def print_movie_people (movie, year):
    if movie in movie_names:
        movie_list = movie_names [movie]
        print (movie_list)
        m = None
        match_found = False
        for n in movie_list:
            if m == None:
                m = n
            if n == (movie, year):
                print ("Match found.")
                m = n
                match_found = True
                continue
            elif (n[0], n[1]) == (movie, year):
                print ("Partial match found with version {}".format (n[2]))
                m = n
                match_found = True
        if not match_found:
            print ("No match found; using first {}".format (m))
        if m in movie_actor:
            print (movie_actor [m])
        else:
            print ("No actors found!")
        if m in movie_director:
            print (movie_director [m])
        else:
            print ("No director found!");

def movie_match (movie, year):
    years = str(year)
    if movie in movie_names:
        movie_list = movie_names [movie]
        # there's movies with variant forms and non-variant forms
        # delete non-variant forms and resolve not to trust variant forms
        delete_list = set ()
        for i in movie_list:
            for j in movie_list:
                if i != j and len (i) == 2 and (i[0], i[1]) == (j[0], j[1]):
                    delete_list.add (i)
        if len (delete_list) > 0:
            for i in delete_list:
                movie_list.remove (i)
                    
        for n in movie_list:
            if n == (movie, years):
                return FULL_MATCH
            elif (n[0], n[1]) == (movie, years):
                return FULL_MATCH_VARIANTS
        return NAME_ONLY
    else:
        return NO_MATCH

with gzip.open ("act_pickle.gz", "rb") as f:
    movie_names = pickle.load (f)
    movie_actor = pickle.load (f)
    movie_director = pickle.load (f)
open()
cur.execute ("SELECT movie_id, name, year FROM movie " 
             "WHERE movie_id NOT IN (select tv_show.movie_id FROM tv_show) ORDER BY movie_id;")
movies = cur.fetchall()
num_movies_per_state = [0, 0, 0, 0, 0, 0, 0]
for m in movies:
    m_state = movie_match (m[1], m[2])
    num_movies_per_state [m_state] += 1
    cur.execute ("SELECT amn.movie_id, amn.name, movie.year FROM alternate_movie_names amn "
                 "INNER JOIN movie ON amn.movie_id = movie.movie_id WHERE amn.movie_id = {};".format (m[0]))
    amn = cur.fetchall()
    for a in amn:
        a_state = movie_match (a[1], a[2])
        if a_state == 2:
            if m_state > 1:
                print ("Full match and alt match: ", m, a)
                num_movies_per_state [FULL_MATCH_ALT_MATCH] += 1
                break
            else:
                num_movies_per_state [NO_FULL_MATCH_ALT_MATCH] += 1
                break
        # We're miscounting states where one variant name gives a match and another gives a variant match
        # and not count states with multiple alternate matches in any distinct way
        elif a_state == 3:
            num_movies_per_state [ALT_VARIANT_MATCH] += 1
            break
            
num_movies = len (movies)
print ("Out of {} movies:".format (num_movies))
print ("\t{} ({}) had no match".format (num_movies_per_state [NO_MATCH], num_movies_per_state [NO_MATCH] / num_movies))
print ("\t{} ({}) matched the name only".format (num_movies_per_state [NAME_ONLY], num_movies_per_state [NAME_ONLY] / num_movies))
print ("\t{} ({}) matched the name and year".format (num_movies_per_state [FULL_MATCH], num_movies_per_state [FULL_MATCH] / num_movies))
print ("\t{} ({}) matched the name and year, but had variants".format (num_movies_per_state [FULL_MATCH_VARIANTS], num_movies_per_state [FULL_MATCH_VARIANTS] / num_movies))
print ("\t{} ({}) had no real match but had an alternate match".format (num_movies_per_state [NO_FULL_MATCH_ALT_MATCH], num_movies_per_state [NO_FULL_MATCH_ALT_MATCH] / num_movies))
print ("\t{} ({}) had a real match AND an alternate match".format (num_movies_per_state [FULL_MATCH_ALT_MATCH], num_movies_per_state [FULL_MATCH_ALT_MATCH] / num_movies))
print ("\t{} ({}) had an alternate match with variants".format (num_movies_per_state [ALT_VARIANT_MATCH], num_movies_per_state [ALT_VARIANT_MATCH] / num_movies))

#for i in (1, 2):
#    movie = input ("Movie name: ")
#    year = input ("Year: ")
#    print_movie_people (movie, year)

               

