#!/bin/bash
q=`mdate | cut -c6-12`
mysqldump DVDs --user prosfilaes --password > nightly/dbbackup.$q
./average_movie_universe.py 8 > nightly/averagewscififl.$q # more of a test
./average_movie_universe.py 11 > nightly/averageanimation.$q
./average_movie_universe.py 9 > nightly/averagesingledvd.$q 
./average_movie_universe.py 6 > nightly/averagewfl.$q
./average_movie_universe.py 5 > nightly/averagesmallfl.$q
./average_movie_universe.py 4 > nightly/averagefl.$q
./average_movie_universe.py 10 > nightly/averagewtv.$q
./average_movie_universe.py 3 > nightly/averagewatched.$q
./average_movie_universe.py 7 > nightly/averagetv.$q
./average_movie_universe.py 2 > nightly/averagesmall.$q
./average_movie_universe.py 1 > nightly/averagemovie.$q

#./average_actor_universe.py 9 > nightly/averagesingledvd_actor.$q
#./average_actor_universe.py 8 > nightly/averagewscififl_actor.$q
#./average_actor_universe.py 6 > nightly/averagewfl_actor.$q
#./average_actor_universe.py 5 > nightly/averagesmallfl_actor.$q
#./average_actor_universe.py 7 > nightly/averagetv_actor.$q
#./average_actor_universe.py 4 > nightly/averagefl_actor.$q
#./average_actor_universe.py 3 > nightly/averagewatched_actor.$q
#./average_actor_universe.py 1 > nightly/averagemovie_actor.$q

