import hashlib
from threading import Timer
import snow

class IncidentManager():

    def __init__(self, snow, apm_url, cooldown):
        self.cooldown = cooldown
        self.alerts = {}
        self.current_incident = None
        self.state = 'CLOSED'
        self.timer = None
        self.snow = snow
        self.apm_url = apm_url

    def key(self, alert):
        return alert['alertName'] + alert['vertex']['name'][0]

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
        relevant_alerts = []

        for current_state in data['items']:
            if current_state['status'] != 'UNKNOWN':
                key = self.key(current_state)
                if key in self.alerts:
                    self.alerts[key] = (self.alerts[key][0], current_state)
                else:
                    self.alerts[key] = (None, current_state)


        for key, alert in self.alerts.iteritems():
            if alert[0]:
                #if the status is not the same as we previously saw
                #then it must have changed
                if alert[0]['status'] != alert[1]['status']:
                    changed = True
                    if alert[1]['status'] == 'OK':
                        relevant_alerts.append(alert[1])
            else:
                # must be the first time we have seen it, so it's changed
                changed = True
                relevant_alerts.append(alert[1])

            if alert[1]['status'] != 'OK':
                allOK = False
                relevant_alerts.append(alert[1])

            #set the prev and current to the same value
            self.alerts[key] = ( self.alerts[key][1], self.alerts[key][1])


        return changed, allOK, relevant_alerts

    def open_new_inident(self, comments):

        print('opening new incident')
        fields = {}
        fields['short_description'] = 'APM Notification'
        fields['comments'] = comments

        self.current_incident = self.snow.postIncident(fields)

    def update_incident(self, comments):

        print('updating incident')
        data = "<request><entry><comments>" + comments + "</comments></entry></request>"

        self.snow.updateIncident(self.current_incident, data)

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

        changed, allOK, alert_list = self.status_changed(data)

        print("changed: " + str(changed) + " allOK: " + str(allOK) )
        for alert in alert_list:
            print('name : ' + self.key(alert) + ' status ' + alert['status'] )

        if self.state == 'CLOSED':
            if changed and not allOK:
                self.open_new_inident(self.formatCommentsJSON(alert_list))
                self.state = 'OPEN'

        elif self.state == 'OPEN':
            self.timer_cancel()
            if changed:
                self.update_incident(self.formatCommentsXML(alert_list))
            if changed and allOK:
                self.state = 'CLOSING'
                self.timer_restart()

        elif self.state == 'CLOSING':
            if changed and not allOK:
                self.timer_cancel()
                self.update_incident(self.formatCommentsXML(alert_list))
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







