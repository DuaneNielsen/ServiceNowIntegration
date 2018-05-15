#Need to install requests package for python
#easy_install requests
import requests



class SNOWIncidentManager:

    def init(self, url, user, pwd):
        self.url = url
        self.user = user
        self.pwd = pwd


    def getIncidents():
        # Set proper headers
        headers = {"Content-Type":"application/json","Accept":"application/json"}

        # Do the HTTP request
        response = requests.get(url, auth=(user, pwd), headers=headers  )

        # Check for HTTP codes other than 200
        if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json())
            exit()

        # Decode the JSON response into a dictionary and use the data
        data = response.json()
        print(data)


if __name__ == '__main__':

    # Set the request parameters
    url = 'https://dev22277.service-now.com/api/now/table/incident?sysparm_limit=5'

    # Eg. User name="admin", Password="admin" for this code sample.
    user = 'admin'
    pwd = 'yfu6WjF9lSND'

    snow = SNOWIncidentManager(url, user, pwd)
