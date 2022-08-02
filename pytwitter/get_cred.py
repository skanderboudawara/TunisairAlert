#!/usr/bin/python
import json
import os
from utils.utility import FileFolderManager

# See tutorial: https://www.mattcrampton.com/blog/step_by_step_tutorial_to_post_to_twitter_using_python_part_two-posting_with_photos/


def get_authentification_json():
    """_summary_
    will get the twitter credential
    Returns:
        _type_: the dictionnary of the JSON
    """
    default_dic = {
        "consumer_key": "REPLACE_THIS_WITH_YOUR_CONSUMER_KEY",
        "consumer_secret": "REPLACE_THIS_WITH_YOUR_CONSUMER_SECRET",
        "access_token": "REPLACE_THIS_WITH_YOUR_ACCESS_TOKEN",
        "access_token_secret": "REPLACE_THIS_WITH_YOUR_ACCESS_TOKEN_SECRET",
    }
    return FileFolderManager("credentials", "credential.json").read_json(default_dic)
