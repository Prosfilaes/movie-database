#!/bin/bash
q=`mdate | cut -c6-12`
mysqldump DVDs --user prosfilaes --password > nightly/dbbackup.$q
./average_movie_universe.py 8 > nightly/averagewscififl.$q # more of a test
./average_movie_universe.py 9 > nightly/averagesingledvd.$q 
./average_movie_universe.py 6 > nightly/averagewfluniverse.$q
./average_movie_universe.py 3 > nightly/averagewatcheduniverse.$q
./average_movie_universe.py 5 > nightly/averagesmallfl.$q
./average_movie_universe.py 2 > nightly/averagesmalluniverse.$q
./average_movie_universe.py 4 > nightly/averagefluniverse.$q
./average_movie_universe.py 7 > nightly/averagetvuniverse.$q
./average_movie_universe.py 1 > nightly/averagemovieuniverse.$q

#Actors are relatively uninteresting and relatively large, so don't usually run
# We never look at it, so why burn the energy?
#./average_bacon_universe_watched.py > averagebaconuniverse.watch.$q 
#./average_bacon_universe_quick.py > averagebaconuniverse.quick.$q 
# Will it ever complete?
#./average_bacon_universe_notable.py > averagebaconuniverse.notable.$q
#./average_bacon_universe_note_watch.py > averagebaconuniverse.nw.$qY
