import hashlib
from threading import Timer
import snow

class IncidentManager():

    def __init__(self, snow, apm_url, cooldown):
        self.cooldown = 30.0
        self.alerts = {}
        self.current_incident = None
        self.state = 'CLOSED'
        self.timer = None
        self.snow = snow
        self.apm_url = apm_url

    def hashkey(self, alert):
        matter = alert['alertName'] + alert['vertex']['name'][0]
        return hashlib.sha224(matter).hexdigest()

    def timer_restart(self):
        self.timer_cancel()
        self.timer = Timer(self.cooldown, self.timer_elapsed)
        self.timer.start()
        print 'timer set'

    def timer_cancel(self):
        if self.timer is not None:
            self.timer.cancel()
            print 'cancelled timer'

    def timer_elapsed(self):
        self.state = 'CLOSED'
        print(self.state)

    def status_changed(self, data):

        changed = False
        allOK = True
        updated = []

        for source in data['items']:
            if source['status'] != 'UNKNOWN':
                key = self.hashkey(source)
                new_state = source['status']

                if new_state != 'OK':
                    allOK = False

                if key in self.alerts:
                    prev_state = self.alerts[key]['status']
                    if prev_state != new_state:
                        changed = True
                        updated.append(source)

                else:
                    # we have not seen this alert before, so it is a change
                    updated.append(source)
                    changed = True

                self.alerts[key] = source

        return changed, allOK, updated

    def open_new_inident(self, comments):

        print('opening new incident')
        fields = {}
        fields['short_description'] = 'APM Notification'
        fields['comments'] = comments

        self.current_incident = snow.postIncident(fields)

    def update_incident(self, comments):

        print('updating incident')
        data = "<request><entry><comments>" + comments + "</comments></entry></request>"

        snow.updateIncident(self.current_incident, data)

    def stripSaaS(self, alertName):
        alerts = alertName.split(':')
        if alerts[0] == 'SuperDomain':
            return alerts[2]
        else:
            return alertName

    def formatData(self, data, newline_seq):
        datastring = newline_seq
        for alert in data:
            datastring += alert['status'] + '  '
            datastring += self.stripSaaS(alert['alertName'])  + '  '
            if alert['vertex'] is not None:
                datastring += alert['vertex']['hostname'][0] + '  '
            datastring += newline_seq
        return datastring

    def formatCommentsJSON(self, data):
        datastring = self.formatData(data, '<br/>')
        return '[code]<a title="CA APM" href="'+ self.apm_url + '">View in CA APM</a>[/code]'+ datastring

    def formatCommentsXML(self, data):
        datastring = self.formatData(data, '<![CDATA[<br/>]]>')
        return '<![CDATA[code]<a title="CA APM" href="'+ self.apm_url + '">View in CA APM</a>[/code]]]>' + datastring

    def tick(self, data):

        alert = {}

        changed, allOK, updated = self.status_changed(data)

        if self.state == 'CLOSED':
            if changed and not allOK:
                self.open_new_inident(self.formatCommentsJSON(updated))
                self.state = 'OPEN'

        elif self.state == 'OPEN':
            self.timer_cancel()
            if changed:
                self.update_incident(self.formatCommentsXML(updated))
            if allOK:
                self.state = 'CLOSING'
                self.timer_restart()

        elif self.state == 'CLOSING':
            if changed and not allOK:
                self.timer_cancel()
                self.update_incident(self.formatCommentsXML(updated))
                self.state = 'OPEN'

        print self.state

if __name__ == '__main__':

    snow = snow.ServiceNow(hostname='dev28070.service-now.com', user='admin', pwd='Bharath@100')

    im = IncidentManager(snow, 'https://cloud.ca.com')

    import json
    import yaml
    from pprint import pprint
    import time

    with open('testdata.json') as f:
        data = yaml.load(f)

    pprint(data)

    from time import time

    prev = time()
    while True:

        def step():

            im.tick(data)

            data['items'][0]['status'] = 'OK'
            im.tick(data)

            data['items'][0]['status'] = 'WARNING'
            im.tick(data)
            assert (im.state == 'OPEN')

            data['items'][0]['status'] = 'DANGER'
            im.tick(data)
            assert (im.state == 'OPEN')

            data['items'][0]['status'] = 'OK'
            im.tick(data)
            assert (im.state == 'CLOSING')

            data['items'][0]['status'] = 'WARNING'
            im.tick(data)
            assert (im.state == 'OPEN')

            data['items'][0]['status'] = 'OK'
            im.tick(data)
            assert (im.state == 'CLOSING')

        now = time()
        if now - prev > 5:
            step()
            prev = now
        else:
            pass
            # runs







