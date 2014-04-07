#!/bin/bash
q=`mdate | cut -c6-12`
mysqldump DVDs --user prosfilaes --password > nightly/dbbackup.$q
~/bin/actor_bacon-0.0.1/bin/actor_bacon 8 nightly/actorwscififl.$q nightly/moviewscififl.$q & # more of a test 
~/bin/actor_bacon-0.0.1/bin/actor_bacon 11  nightly/actoranimation.$q nightly/movieanimation.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 9  nightly/actorsingledvd.$q nightly/moviesingledvd.$q 
~/bin/actor_bacon-0.0.1/bin/actor_bacon 6  nightly/actorwfl.$q nightly/moviewfl.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 5  nightly/actorsmallfl.$q nightly/moviesmallfl.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 4  nightly/actorfl.$q nightly/moviefl.$q 
~/bin/actor_bacon-0.0.1/bin/actor_bacon 10 nightly/actorwtv.$q nightly/moviewtv.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 3  nightly/actorwatched.$q nightly/moviewatched.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 7  nightly/actortv.$q nightly/movietv.$q 
~/bin/actor_bacon-0.0.1/bin/actor_bacon 2  nightly/actorsmall.$q nightly/moviesmall.$q &
~/bin/actor_bacon-0.0.1/bin/actor_bacon 1  nightly/actormovie.$q nightly/moviemovie.$q 

