name := "Actor_Bacon"

version := "0.0.3"

// Don't use -Xfatal-warnings, since Slick apparently problems with extra ()s
scalacOptions ++= Seq("-deprecation", "-feature", "-optimise", "-target:jvm-1.7", "-Xlint", "-Ywarn-dead-code")

libraryDependencies ++= List(
  // use the right Slick version here:
  "com.typesafe.slick" %% "slick" % "1.0.1",
  "org.slf4j" % "slf4j-simple" % "1.6.4",
  "com.h2database" % "h2" % "1.3.166",
  "mysql" % "mysql-connector-java" % "5.1.27"
)

packageArchetype.java_application

// packageDescription in Debian := "Calculates average distances between actors and movies"

// maintainer in Debian := "David Starner"
