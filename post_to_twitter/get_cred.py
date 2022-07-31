import json
import os
# See tutorial: https://www.mattcrampton.com/blog/step_by_step_tutorial_to_post_to_twitter_using_python_part_two-posting_with_photos/


def get_authentification_json():
    path_to_credential = os.path.join(
        os.path.abspath(os.curdir), 'credential.json')
    if os.path.isfile(path_to_credential):
        with open(path_to_credential) as f:
            return json.load(f)
    else:
        default_dic = {
            "consumer_key": "REPLACE_THIS_WITH_YOUR_CONSUMER_KEY",
            "consumer_secret": "REPLACE_THIS_WITH_YOUR_CONSUMER_SECRET",
            "access_token": "REPLACE_THIS_WITH_YOUR_ACCESS_TOKEN",
            "access_token_secret": "REPLACE_THIS_WITH_YOUR_ACCESS_TOKEN_SECRET"
        }
        with open(path_to_credential, 'w') as f:
            json.dump(default_dic, f)
        return {}