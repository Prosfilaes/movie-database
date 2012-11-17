#!/usr/bin/python3
# -*- coding: utf-8 -*-


# The problem should be fixed; we should never need to run this again
exit ()
import pymysql as mdb
import sys

con = None

try:

    con = mdb.connect('localhost', 'dvdeug', '', 'DVDs', use_unicode=True, charset="utf8")
    cur = con.cursor()
    cur.execute ("SET NAMES 'utf8'")
    while (True):
        cur.execute("SELECT dvd.dvd_id, dvd.title FROM dvd;");
        rows = cur.fetchall()
        for row in rows:
            if ((row [1])[-1:]  == '\0'):
                print (str(row[1]), str(row[1][0:-1]))
                cur.execute ("UPDATE dvd SET dvd.title = \"%s\" WHERE dvd.dvd_id = %s;" % (row[1][0:-1], str (row[0])))
                break
        else:
            break
    cur.execute("SELECT dvd.dvd_id, dvd.title FROM dvd;");
    rows = cur.fetchall()
    for row in rows:
        print (row)
    con.commit ()    
    
except mdb.Error as e:
  
    print (e)
    sys.exit(1)
    
finally:    
        
    if con:
        con.rollback ()
        con.close()

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#include <my_global.h>
#include <mysql.h>

##const int year_start = 1878;
##const int year_end = 2020;
##
##void usage_note (char * program_name) {
##  fprintf (stderr, 
##	   "This utility adds a DVD whose name is not necessarily related to its movies to the database.\n"
##	   "It takes 2n +1 arguments, where n ∈ ℤ, n > 0.\n"
##	   "%s dvdname movie1 year1 {movie2 year2 ...}.\n", program_name);
##}
##
##void year_note (const int year_start, const int year_end) {
##  fprintf (stderr, "The year must be a decimal number between %d and, err, %d.\n",
##	   year_start, year_end); 
##}
##
##void check_year (const char* year) {
##  if (strlen (year) == 4) {
##    errno = 0;
##    int year_num = strtol (year, NULL, 10);
##    const int year_start = 1878;
##    const int year_end = 2020;
##    if (errno != 0 || year_num < year_start || year_num > year_end) {
##      year_note (year_start, year_end);
##      exit (1);
##    }
##  } else {
##    year_note (year_start, year_end);
##    exit (1);
##  }
##}
##
##MYSQL *conn;
##void check_mysql_error (int e) {
##  if (e) {
##    printf("Error %u: %s\n", mysql_errno(conn), mysql_error(conn));
##    mysql_rollback (conn);
##    exit(1);
##  }
##}
##
##int main(int argc, char **argv)
##{
##
##  if (argc < 4 || argc % 2 == 1) {
##    usage_note (argv[0]);	
##    exit (1);
##  }
##
##  conn = mysql_init(NULL);
##
##  if (conn == NULL) {
##    printf("Error %u: %s\n", mysql_errno(conn), mysql_error(conn));
##    exit(1);
##  }
##
##  if (mysql_real_connect(conn, "localhost", "dvdeug", 
##			 "", "DVDs", 0, NULL, 0) == NULL) 
##    {
##      printf("Error %u: %s\n", mysql_errno(conn), mysql_error(conn));
##      exit(1);
##    }
##
##  // Work in transactions
##  check_mysql_error (mysql_autocommit (conn, 0));
##
##  // Process DVD name
##  const int escaped_name_length = strlen (argv[1]) * 2 + 1;
##  char escaped_name [escaped_name_length];
##  char query[1024];
##  unsigned long int dvd_id, movie_id;
##
##  mysql_real_escape_string (conn, escaped_name, argv[1], strlen (argv[1]));
##	
##  // Insert title into dvd table
##  snprintf (query, 1024, "INSERT INTO dvd (title) VALUES ('%s')", escaped_name);
##  check_mysql_error (mysql_query(conn, query));
##  dvd_id = mysql_insert_id (conn);
##  if (dvd_id == 0) {
##    fprintf (stderr, "insert_id problems with dvd; aborting\n");
##    mysql_rollback (conn);
##    exit(1);
##  }
##  
##  // Process Movies
##  for (int movie_count = 1; movie_count * 2  < argc; movie_count++) {	
##    const char * movie_name = argv [movie_count * 2];
##    const char * year =  argv [movie_count * 2 + 1];
##    check_year (year); // Verfies year is a string of four digits, among other things
##    const int movie_name_length = strlen (movie_name);
##    char escaped_name [movie_name_length * 2 + 1];
##    mysql_real_escape_string (conn, escaped_name, movie_name, movie_name_length);
##
##    // Insert name and year into movie table
##    snprintf (query, 1024, "INSERT INTO movie (name, year, is_full_length) VALUES ('%s', %s, %s)", 
##	      escaped_name, year, "TRUE");
##    check_mysql_error (mysql_query(conn, query));
##    movie_id = mysql_insert_id (conn);
##    if (movie_id == 0) {
##      fprintf (stderr, "insert_id problems with movie; aborting\n");
##      mysql_rollback (conn);
##      exit(1);
##    }
##	
##    // Insert into dvd-movie connection table
##    snprintf (query, 1024, "INSERT INTO dvd_contents (dvd_id, movie_id) VALUES (%lu, %lu)", dvd_id, movie_id);
##    check_mysql_error (mysql_query(conn, query));
##  
##  }
##
##  // Everything seems to have gone okay; commit transaction.
##  // I don't believe this can fail and the rollback work, but check anyway.
##  check_mysql_error (mysql_commit (conn));
##  
##  // Close up shop and report success
##  mysql_close(conn);
##  printf ("Successfully added %s, dvd_id (%lu).\n", argv[1], dvd_id);
##  return (0);
##}
