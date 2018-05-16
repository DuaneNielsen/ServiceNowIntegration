# Need to install requests package for python

# easy_install requests

import exitstatus
import requests
import time
import logging
import json
from snow import ServiceNow
from alertmanager import IncidentManager

logging.basicConfig(filename='event_logger',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


event_logger = logging.getLogger('apm_events')

# Set the request parameters

url = 'https://955055.apm.cloud.ca.com:443/apm/appmap/private/graph/recentstatuschanges'
#url =  'https://954976.apm.cloud.ca.com:443/apm/appmap/private/graph/recentstatuschanges'

#proxyKey created from APM security panel

proxyKey = "40c94f7a-ab83-4d5f-92b1-0bf8a6050da8"

#proxyKey = '858d4d13-d71a-48e5-9fbf-a2081527ff5b'

# Eg. Bearer token, created in APM Notifications panel

bearer = 'ffe14126-0493-4af8-8032-3a2626048a8e'

#bearer = '7462cf42-9bbb-4ca1-8f8f-fa1ae00ddebb'

# Set proper headers

headers = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": "Bearer " + bearer}

snow = ServiceNow(hostname='dev28070.service-now.com', user='admin', pwd='Bharath@100')
im = IncidentManager(snow, 'https://cloud.ca.com')

version = 0

#am = IncidentManager()

while True:

    # Do the HTTP request

    response = requests.post(url, headers=headers, json={ "lastVersion" : str(version), "proxyKey" : proxyKey } )

    # Check for HTTP codes other than 200

    if response.status_code != 200:
        print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())
    else:
        data = response.json()
        im.tick(data)

        # Decode the JSON response into a dictionary and use the data


        version = data['version']

        pretty_json = json.dumps(data, indent=4, sort_keys=True)
        event_logger.debug(pretty_json)
        print(pretty_json)

        summary = []
        matched_alerts = []

        pretty_json = json.dumps(summary, indent=4, sort_keys=True)
        event_logger.info(pretty_json)
        print(pretty_json)


    time.sleep(10)