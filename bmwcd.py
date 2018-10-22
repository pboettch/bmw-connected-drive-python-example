#!/usr/bin/env python3


""" Small script showing how to login to BMW Connected Drive to get Vehicle Data associated """

import datetime
import http.client
import json
import time
import urllib

from bmwcdcredentials import BMWCDCredentials

# host is www.bmw-connecteddrive.co.uk or .fr or .de
# <host>/api/vehicle/dynamic/v1/<VIN>
# <host>/api/vehicle/navigation/v1/<VIN>
# <host>/api/vehicle/efficiency/v1/<VIN>
# <host>/api/vehicle/remoteservices/chargingprofile/v1/<VIN>

def main():
    # Get access token from authentication server
    conn = http.client.HTTPSConnection("customer.bmwgroup.com")

    payload = urllib.parse.urlencode( {
        'client_id': 'dbf0a542-ebd1-4ff0-a9a7-55172fbfce35',
        'redirect_uri': 'https://www.bmw-connecteddrive.com/app/static/external-dispatch.html',
        'response_type': 'token',
        'scope': 'authenticate_user fupo',
        'username': BMWCDCredentials.username,
        'password': BMWCDCredentials.password,
    })

    headers = {
            'content-type': 'application/x-www-form-urlencoded',
    }
    conn.request("POST", "/gcdm/oauth/authenticate", payload, headers)

    response = conn.getresponse()
    if response.status != 302:
        print("unexpected HTTP response code", response.status, response.reason)
        return

    hdr = dict(response.getheaders())
    if 'Location' not in hdr:
        print("unexpected: missing 'Location' in Response header")
        return


    loc = urllib.parse.urlsplit(hdr['Location'])
    query = urllib.parse.parse_qs(loc.query)
    fragment = urllib.parse.parse_qs(loc.fragment)

    if 'error' in query:
        print("error during authentification:", query['error'])
        return

    if 'access_token' not in fragment:
        print("unexpected: missing 'AccessToken' in Location-field", fragment)
        return

    access_token = fragment['access_token'][0]

    print("access_token", access_token)

    # Get JSON object with vehicle data from backend server
    conn = http.client.HTTPSConnection("www.bmw-connecteddrive.co.uk")

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36',
        'cache-control': "no-cache",
        'authorization': "Bearer " + access_token,
    }
    conn.request("GET", "/api/vehicle/dynamic/v1/" + BMWCDCredentials.vin, headers=headers)

    response = conn.getresponse()
    json_data = json.loads(response.read())

    print(json_data['attributesMap']['mileage'])

    # Get JSON data (location)
    conn.request("GET", "/api/vehicle/navigation/v1/" + BMWCDCredentials.vin, headers=headers)
    response = conn.getresponse()
    json_data = json.loads(response.read())

    print('latitude {}, longitude {}'.format(json_data['latitude'], json_data['longitude']))


if __name__ == '__main__':
    main()
