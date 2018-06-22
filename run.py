from snow import ServiceNow
from alertmanager import IncidentManager
from apm_event_poller import APMEventPoller
import yaml
from pprint import pprint

class Config:
    def __init__(self):

        self.apm_host = None
        self.apm_bearer_token = None
        self.apm_proxyKey = None
        self.apm_url = 'https://cloud.ca.com'

        self.snow_hostname = None
        self.snow_user = None
        self.snow_pwd = None

        self.incident_cooldown = 3600

    @staticmethod
    def load(filename):
        with open('config.json') as f:
            data = yaml.load(f)
        config = Config()

        config.apm_host = data['apm_host']
        config.apm_bearer_token = data['apm_bearer_token']
        config.apm_proxyKey = data['apm_proxyKey']
        config.apm_url = data['apm_url']

        config.snow_hostname = data['snow_hostname']
        config.snow_user = data['snow_user']
        config.snow_pwd = data['snow_pwd']
        config.incident_cooldown = float(data['incident_cooldown'])

        pprint(data)
        return config

    def getPoller(self):
        snow = ServiceNow(hostname=self.snow_hostname, user=self.snow_user, pwd=self.snow_pwd)
        im = IncidentManager(snow, self.apm_url, cooldown=self.incident_cooldown)
        return APMEventPoller(host=self.apm_host, bearer=self.apm_bearer_token, proxyKey=self.apm_proxyKey, incident_manger=im)


if __name__ == '__main__':
    config = Config.load('config.json')
    apmPoller = config.getPoller()
    apmPoller.run()