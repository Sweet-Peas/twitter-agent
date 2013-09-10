#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb as mdb
import sys
import tweepy
from tweepy.error import TweepError
import time
import datetime
from random import randint

#
# Connects to the database and returns a connection object to the caller
#
def database_connect():
    try:
        lcon = mdb.connect('localhost', 'tweeter', 'Tweeter', 'tweeter')
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
        cur.execute("SELECT * FROM tweets")
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
    con = database_connect()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM tweets")
        rows = cur.fetchall()
        con.close()
        return rows[pos][1]
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
    no_tweets = -1
    cur_tweet = 0
    print "The Magic Tweeter app, Version 0.001"

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

    #
    # Get timer values from the database
    minTime, maxTime = get_timer_settings()

    print "Twitter User %s\n" % api.me().name

    while 1:
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
        print "Tweeting message: '%s'" % tweet_msg

        try:
            api.update_status(tweet_msg)
        except TweepError, e:
            print "An Error while trying to tweet a message, %s" % (e.reason[1])
            print "I will ignore this and continue with the next message in the queue"

        cur_tweet += 1
	
        # Get a random number to create an appropriate wait time
        random_time = randint (minTime, maxTime)
        time.sleep(random_time)

#
# Call our main function
if __name__ == "__main__":
   main(sys.argv[1:])

