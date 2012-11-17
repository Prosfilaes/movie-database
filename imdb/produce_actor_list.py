#!/usr/bin/python3.3
import gzip
import pickle
import pymysql as mdb

con = None
cur = None

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

with gzip.open ("act_pickle.gz", "rb") as f:
    movie_names = pickle.load (f)
    movie_actor = pickle.load (f)
    movie_director = pickle.load (f)
#for i in (1, 2):
#    movie = input ("Movie name: ")
#    year = input ("Year: ")
#    print_movie_people (movie, year)

               

