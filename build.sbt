name := "Actor_Bacon"

version := "0.0.1"

scalaVersion := "2.10.2"
// scalaVersion := "2.11.0-M8"

libraryDependencies ++= List(
  // use the right Slick version here:
  // "com.typesafe.slick" %% "slick" % "1.0.1",
  "com.typesafe.slick" % "slick_2.10" % "1.0.1",
  "org.slf4j" % "slf4j-simple" % "1.6.4",
  "com.h2database" % "h2" % "1.3.166",
  "mysql" % "mysql-connector-java" % "5.1.27"
  //"org.scalaforge" % "scalax" % "0.1"
)

packageArchetype.java_application
