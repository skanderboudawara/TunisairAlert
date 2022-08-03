#!/usr/bin/python3
import tweepy
from pytwitter.get_cred import get_authentification_json


def post_tweet_with_pic(tweet_msg, picture_loc=None):
    """_summary_
    to post a twitter with picture or not
    Args:
        tweet_msg (_type_): the tweet to be posted
        picture_loc (_type_, optional): the path of the picture. Defaults to None.
    """
    twitter_auth_keys = get_authentification_json()
    if twitter_auth_keys["consumer_key"] == "REPLACE_THIS_WITH_YOUR_CONSUMER_KEY":
        print("you need to fill credential.json")
        return

    auth = tweepy.OAuthHandler(
        consumer_key=twitter_auth_keys["consumer_key"],
        consumer_secret=twitter_auth_keys["consumer_secret"],
        access_token=twitter_auth_keys["access_token"],
        access_token_secret=twitter_auth_keys["access_token_secret"],
    )

    api = tweepy.API(auth)

    # Upload image
    if picture_loc is not None:
        media = api.media_upload(picture_loc)
        api.update_status(status=tweet_msg, media_ids=[media.media_id])
    else:
        api.update_status(status=tweet_msg)
