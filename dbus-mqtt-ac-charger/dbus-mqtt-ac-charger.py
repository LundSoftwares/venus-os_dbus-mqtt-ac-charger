#!/usr/bin/env python

from gi.repository import GLib  # pyright: ignore[reportMissingImports]
import platform
import logging
import sys
import os
from time import sleep, time
import json
import paho.mqtt.client as mqtt
import configparser  # for config/ini file
import _thread

# import Victron Energy packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService


# get values from config.ini file
try:
    config_file = (os.path.dirname(os.path.realpath(__file__))) + "/config.ini"
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if config["MQTT"]["broker_address"] == "IP_ADDR_OR_FQDN":
            print(
                'ERROR:The "config.ini" is using invalid default values like IP_ADDR_OR_FQDN. The driver restarts in 60 seconds.'
            )
            sleep(60)
            sys.exit()
    else:
        print(
            'ERROR:The "'
            + config_file
            + '" is not found. Did you copy or rename the "config.sample.ini" to "config.ini"? The driver restarts in 60 seconds.'
        )
        sleep(60)
        sys.exit()

except Exception:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    file = exception_traceback.tb_frame.f_code.co_filename
    line = exception_traceback.tb_lineno
    print(
        f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}"
    )
    print("ERROR:The driver restarts in 60 seconds.")
    sleep(60)
    sys.exit()


# Get logging level from config.ini
# ERROR = shows errors only
# WARNING = shows ERROR and warnings
# INFO = shows WARNING and running functions
# DEBUG = shows INFO and data/values
if "DEFAULT" in config and "logging" in config["DEFAULT"]:
    if config["DEFAULT"]["logging"] == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif config["DEFAULT"]["logging"] == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif config["DEFAULT"]["logging"] == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.WARNING)


# get timeout
if "DEFAULT" in config and "timeout" in config["DEFAULT"]:
    timeout = int(config["DEFAULT"]["timeout"])
else:
    timeout = 60


# set variables
connected = 0
last_changed = 0
last_updated = 0

charger_ac_power = 0
charger_ac_current = 0
charger_ac_currentlimit = 0

charger_nr_outputs = 1
charger_DC0_voltage = 0
charger_DC0_current = -1
charger_DC0_temperature = 0
charger_DC1_voltage = 0
charger_DC1_current = 0
charger_DC1_temperature = 0
charger_DC2_voltage = 0
charger_DC2_current = 0
charger_DC2_temperature = 0

charger_state = 0
charger_mode = 4
charger_errorcode = 0
charger_relaystate = 0
charger_LowVoltageAlarm = 0
charger_HighVoltageAlarm = 0


# MQTT requests
def on_disconnect(client, userdata, rc):
    global connected
    logging.warning("MQTT client: Got disconnected")
    if rc != 0:
        logging.warning(
            "MQTT client: Unexpected MQTT disconnection. Will auto-reconnect"
        )
    else:
        logging.warning("MQTT client: rc value:" + str(rc))

    while connected == 0:
        try:
            logging.warning("MQTT client: Trying to reconnect")
            client.connect(config["MQTT"]["broker_address"])
            connected = 1
        except Exception as err:
            logging.error(
                f"MQTT client: Error in retrying to connect with broker ({config['MQTT']['broker_address']}:{config['MQTT']['broker_port']}): {err}"
            )
            logging.error("MQTT client: Retrying in 15 seconds")
            connected = 0
            sleep(15)


def on_connect(client, userdata, flags, rc):
    global connected
    if rc == 0:
        logging.info("MQTT client: Connected to MQTT broker!")
        connected = 1
        client.subscribe(config["MQTT"]["topic"])
    else:
        logging.error("MQTT client: Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:
        global last_changed,charger_ac_power,charger_ac_current,charger_ac_currentlimit,charger_nr_outputs,charger_DC0_voltage,charger_DC0_current,charger_DC0_temperature,charger_DC1_voltage,charger_DC1_current,charger_DC1_temperature,charger_DC2_voltage,charger_DC2_current,charger_DC2_temperature,charger_state,charger_mode,charger_errorcode,charger_relaystate,charger_LowVoltageAlarm,charger_HighVoltageAlarm

        # get JSON from topic
        if msg.topic == config["MQTT"]["topic"]:
            if msg.payload != "" and msg.payload != b"":
                jsonpayload = json.loads(msg.payload)

                last_changed = int(time())

                if "ac_charger" in jsonpayload:
                    if (
                        type(jsonpayload["ac_charger"]) == dict
                        and "ac_current" in jsonpayload["ac_charger"]
                    ):
                        charger_ac_current = float(jsonpayload["ac_charger"]["ac_current"])
                        charger_ac_power = (
                            float(jsonpayload["ac_charger"]["ac_power"])
                            if "ac_power" in jsonpayload["ac_charger"]
                            else charger_ac_current * float(config["DEFAULT"]["voltage"])
                        )
                        charger_ac_currentlimit = (
                            float(jsonpayload["ac_charger"]["ac_currentlimit"])
                            if "ac_currentlimit" in jsonpayload["ac_charger"]
                            else None
                        )                        
                        charger_state = (
                            float(jsonpayload["ac_charger"]["state"])
                            if "state" in jsonpayload["ac_charger"]
                            else None
                        )                       
                        charger_mode = (
                            float(jsonpayload["ac_charger"]["mode"])
                            if "mode" in jsonpayload["ac_charger"]
                            else 1
                        )   
                        charger_errorcode = (
                            float(jsonpayload["ac_charger"]["errorcode"])
                            if "errorcode" in jsonpayload["ac_charger"]
                            else 0
                        )    
                        charger_relaystate = (
                            float(jsonpayload["ac_charger"]["relaystate"])
                            if "relaystate" in jsonpayload["ac_charger"]
                            else None
                        )    
                        charger_LowVoltageAlarm = (
                            float(jsonpayload["ac_charger"]["lowvoltagealarm"])
                            if "lowvoltagealarm" in jsonpayload["ac_charger"]
                            else None
                        )    
                        charger_HighVoltageAlarm = (
                            float(jsonpayload["ac_charger"]["highvoltagealarm"])
                            if "highvoltagealarm" in jsonpayload["ac_charger"]
                            else None
                        )   
                        
                      
                        
                        # check if DC0 and DC0 -> current exists
                        if (
                            "DC0" in jsonpayload["ac_charger"]
                            and "current" in jsonpayload["ac_charger"]["DC0"]
                        ):
                            charger_nr_outputs = 1
                            charger_DC0_current = float(jsonpayload["ac_charger"]["DC0"]["current"])
                            charger_DC0_voltage = (
                                float(jsonpayload["ac_charger"]["DC0"]["voltage"])
                                if "voltage" in jsonpayload["ac_charger"]["DC0"]
                                else 0
                            )
                            charger_DC0_temperature = (
                                float(jsonpayload["ac_charger"]["DC0"]["temperature"])
                                if "temperature" in jsonpayload["ac_charger"]["DC0"]
                                else 0
                            )
                            
                        # check if DC1 and DC1 -> current exists
                        if (
                            "DC1" in jsonpayload["ac_charger"]
                            and "current" in jsonpayload["ac_charger"]["DC1"]
                        ):
                            charger_nr_outputs = 2
                            charger_DC1_current = float(jsonpayload["ac_charger"]["DC1"]["current"])
                            charger_DC1_voltage = (
                                float(jsonpayload["ac_charger"]["DC1"]["voltage"])
                                if "voltage" in jsonpayload["ac_charger"]["DC1"]
                                else 0
                            )
                            charger_DC1_temperature = (
                                float(jsonpayload["ac_charger"]["DC1"]["temperature"])
                                if "temperature" in jsonpayload["ac_charger"]["DC1"]
                                else 0
                            )


                         # check if DC2 and DC2 -> current exists
                        if (
                            "DC2" in jsonpayload["ac_charger"]
                            and "current" in jsonpayload["ac_charger"]["DC2"]
                        ):
                            charger_nr_outputs = 3
                            charger_DC2_current = float(jsonpayload["ac_charger"]["DC2"]["current"])
                            charger_DC2_voltage = (
                                float(jsonpayload["ac_charger"]["DC2"]["voltage"])
                                if "voltage" in jsonpayload["ac_charger"]["DC2"]
                                else 0
                            )
                            charger_DC2_temperature = (
                                float(jsonpayload["ac_charger"]["DC2"]["temperature"])
                                if "temperature" in jsonpayload["ac_charger"]["DC2"]
                                else 0
                            )
                    else:
                        logging.error(
                            'Received JSON MQTT message does not include an ac_power object in the ac_charger object. Expected at least: {"ac_charger": {"ac_power": 0.0}"}'
                        )
                        logging.debug("MQTT payload: " + str(msg.payload)[1:])
                else:
                    logging.error(
                        'Received JSON MQTT message does not include a ac_charger object. Expected at least: {"ac_charger": {"ac_power": 0.0}"}'
                    )
                    logging.debug("MQTT payload: " + str(msg.payload)[1:])

            else:
                logging.warning(
                    "Received JSON MQTT message was empty and therefore it was ignored"
                )
                logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except ValueError as e:
        logging.error("Received message is not a valid JSON. %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except Exception as e:
        logging.error("Exception occurred: %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])


class DbusMqttAcChargerService:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT AC Charger",
        customname="MQTT AC Charger",
        connection="MQTT AC Charger service",
    ):
        self._dbusservice = VeDbusService(servicename)
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", "0.1.0 (20230818)")
        # self._dbusservice.add_path('/HardwareVersion', '')
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Latency", None)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["initial"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global last_changed, last_updated

        now = int(time())

        if last_changed != last_updated:
            self._dbusservice["/Ac/In/L1/I"] = (
                round(charger_ac_current, 2) if charger_ac_current is not None else None
            )
            self._dbusservice["/Ac/In/L1/P"] = (
                round(charger_ac_power, 2) if charger_ac_power is not None else None
            )
            self._dbusservice["/Ac/In/CurrentLimit"] = (
                round(charger_ac_currentlimit, 2) if charger_ac_currentlimit is not None else None
            )
            self._dbusservice["/NrOfOutputs"] = (
                round(charger_nr_outputs, 0) if charger_nr_outputs is not None else None
            )
            self._dbusservice["/State"] = (
                round(charger_state, 0) if charger_state is not None else None
            )
            self._dbusservice["/Mode"] = (
                round(charger_mode, 0) if charger_mode is not None else None
            )
            self._dbusservice["/ErrorCode"] = (
                round(charger_errorcode, 0) if charger_errorcode is not None else None
            )
            self._dbusservice["/Relay/0/State"] = (
                round(charger_relaystate, 0) if charger_relaystate is not None else None
            )
            self._dbusservice["/Alarms/LowVoltage"] = (
                round(charger_LowVoltageAlarm, 0) if charger_LowVoltageAlarm is not None else None
            )
            self._dbusservice["/Alarms/HighVoltage"] = (
                round(charger_HighVoltageAlarm, 0) if charger_HighVoltageAlarm is not None else None
            )

            if charger_DC0_current is not None:
                self._dbusservice["/Dc/0/Current"] = (
                    round(charger_DC0_current, 2) if charger_DC0_current is not None else None
                )
                self._dbusservice["/Dc/0/Voltage"] = (
                    round(charger_DC0_voltage, 2) if charger_DC0_voltage is not 0 else None
                )
                self._dbusservice["/Dc/0/Temperature"] = (
                    round(charger_DC0_temperature, 2) if charger_DC0_temperature is not 0 else None
                )
                
            if charger_DC1_current is not None:
                self._dbusservice["/Dc/1/Current"] = (
                    round(charger_DC1_current, 2) if charger_DC1_current is not None else None
                )
                self._dbusservice["/Dc/1/Voltage"] = (
                    round(charger_DC1_voltage, 2) if charger_DC1_voltage is not 0 else None
                )
                self._dbusservice["/Dc/1/Temperature"] = (
                    round(charger_DC1_temperature, 2) if charger_DC1_temperature is not 0 else None
                )
                
            if charger_DC2_current is not None:
                self._dbusservice["/Dc/2/Current"] = (
                    round(charger_DC2_current, 2) if charger_DC2_current is not None else None
                )
                self._dbusservice["/Dc/2/Voltage"] = (
                    round(charger_DC2_voltage, 2) if charger_DC2_voltage is not 0 else None
                )
                self._dbusservice["/Dc/2/Temperature"] = (
                    round(charger_DC2_temperature, 2) if charger_DC2_temperature is not 0 else None
                )                


            if charger_DC0_current:
                logging.debug(
                    "|- DC1: {:.1f} A - {:.1f} V - {:.1f} °C".format(
                        charger_DC0_current, charger_DC0_voltage, charger_DC0_temperature
                    )
                )
            
            if charger_DC1_current:
                logging.debug(
                    "|- DC1: {:.1f} A - {:.1f} V - {:.1f} °C".format(
                        charger_DC1_current, charger_DC1_voltage, charger_DC1_temperature
                    )
                )
            if charger_DC2_current:
                logging.debug(
                    "|- DC2: {:.1f} A - {:.1f} V - {:.1f} °C".format(
                        charger_DC2_current, charger_DC2_voltage, charger_DC2_temperature
                    )
                )

            last_updated = last_changed

        # quit driver if timeout is exceeded
        if timeout != 0 and (now - last_changed) > timeout:
            logging.error(
                "Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time."
                % timeout
            )
            sys.exit()

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


def main():
    _thread.daemon = True  # allow the program to quit

    from dbus.mainloop.glib import (
        DBusGMainLoop,
    )  # pyright: ignore[reportMissingImports]

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    # MQTT setup
    client = mqtt.Client("MqttACcharger_" + str(config["MQTT"]["device_instance"]))
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    # check tls and use settings, if provided
    if "tls_enabled" in config["MQTT"] and config["MQTT"]["tls_enabled"] == "1":
        logging.info("MQTT client: TLS is enabled")

        if (
            "tls_path_to_ca" in config["MQTT"]
            and config["MQTT"]["tls_path_to_ca"] != ""
        ):
            logging.info(
                'MQTT client: TLS: custom ca "%s" used'
                % config["MQTT"]["tls_path_to_ca"]
            )
            client.tls_set(config["MQTT"]["tls_path_to_ca"], tls_version=2)
        else:
            client.tls_set(tls_version=2)

        if "tls_insecure" in config["MQTT"] and config["MQTT"]["tls_insecure"] != "":
            logging.info(
                "MQTT client: TLS certificate server hostname verification disabled"
            )
            client.tls_insecure_set(True)

    # check if username and password are set
    if (
        "username" in config["MQTT"]
        and "password" in config["MQTT"]
        and config["MQTT"]["username"] != ""
        and config["MQTT"]["password"] != ""
    ):
        logging.info(
            'MQTT client: Using username "%s" and password to connect'
            % config["MQTT"]["username"]
        )
        client.username_pw_set(
            username=config["MQTT"]["username"], password=config["MQTT"]["password"]
        )

    # connect to broker
    logging.info(
        f"MQTT client: Connecting to broker {config['MQTT']['broker_address']} on port {config['MQTT']['broker_port']}"
    )
    client.connect(
        host=config["MQTT"]["broker_address"], port=int(config["MQTT"]["broker_port"])
    )
    client.loop_start()

    # wait to receive first data, else the JSON is empty and phase setup won't work
    i = 0
    while charger_DC0_current == -1:
        if i % 12 != 0 or i == 0:
            logging.info("Waiting 5 seconds for receiving first data...")
        else:
            logging.warning(
                "Waiting since %s seconds for receiving first data..." % str(i * 5)
            )
        sleep(5)
        i += 1

    # formatting
  
    def _a(p, v):
        return str("%.1f" % v) + "A"

    def _w(p, v):
        return str("%i" % v) + "W"

    def _v(p, v):
        return str("%.2f" % v) + "V"

    def _deg(p, v):
        return str("%.1f" % v) + "°C"

    def _n(p, v):
        return str("%i" % v)

    paths_dbus = {
        "/Ac/In/L1/I": {"initial": 0, "textformat": _a},
        "/Ac/In/L1/P": {"initial": 0, "textformat": _w},
        "/Ac/In/CurrentLimit": {"initial": 0, "textformat": _a},
        "/NrOfOutputs": {"initial": 0, "textformat": _n},
        "/State": {"initial": 0, "textformat": _n},
        "/Mode": {"initial": 0, "textformat": _n},
        "/ErrorCode": {"initial": 0, "textformat": _n},
        "/Relay/0/State": {"initial": 0, "textformat": _n},
        "/Alarms/LowVoltage": {"initial": 0, "textformat": _n},
        "/Alarms/HighVoltage": {"initial": 0, "textformat": _n},       
        "/Dc/0/Voltage": {"initial": None, "textformat": _v},
        "/Dc/0/Current": {"initial": 0, "textformat": _a},
        "/Dc/0/Temperature": {"initial": None, "textformat": _deg},
        "/UpdateIndex": {"initial": 0, "textformat": _n},
    }

    if charger_DC1_current is not None:
        paths_dbus.update(
            {
                "/Dc/1/Voltage": {"initial": None, "textformat": _v},
                "/Dc/1/Current": {"initial": None, "textformat": _a},
                "/Dc/1/Temperature": {"initial": None, "textformat": _deg},
            }
        )

    if charger_DC2_current is not None:
        paths_dbus.update(
            {
                "/Dc/2/Voltage": {"initial": None, "textformat": _v},
                "/Dc/2/Current": {"initial": None, "textformat": _a},
                "/Dc/2/Temperature": {"initial": None, "textformat": _deg},
            }
        )

    DbusMqttAcChargerService(
        servicename="com.victronenergy.charger.mqtt_ac_charger_"
        + str(config["MQTT"]["device_instance"]),
        deviceinstance=int(config["MQTT"]["device_instance"]),
        customname=config["MQTT"]["device_name"],
        paths=paths_dbus,
    )

    logging.info(
        "Connected to dbus and switching over to GLib.MainLoop() (= event based)"
    )
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
