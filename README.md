# dbus-mqtt-ac-charger - Emulates a physical AC Charger from info in MQTT data

**First off, a big thanks to [mr-manuel](https://github.com/mr-manuel) that created a bunch of templates that made this possible**

GitHub repository: [LundSoftwares/venus-os_dbus-mqtt-ac-charger](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac-charger)

### Disclaimer
I'm not responsible for the usage of this script. Use on own risk! 


### Purpose
The script emulates a physical AC Charger in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service com.victronenergy.charger.mqtt_ac_charger with the VRM instance 31.


### Config
Copy or rename the config.sample.ini to config.ini in the dbus-mqtt-ac-charger folder and change it as you need it.


#### JSON structure
<details>
<summary>Minimum required</summary> 
  
```ruby
{
"ac_charger": {
    "ac_current":0,
        "DC0":{
            "current":0
        }
    }
}
```
</details>

<details>
<summary>Minimum required with DC0</summary> 
  
```ruby
{
"ac_charger": {
    "ac_current":0,
        "DC0":{
            "current":0,
            "voltage":0,
            "temperature":0
        }
    }
}
```
</details>

<details>
<summary>Minimum required with DC0 and DC1</summary> 
  
```ruby
{
"ac_charger": {
    "ac_current":0,
        "DC0":{
            "current":0,
            "voltage":0,
            "temperature":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperature": 0
        }
    }
}
```
</details>

<details>
<summary>Minimum required with DC0, DC1 and DC2</summary> 
  
```ruby
{
"ac_charger": {
    "ac_current":0,
        "DC0":{
            "current":0,
            "voltage":0,
            "temperature":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperature": 0
        },
        "DC2": {
            "current": 0,
            "voltage": 0,
            "temperature": 0
        }
    }
}
```
</details>

<details>
<summary>Full</summary> 
  
```ruby
{
"ac_charger": {
    "ac_current":0,
    "ac_power":0,
    "ac_currentlimit":0,
    "state":0,
    "mode":0,
    "errorcode":0,
    "relaystate":0,
    "lowvoltagealarm":0,
    "highvoltagealarm":0,
        "DC0":{
            "current":0,
            "voltage":0,
            "temperature":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperature": 0
        },
        "DC2": {
            "current": 0,
            "voltage": 0,
            "temperature": 0
        }
    }
}
```
</details>


### Install
1. Copy the ```dbus-mqtt-ac-charger``` folder to ```/data/etc``` on your Venus OS device

2. Run ```bash /data/etc/dbus-mqtt-ac-charger/install.sh``` as root

The daemon-tools should start this service automatically within seconds.

### Uninstall
Run ```/data/etc/dbus-mqtt-ac-charger/uninstall.sh```

### Restart
Run ```/data/etc/dbus-mqtt-ac-charger/restart.sh```

### Debugging
The logs can be checked with ```tail -n 100 -F /data/log/dbus-mqtt-ac-charger/current | tai64nlocal```

The service status can be checked with svstat: ```svstat /service/dbus-mqtt-ac-charger```

This will output somethink like ```/service/dbus-mqtt-ac-charger: up (pid 5845) 185 seconds```

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in ```/data/etc/dbus-mqtt-ac-charger/dbus-mqtt-ac-charger.py``` by changing ```level=logging.WARNING``` to ```level=logging.INFO``` or ```level=logging.DEBUG```

If the script stops with the message ```dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid.mqtt_ac-charger"``` it means that the service is still running or another service is using that bus name.

### Multiple instances
It's possible to have multiple instances, but it's not automated. Follow these steps to achieve this:

1. Save the new name to a variable ```driverclone=dbus-mqtt-ac-charger-2```

2. Copy current folder ```cp -r /data/etc/dbus-mqtt-ac-charger/ /data/etc/$driverclone/```

3. Rename the main ```script mv /data/etc/$driverclone/dbus-mqtt-ac-charger.py /data/etc/$driverclone/$driverclone.py```

4. Fix the script references for service and log
```
sed -i 's:dbus-mqtt-ac-charger:'$driverclone':g' /data/etc/$driverclone/service/run
sed -i 's:dbus-mqtt-ac-charger:'$driverclone':g' /data/etc/$driverclone/service/log/run
```
5. Change the ```device_name``` and increase the ```device_instance``` in the ```config.ini```

Now you can install and run the cloned driver. Should you need another instance just increase the number in step 1 and repeat all steps.

### Compatibility
It was tested on Venus OS Large ```v3.01``` on the following devices:

- RaspberryPi 3b+
- Simulated AC Charger data sent from NodeRed

### NodeRed Example code

<details>
<summary>Import into NodeRed runing on your VenusOS device for some simple testing</summary> 
  
```ruby
[{"id":"36b8e7c267cde307","type":"tab","label":"Flow 1","disabled":false,"info":"","env":[]},{"id":"fee581eac3fab0c3","type":"mqtt out","z":"36b8e7c267cde307","name":"","topic":"chargers/ac","qos":"","retain":"","respTopic":"","contentType":"","userProps":"","correl":"","expiry":"","broker":"3cc159c0642d9663","x":730,"y":200,"wires":[]},{"id":"6e400e6ad609538c","type":"function","z":"36b8e7c267cde307","name":"function 1","func":"msg.payload=\n{\n    \"ac_charger\": {\n        \"ac_current\": 5,\n        \"ac_power\": 0,\n        \"ac_currentlimit\": 0,\n        \"state\": 4,\n        \"mode\": 1,\n        \"errorcode\": 0,\n        \"relaystate\": 0,\n        \"lowvoltagealarm\": 0,\n        \"highvoltagealarm\": 0,\n        \"DC0\": {\n            \"current\": 8,\n            \"voltage\": 12.5,\n            \"temperature\": 23\n        },\n        \"DC1\": {\n            \"current\": 10,\n            \"voltage\": 12.8,\n            \"temperature\": 12\n        },\n        \"DC2\": {\n            \"current\": 3,\n            \"voltage\": 12.85,\n            \"temperature\": 23\n        }\n    }\n}\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","libs":[],"x":520,"y":200,"wires":[["fee581eac3fab0c3"]]},{"id":"e64506d8e5edefe0","type":"inject","z":"36b8e7c267cde307","name":"","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"30","crontab":"","once":true,"onceDelay":"1","topic":"","payload":"","payloadType":"date","x":350,"y":200,"wires":[["6e400e6ad609538c"]]},{"id":"3cc159c0642d9663","type":"mqtt-broker","name":"","broker":"localhost","port":"1883","clientid":"","autoConnect":true,"usetls":false,"protocolVersion":"4","keepalive":"60","cleansession":true,"birthTopic":"","birthQos":"0","birthPayload":"","birthMsg":{},"closeTopic":"","closeQos":"0","closePayload":"","closeMsg":{},"willTopic":"","willQos":"0","willPayload":"","willMsg":{},"userProps":"","sessionExpiry":""}]
```
</details>






### Screenshots

<details>
<summary>With DC0</summary> 
  
![Skärmbild 2023-08-19 101420](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger/assets/23386303/b75ccca2-c317-4f9f-b16a-1006872f8e03)

</details>

<details>
<summary>With DC0 and DC1</summary> 
  
![Skärmbild 2023-08-19 101638](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger/assets/23386303/2043bdfe-2cb7-4403-92b1-1c92294a4394)

</details>

<details>
<summary>With DC0, DC1 and DC3</summary> 
  
![Skärmbild 2023-08-19 101735](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger/assets/23386303/096c135c-8ea8-45e9-83f9-0b517209e8fa)

</details>

<details>
<summary>Full</summary> 
  
![Skärmbild 2023-08-19 101950](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger/assets/23386303/3c6474e8-d473-4f8b-9769-5a1d6886e812)
![Skärmbild 2023-08-19 103433](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger/assets/23386303/a770d74f-c88c-4f73-9b89-eb0f7fdb6e46)


</details>


# Sponsor this project

<a href="https://www.paypal.com/donate/?business=MTXQ49TG6YH36&no_recurring=0&item_name=Like+my+work?+%0APlease+buy+me+a+coffee...&currency_code=SEK">
  <img src="https://pics.paypal.com/00/s/MjMyYjAwMjktM2NhMy00NjViLTg3N2ItMDliNjY3MjhiOTJk/file.PNG" alt="Donate with PayPal" />
</a>
