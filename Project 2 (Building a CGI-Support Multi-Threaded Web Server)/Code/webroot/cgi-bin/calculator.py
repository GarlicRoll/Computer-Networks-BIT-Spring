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

content_length = int(os.environ.get('CONTENT_LENGTH', 0))
# Read the POST data
post_data = sys.stdin.read(content_length)

cgitb.enable()

print("Content-Type: text/html\r\n\r\n")
print("<html><head><title>Calculator Result</title></head><body>")
print("<h1>Calculator Result</h1>")

try:
    num1 = float(parse_post_data("num1", post_data))
    num2 = float(parse_post_data("num2", post_data))
    operation = parse_post_data("operation", post_data)
    if operation == "add":
        result = num1 + num2
    elif operation == "multiply":
        result = num1 * num2
    else:
        result = "Invalid operation"

    print(f"<p>Result: {result}</p>")
except ValueError:
    print("<p>Invalid input. Please enter numerical values for Number 1 and Number 2.</p>")

print("</body></html>")
