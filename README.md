twitter-agent
=============

Simple twitter-agent that tweets announcements from a MySQL database

To run this script you need to have MySQL installed on you system. 
There is currently no code for initializing the database so you need to create the following entry manually.

You need to create a database called "tweeter", this will be used to hold all tables for the application.
The database itself must contain the following three (3) tables:
  * hashtags
  * settings
  * tweets

And each individuall table need to look as follows:

  * hashtags
    -> index (int, autoincrement, pri)
    -> hashTag (char-32 bytes)
  * settings
    -> index (int, autoincrement, pri)
    -> consumerKey (char-255 bytes)
    -> consumerSecret (char-255 bytes)
    -> accessToken (char-255 bytes)
    -> accessSecret (char-255 bytes)
    -> minTime (int)
    -> maxTime (int)
  * tweets
    -> tweetID (int, autoincrement, pri)
    -> tweetMgs (text)

I am lazy and used phpmyadmin to do all the database work.
Here's a sql script that can be executed to generate the current structure.
I should probably keep this in the repo, but will have to do for now.

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;


CREATE TABLE IF NOT EXISTS `hashtags` (
  `index` int(11) NOT NULL AUTO_INCREMENT,
  `hashTag` char(32) NOT NULL,
  PRIMARY KEY (`index`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='A table of different hastags that can be insterted into messages' AUTO_INCREMENT=6 ;

CREATE TABLE IF NOT EXISTS `settings` (
  `index` int(11) NOT NULL AUTO_INCREMENT,
  `consumerKey` char(255) NOT NULL,
  `consumerSecret` char(255) NOT NULL,
  `accessToken` char(255) NOT NULL,
  `accessSecret` char(255) NOT NULL,
  `minTime` int(11) NOT NULL,
  `maxTime` int(11) NOT NULL,
  PRIMARY KEY (`index`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Settings table for the twitter spitter' AUTO_INCREMENT=2 ;

CREATE TABLE IF NOT EXISTS `tweets` (
  `tweetID` int(11) NOT NULL AUTO_INCREMENT,
  `tweetMgs` text NOT NULL,
  PRIMARY KEY (`tweetID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 COMMENT='Basic table for tweets' AUTO_INCREMENT=9 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

All for noe
