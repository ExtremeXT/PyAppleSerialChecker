# Copyright © 2023 ExtremeXT. Licensed under the GNU Affero General Public License v3.0. See LICENSE for details.

import base64
import json
import requests

serial_number = input("Input the serial number: ")

# Spoof user agent to Safari browser on macOS 13.5
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"

# Get auth token from main page
url = "https://checkcoverage.apple.com"
headers = {"User-Agent": user_agent}
response = requests.get(url, headers=headers)

try:
    auth_token = response.headers['X-APPLE-AUTH-TOKEN']
except KeyError:
    print("Could not fetch authentification token cause of rate limit!")
    exit()

# Get captcha in base64
url = "https://checkcoverage.apple.com/api/v1/facade/captcha?type=image"
headers = {
    "X-Apple-Auth-Token": auth_token,
    "User-Agent": user_agent,
    # Set the accept type as json to get the base64 encoded captcha properly
    "Accept": "application/json",
}
response = requests.get(url, headers=headers)
captcha = base64.b64decode(json.loads(response.content)["binaryValue"])

# Write captcha to file
with open("captcha.png", "wb") as f:
    f.write(captcha)

captcha_answer = input("Input the captcha answer: ")

# Get serial status
url = "https://checkcoverage.apple.com/api/v1/facade/coverage"
headers = {"X-Apple-Auth-Token": auth_token, "User-Agent": user_agent}
json = {
    "captchaAnswer": captcha_answer,
    "captchaType": "image",
    "serialNumber": serial_number,
}
response = requests.post(url, headers=headers, json=json)

if b"Sorry. The code you entered doesn" in response.content:
    print("Captcha is invalid, please try again!")
elif b"Please enter a valid serial number." in response.content:
    print("Serial is invalid, safe to use!")
elif b"Sign in to update purchase date" in response.content:
    print("Serial is: Unable to verified purchase date, please regenerate!")
elif b"Your coverage includes the following benefits" or b"Coverage Expired" in response.content:
    print("Serial is: Fully valid, please regenerate!")
else:
    print("Unknown error occurred!")
