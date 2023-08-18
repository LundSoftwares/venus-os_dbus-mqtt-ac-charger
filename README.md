# dbus-mqtt-ac_charger - Emulates a physical AC Charger from info in MQTT data

**First off, a big thanks to [mr-manuel](https://github.com/mr-manuel) that created a bunch of templates that made this possible**

GitHub repository: [LundSoftwares/venus-os_dbus-mqtt-ac_charger](https://github.com/LundSoftwares/venus-os_dbus-mqtt-ac_charger)

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
            "temperture":0
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
            "temperture":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperture": 0
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
            "temperture":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperture": 0
        },
        "DC2": {
            "current": 0,
            "voltage": 0,
            "temperture": 0
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
            "temperture":0
        },
        "DC1": {
            "current": 0,
            "voltage": 0,
            "temperture": 0
        },
        "DC2": {
            "current": 0,
            "voltage": 0,
            "temperture": 0
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

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in ```/data/etc/dbus-mqtt-grid/dbus-mqtt-ac-charger.py``` by changing ```level=logging.WARNING``` to ```level=logging.INFO``` or ```level=logging.DEBUG```

If the script stops with the message ```dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.grid.mqtt_ac-charger"``` it means that the service is still running or another service is using that bus name.

### Multiple instances
It's possible to have multiple instances, but it's not automated. Follow these steps to achieve this:

1. Save the new name to a variable ```driverclone=dbus-mqtt-ac-charger-2```

2. Copy current folder ```cp -r /data/etc/dbus-mqtt-ac-charger/ /data/etc/$driverclone/```

3. Rename the main ```script mv /data/etc/$driverclone/dbus-mqtt-ac-charger.py /data/etc/$driverclone/$driverclone.py```

4. Fix the script references for service and log
```
sed -i 's:dbus-mqtt-grid:'$driverclone':g' /data/etc/$driverclone/service/run
sed -i 's:dbus-mqtt-grid:'$driverclone':g' /data/etc/$driverclone/service/log/run
```
5. Change the ```device_nam0```e and increase the ```device_instance``` in the ```config.ini```

Now you can install and run the cloned driver. Should you need another instance just increase the number in step 1 and repeat all steps.

### Compatibility
It was tested on Venus OS Large ```v3.01``` on the following devices:

RaspberryPi 3b+

### Screenshots


