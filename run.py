from snow import ServiceNow
from alertmanager import IncidentManager
from apm_event_poller import APMEventPoller
import yaml
from pprint import pprint

class Config:
    def __init__(self):

        self.apm_host = '955055.apm.cloud.ca.com'
        self.apm_bearer_token = 'ffe14126-0493-4af8-8032-3a2626048a8e'
        self.apm_proxyKey = "40c94f7a-ab83-4d5f-92b1-0bf8a6050da8"
        self.apm_url = 'https://cloud.ca.com'

        self.snow_hostname = 'dev28070.service-now.com'
        self.snow_user = 'admin'
        self.snow_pwd = 'Bharath@100'

        self.incident_cooldown = 3600

    def load(self, filename):
        with open('config.json') as f:
            data = yaml.load(f)

        self.apm_host = data['apm_host']
        self.apm_bearer_token = data['apm_bearer_token']
        self.apm_proxyKey = data['apm_proxyKey']
        self.apm_url = data['apm_url']

        self.snow_hostname = data['snow_hostname']
        self.snow_user = data['snow_hostname']
        self.snow_pwd = data['snow_pwd']
        self.incident_cooldown = float(data['incident_cooldown'])

        pprint(data)

    def getPoller(self):
        snow = ServiceNow(hostname=self.snow_hostname, user=self.snow_user, pwd=self.snow_pwd)
        im = IncidentManager(snow, self.apm_url, cooldown=self.incident_cooldown)
        return APMEventPoller(host=self.apm_host, bearer=self.apm_bearer_token, proxyKey=self.apm_proxyKey, incident_manger=im)


if __name__ == '__main__':
    config = Config()
    config.load('config.json')
    apmPoller = config.getPoller()
    apmPoller.run()