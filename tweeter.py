#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb as mdb
import sys
import tweepy
from tweepy.error import TweepError
import time
import datetime
from random import randint
from optparse import OptionParser

current_database = "tweeter"
mdb_user = "pontus"
mdb_pass = "cecilia"

options = 0

#
# Connects to the database and returns a connection object to the caller
#
def database_connect():
    try:
        # Currently only local databases are supported
        lcon = mdb.connect('localhost', mdb_user, mdb_pass, current_database)
        return lcon
    except mdb.Error, e:
        print "An error occured while trying to connect to the database '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)
#
# Return the twitter settings
#
def get_twitter_settings():
    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT consumerKey, consumerSecret, accessToken, accessSecret FROM settings")
        settings = cur.fetchone()
        return settings
    except mdb.Error, e:
        print "An error occured while trying to get twitter settings from the database '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)

#
# Get timer settings and return to caller
#
def get_timer_settings():
    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT minTime, maxTime FROM settings")
        settings = cur.fetchone()
        return settings
    except mdb.Error, e:
        print "An error occured while trying to get timer settings from the database '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)

#
# This function retrieves the number of tweets in the tweet table
#
def get_no_tweets():
    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM tweets WHERE enabled = true")
        count = cur.rowcount
        con.close()
        return count
    except mdb.Error, e:
        print "An error occured while trying to get the number of tweets '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)

#
# Gets the tweet defined by the pos parameter.
#
def get_tweet(pos):
    global options

    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM tweets WHERE enabled = true ORDER BY sort")
        rows = cur.fetchall()
        # Get iteration counter, increment it and compare with max iterations
        # Disable tweet if we have reached the maximum number of iterations
        icntr = rows[pos][3] + 1;
        enabled = rows[pos][5];
        if icntr == rows[pos][4]:
            print "Reached the max number of iterations, disabling this tweet"
            enabled = 0

        # Update data base entry with new information
        sqlcmd = "UPDATE tweets SET numIterations='%d', enabled='%d' WHERE tweetID = '%d';" % (icntr, enabled, rows[pos][0])

        print "Executing <%s>" % (sqlcmd)
        # New cursor for the update operation
        upd_cur = con.cursor()
        try:
            upd_cur.execute(sqlcmd)
            con.commit()
        except:
            print "Error on <%s>" % (sqlcmd)

        # Close connection with database
        con.close()

        return rows[pos][2]
    except mdb.Error, e:
        print "An error occured while trying to get a tweet from the database '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)

#
# Get a random hashtag from the database
#
def get_random_hashtag():
    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM hashtags")
        rows = cur.fetchall()
        con.close()
        return rows[randint (0, cur.rowcount-1)]
    except mdb.Error, e:
        print "An error occured while trying to get a hashtag from the database '%d, %s'" % (e.args[0], e.args[1])
        sys.exit(1)

#
# So here's an algorithm that should make it reasonably certain that
# each tweet is pretty unique, without resorting to having some sort of
# time stamp in each tweet.
def sub_rehash_tweet(tweet, tag_level):
    # First check if there are any hashtag tag's in the tweet.
    # Assuming that the sequence "<Tn>" constitues a hastag marker.
    tag_marker = "<T" + '{:0}'.format(tag_level) + ">"
    if tweet.find(tag_marker) != -1:
        # So we found a tag, now replace that with a real hashtag
        hashtag = get_random_hashtag()[1]
        tweet = tweet.replace(tag_marker, "#" + hashtag)
        # Do it again to flush out all tags
        tweet = sub_rehash_tweet (tweet, tag_level + 1)
    # We also check for the <C> tag
    if tweet.find("<C>") != -1:
        time_string = '{:%H:%M}'.format(datetime.datetime.now().time())
        tweet = tweet.replace("<C>", time_string)

    return tweet

def rehash_tweet (tweet):
    tweet = sub_rehash_tweet (tweet, 1) 
    if len (tweet) > 140:
        # We've detected that the tweet probably is to long, we may
        # need to do something about it. And is this really correct,
        # I have a feeling that twitter compress URL's somehow.
        # There should have been something int the API to deal with
        # tweet message lengths.
        print "The tweet is to long"

    return tweet
#
# Main loop, mostly spends its time sleeping. Which is what I should do
# right now =)
#
def main(argv):
    global options

    no_tweets = -1
    cur_tweet = 0
    first = 1

    parser = OptionParser()

	# Option for setting an initial wait
    parser.add_option("-w", "--wait", action="store_true",
                  help="Do an initial random wait period before starting tweeting.", 
                  dest="wait", default=False)

	# Debug option
    parser.add_option("-d", "--debug", action="store_true",
                  help="Run in debug mode, no real tweets and quick timing.", 
                  dest="debug", default=False)

	# Username option
    parser.add_option("-u", "--user", type="string",
                  help="Enter a username for the MySQL database.", 
                  dest="username", default="pontus")

	# Password option
    parser.add_option("-p", "--password", type="string",
                  help="Enter a password for the MySQL database.", 
                  dest="password", default="cecilia")

    options, arguments = parser.parse_args()

    mdb_user = options.username
    mdb_pass = options.password
    
    print "The Magic Tweeter app, Version 0.002"

    try:
        con = database_connect()
        cur = con.cursor()
        cur.execute("SELECT VERSION()")
        print "MySQL version: %s" % cur.fetchone()
        con.close()
    except mdb.Error, e:
        print "An Error occured %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    #
    # Get Twitter access credentials from the database
    consumerKey, consumerSecret, accessToken, accessSecret = get_twitter_settings()
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
    api = tweepy.API(auth)

    print "Twitter User %s\n" % api.me().name

    while 1:
        if first == 1 and options.wait == True:
            # A defensive no spam friendly wait in case we sent out a tweet very close
            # in time to restarting the application.
            minTime, maxTime = get_timer_settings()
            random_time = randint (minTime, maxTime)
            print "Waiting %d seconds before sending the first tweet" % (random_time)
            time.sleep(random_time)
            first = 0

        # Make sure that the current tweet number still is within
        # the total number of tweets in the database
        if no_tweets != get_no_tweets():
            print "The database was updated or we have just started, adjusting parameters!"
            no_tweets = get_no_tweets()
            print "Found %d number of tweets in the database" % no_tweets

        if cur_tweet >= get_no_tweets():
            cur_tweet = 0

        # Get the next tweet and process it.
        tweet_msg = rehash_tweet(get_tweet (cur_tweet))

        try:
            print "Tweeting message: '%s'" % tweet_msg
            if options.debug == False:
	            api.update_status(tweet_msg)
            else:
                print "Psst, did not really tweet that"
        except TweepError, e:
            print "An Error while trying to tweet a message, %s" % (e.reason[1])
            print "I will ignore this and continue with the next message in the queue"

        cur_tweet += 1
	
        #
        # Get timer values from the database
        if options.debug == False:
            minTime, maxTime = get_timer_settings()
        else:
            # When debugging it's quite usefull to see what happens quickly
            minTime = 10
            maxTime = 20

        # Get a random number to create an appropriate wait time
        random_time = randint (minTime, maxTime)
        print "Waiting %d seconds before sending the next tweet" % (random_time)
        time.sleep(random_time)

#
# Call our main function
if __name__ == "__main__":
   main(sys.argv[1:])

