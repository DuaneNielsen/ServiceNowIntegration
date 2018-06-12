# APM SAAS ServiceNOW integration

![Alt Text](https://thumbs.gfycat.com/ThatHorribleDesertpupfish-size_restricted.gif)


<iframe src='https://gfycat.com/ifr/ThatHorribleDesertpupfish' frameborder='0' scrolling='no' width='2560' height='1440' allowfullscreen></iframe>

### Install Instructions

Requires Python 2.7

set properties in config.json

```
  "apm_host" : "<host_id>.apm.cloud.ca.com",
  "apm_bearer_token" : "<from apm config>",
  "apm_proxyKey" : "<from notifications panel>",
  "apm_url" : "https://cloud.ca.com",
  "snow_hostname" : "<your ServiceNow host address>",
  "snow_user" : "<your snow userid>",
  "snow_pwd" : "password",
  "incident_cooldown" : "3600"
```

install the dependencies

```buildoutcfg
python setup.py install
```

run the script
```buildoutcfg
python run.py
```