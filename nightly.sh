#!/bin/bash
q=`mdate | cut -c6-12`
mysqldump DVDs --user prosfilaes --password > nightly/dbbackup.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 35  nightly/actorfltv.$q nightly/moviefltv.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 20 nightly/actormidnite.$q nightly/moviemidnite.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 19 nightly/actordecades.$q nightly/moviedecades.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 18 nightly/actoritalian.$q nightly/movieitalian.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 13 nightly/actorscififl.$q nightly/moviescififl.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 14 nightly/actorlargep.$q nightly/movielargep.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 15 nightly/actor50movies.$q nightly/movie50movies.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 21 nightly/actor1910s.$q nightly/movie1910s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 22 nightly/actor1920s.$q nightly/movie1920s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 23 nightly/actor1930s.$q nightly/movie1930s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 24 nightly/actor1940s.$q nightly/movie1940s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 25 nightly/actor1950s.$q nightly/movie1950s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 26 nightly/actor1960s.$q nightly/movie1960s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 27 nightly/actor1970s.$q nightly/movie1970s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 28 nightly/actor1980s.$q nightly/movie1980s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 29 nightly/actor1990s.$q nightly/movie1990s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 30 nightly/actor2000s.$q nightly/movie2000s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 31 nightly/actor2010s.$q nightly/movie2010s.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 8 nightly/actorwscififl.$q nightly/moviewscififl.$q  # more of a test 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 11  nightly/actoranimation.$q nightly/movieanimation.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 9  nightly/actorsingledvd.$q nightly/moviesingledvd.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 12 SHOULD_NOT_APPEAR nightly/moviedouble.$q # defined only for movies
~/bin/actor_bacon-0.0.3/bin/actor_bacon 6  nightly/actorwfl.$q nightly/moviewfl.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 5  nightly/actorsmallfl.$q nightly/moviesmallfl.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 4  nightly/actorfl.$q nightly/moviefl.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 10 nightly/actorwtv.$q nightly/moviewtv.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 3  nightly/actorwatched.$q nightly/moviewatched.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 16 nightly/actorunmixed.$q nightly/movieunmixed.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 17 nightly/actorunmixedfl.$q nightly/movieunmixedfl.$q
~/bin/actor_bacon-0.0.3/bin/actor_bacon 7  nightly/actortv.$q nightly/movietv.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 2  nightly/actorsmall.$q nightly/moviesmall.$q 
~/bin/actor_bacon-0.0.3/bin/actor_bacon 1  nightly/actormovie.$q nightly/moviemovie.$q 
