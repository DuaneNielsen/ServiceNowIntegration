# Need to install requests package for python

# easy_install requests

#7462cf42-9bbb-4ca1-8f8f-fa1ae00ddebb

import requests
import json
from xml.etree import ElementTree
import time

def indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem

def printXML(response):
    # Decode the JSON response into a dictionary and use the data
    data = ElementTree.fromstring(response.content)
    indent(data)
    ElementTree.dump(data)

class ServiceNow():

    def __init__(self, hostname, user, pwd):
        self.url = 'https://' + hostname + '/api/now/table/incident'
        self.user = user
        self.pwd = pwd
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.headers_xml = {"Content-Type":"application/xml","Accept":"application/xml"}


    def getIncidents(self):

        # Do the HTTP request
        response = requests.get(url, auth=(user, pwd), headers=self.headers)

        # Check for HTTP codes other than 200
        if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

        # Decode the JSON response into a dictionary and use the data
        data = response.json()
        print(data)

    """
    POST Incident to ServiceNow, expects a python dict as input, eg:
    
    fields = {}
    fields['short_description'] = 'a short description of the incident'
    fields['comments'] = 'some comments'
    
    postIncident(fields)
    
    returns sys_id = the system id of the created incident
     
    """

    def postIncident(self, fields):

        json_fields = json.dumps(fields)

        # Do the HTTP request

        response = requests.post(self.url, auth=(self.user, self.pwd), headers=self.headers, data=json_fields )

        # Check for HTTP codes other than 200

        if response.status_code >= 300:
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:', response.json())

        # Decode the JSON response into a dictionary and use the data

        data = response.json()
        pretty_json = json.dumps(data, indent=4, sort_keys=True)
        print(pretty_json)

        return data['result']['sys_id']


    def updateIncident(self, sys_id, data):

        url = str(self.url + '/' + sys_id)

        # Do the HTTP request
        response = requests.put(url, auth=(self.user, self.pwd), headers=self.headers_xml, data=data)

        # Check for HTTP codes other than 200
        if response.status_code != 200:
            print(url)
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:')
            printXML(response)

        printXML(response)

if __name__ == '__main__':

    # Set the request parameters

    #url = 'https://dev28070.service-now.com/api/now/table/incident'
    url = 'dev28070.service-now.com'

    # Eg. User name="admin", Password="admin" for this code sample.

    user = 'admin'
    pwd = 'Bharath@100'

    snow = ServiceNow(url, user, pwd)


    fields = {}
    fields['short_description'] = 'a short description of the incident'
    fields['comments'] = 'some comments'

    sys_id = snow.postIncident(fields)

    time.sleep(1)

    #sys_id = '9d714e4edb46130054b2ddd0cf96190b'
    data = "<request><entry><comments>Elevating urgency, this is a blocking issue</comments></entry></request>"

    snow.updateIncident(sys_id, data)

