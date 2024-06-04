#!/usr/bin/env python

import cgitb
import os
import sys
import warnings
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


warnings.filterwarnings("ignore", category=DeprecationWarning)

cgitb.enable()

content_length = int(os.environ.get('CONTENT_LENGTH', 0))
# Read the POST data
post_data = sys.stdin.read(content_length)

print("Content-Type: text/html\r\n\r\n")
print("<html><head><title>Data Query Result</title></head><body>")
print("<h1>Data Query Result</h1>")

# Retrieve the value of 'query'
query = parse_post_data("query", post_data)

# Check if query is provided
if query:
    # Simulate a database query response
    result = f"Result for query: {query}"
    print(f"<p>{result}</p>")
else:
    print("<p>Please provide a query.</p>")

print("</body></html>")
