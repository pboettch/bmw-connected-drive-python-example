#!/usr/bin/env python3


""" Small script showing how to login to BMW Connected Drive to get Vehicle Data associated """

import datetime
import http.client
import json
import time
import urllib
import os

from bmwcdcredentials import BMWCDCredentials

# host is www.bmw-connecteddrive.co.uk or .fr or .de
# <host>/api/vehicle/dynamic/v1/<VIN>
# <host>/api/vehicle/navigation/v1/<VIN>
# <host>/api/vehicle/efficiency/v1/<VIN>
# <host>/api/vehicle/remoteservices/chargingprofile/v1/<VIN>

def main():

    cachefile = os.environ['HOME'] + '/.bmwcd-access-token.json'

    cache = None

    try:
        with open(cachefile) as f:
            cache = json.load(f)
    except:
        pass

    if cache is None or cache['expiration'] < time.time():
        # Get access token from authentication server
        conn = http.client.HTTPSConnection("customer.bmwgroup.com", timeout=30)

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

        # store cache for later usage
        cache = {
            'token': access_token,
            'expiration' : time.time() + int(fragment['expires_in'][0]),
        }

        with open(cachefile, 'w') as f:
            json.dump(cache, f)
    else:
        access_token = cache['token']

    # Get JSON object with vehicle data from backend server
    conn = http.client.HTTPSConnection("www.bmw-connecteddrive.co.uk", timeout=30)

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36',
        'cache-control': "no-cache",
        'authorization': "Bearer " + access_token,
    }
    conn.request("GET", "/api/vehicle/dynamic/v1/" + BMWCDCredentials.vin, headers=headers)

    response = conn.getresponse()
    json_data = json.loads(response.read().decode('utf-8'))

    print(json_data['attributesMap']['mileage'])

    # Get JSON data (location)
    conn.request("GET", "/api/vehicle/navigation/v1/" + BMWCDCredentials.vin, headers=headers)
    response = conn.getresponse()
    json_data = json.loads(response.read().decode('utf-8'))

    print('latitude {}, longitude {}'.format(json_data['latitude'], json_data['longitude']))


if __name__ == '__main__':
    main()
