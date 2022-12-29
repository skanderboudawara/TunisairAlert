#!/usr/bin/python3
import tweepy
from src.utils import get_env


def post_tweet_with_pic(tweet_msg, picture_loc=None):
    """
    to post a twitter with picture or not
    Args:
        tweet_msg (_type_): the tweet to be posted
        picture_loc (_type_, optional): the path of the picture. Defaults to None.
    """

    auth = tweepy.OAuthHandler(
        consumer_key=get_env("consumer_key",
        consumer_secret=get_env("consumer_secret"),
        access_token=get_env("access_token"),
        access_token_secret=get_env("access_token_secret"),
    )

    api=tweepy.API(auth)

    # Upload image
    if picture_loc is not None:
        media=api.media_upload(picture_loc)
        api.update_status(status=tweet_msg, media_ids=[media.media_id])
    else:
        api.update_status(status=tweet_msg)
