import os
import re


def parse_post_data(name, post_data):
    # Read the content length
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    if content_length > 0:
        # Parse the POST data
        post_fields = re.split(r'=|&', post_data)
        try:
            id_name = post_fields.index(name)
        except ValueError:
            print('Invalid post value')
            return -1
        post_value = post_fields[id_name + 1]
        return post_value
    return -1
