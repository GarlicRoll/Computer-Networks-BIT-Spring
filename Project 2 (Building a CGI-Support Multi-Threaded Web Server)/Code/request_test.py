import requests

# Define the URL and payload
url = "http://localhost:8888/cgi-bin/data_query.py"
payload = {'query': '32'}

# Define the headers including Authorization
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Authorization': 'Bearer default_token'
}

# Send the POST request
response = requests.post(url, data=payload, headers=headers)

# Print the response status code and text
print(f'Status Code: {response.status_code}')
print(f'Response Text: {response.text}')