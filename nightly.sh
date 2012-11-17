#!/bin/bash
q=`mdate | cut -c6-12`
mysqldump DVDs --user dvdeug --password > dbbackup.$q
# We've update the actor's table, but not all programs
#./average_bacon_universe_note_watch.py > averagebaconuniverse.nw.$q
./average_tv_universe.py > averagetvuniverse.$q
./average_wfl_universe.py > averagewfluniverse.$q
./average_watched_universe.py > averagewatcheduniverse.$q
./average_smalldvd.py > averagesmalluniverse.$q
./average_fulllength_universe.py > averagefluniverse.$q
./average_movie_universe.py > averagemovieuniverse.$q
# We never look at it, so why burn the energy?
#./average_bacon_universe_watched.py > averagebaconuniverse.watch.$q 
#./average_bacon_universe_quick.py > averagebaconuniverse.quick.$q 
# Will it ever complete?
#./average_bacon_universe_notable.py > averagebaconuniverse.notable.$q
