#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pymysql as mdb
import sys
import readline

try:
    global con, cur
    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")

    cur.execute ("SELECT movie_id, name, year from movie " 
                 "where have_watched and is full_length" 
                 ";")
    remaining_movie_list = set ()
    movie_name = {}
    for movie in cur.fetchall ():
        remaining_movie_list.add (movie [0])
        movie_name [movie [0]] = "{} ({})".format (movie[1], movie[2])

    group_num = 1
    while (len (remaining_movie_list) > 0):
        if group_num == 1:
            first_movie = 376
            remaining_movie_list.remove (376)
        else:
            first_movie = min(remaining_movie_list)
            remaining_movie_list.remove (first_movie)
        movies_tree = [set((first_movie,))]
        movies_set = set ((first_movie,))
        i = 0
        while (len (movies_tree[i]) > 0):
            i += 1;
            movies_tree.append (set ())
            for movie in movies_tree[i - 1]:
                cur.execute ("SELECT DISTINCT p2.movie_id from person p2 "
                             "INNER JOIN person p1 ON p1.name = p2.name "
                             "INNER JOIN movie m ON m.movie_id = p2.movie_id "
                             "WHERE p1.movie_id = {} "
                             " AND m.have_watched AND m.is_full_length "
                             "ORDER BY p2.movie_id;"
                             "".format(movie))           
                newbies = cur.fetchall ()
                for newb in newbies:
                    if newb[0] not in movies_set:
                        remaining_movie_list.remove (newb [0])
                        movies_set.add (newb [0])
                        movies_tree [i].add (newb[0])

        print ("==Group {}==".format (group_num))
        print ("Total number of movies: ", len (movies_set))
        print
        for i in movies_set:
            print (movie_name [i], "~", i)
        group_num += 1

except mdb.Error as e:
    print (e)
    sys.exit(1)
