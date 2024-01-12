# == soliscloud_to_pvoutput.py Author: Zuinige Rijder =========================
"""
Simple Python3 script to copy latest
(normally once per 5 minutes) SolisCloud portal update to PVOutput portal.
 """
from os import path
import base64
import hashlib
import hmac
import json
import time
import sys
import configparser
import socket
import traceback
import logging
import logging.config

from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

# == read api_secrets in soliscloud_to_pvoutput.cfg ==========================
SCRIPT_DIRNAME = path.abspath(path.dirname(__file__))
parser = configparser.ConfigParser()
parser.read(f"{SCRIPT_DIRNAME}/soliscloud_to_pvoutput.cfg")


def get(dictionary: dict, key: str, default: str = "") -> str:
    """get key from dictionary"""
    if key in dictionary:
        return dictionary[key].strip()
    return default


def get_bool(dictionary: dict, key: str, default: bool = True) -> bool:
    """get boolean value from dictionary key"""
    value = get(dictionary, key)
    if value == "":
        return default
    return value.lower() == "true"


# == API Secrets, fill in yours in soliscloud_to_pvoutput.cfg ================
api_secrets = dict(parser.items("api_secrets"))
SOLISCLOUD_API_ID = get(api_secrets, "soliscloud_api_id")  # userId
SOLISCLOUD_API_SECRET = get(api_secrets, "soliscloud_api_secret").encode("utf-8")
SOLISCLOUD_API_URL = get(api_secrets, "soliscloud_api_url")
SOLISCLOUD_STATION_INDEX = int(get(api_secrets, "soliscloud_station_index", "0"))
SOLISCLOUD_INVERTER_INDEX = int(get(api_secrets, "soliscloud_inverter_index", "0"))
PVOUTPUT_API_KEY = get(api_secrets, "pvoutput_api_key")
PVOUTPUT_SYSTEM_ID = get(api_secrets, "pvoutput_system_id")

# == PVOutput info, fill in yours in soliscloud_to_pvoutput.cfg ===========
pvoutput_info = dict(parser.items("PVOutput"))
SEND_TO_PVOUTPUT = get_bool(pvoutput_info, "send_to_pvoutput")  # default True
PVOUTPUT_FILL_TEMPERATURE = get_bool(
    pvoutput_info, "pvoutput_fill_temperature_with_inverter_temperature"
)
PVOUTPUT_FILL_VOLTAGE_WITH_AC_VOLTAGE = get_bool(
    pvoutput_info, "pvoutput_fill_voltage_with_ac_voltage", False
)

PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_FAMILYLOADPOWER = get_bool(
    pvoutput_info, "pvoutput_fill_power_consumption_with_familyloadpower"
)
PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_HOMECONSUMPTION = get_bool(
    pvoutput_info, "pvoutput_fill_power_consumption_with_homeconsumption"
)
PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_AC_VOLTAGE = get_bool(
    pvoutput_info, "pvoutput_fill_power_consumption_with_ac_voltage"
)


# == domoticz info, fill in yours in soliscloud_to_pvoutput.cfg ===========
domoticz_info = dict(parser.items("Domoticz"))
SEND_TO_DOMOTICZ = get_bool(domoticz_info, "send_to_domoticz", False)
DOMOTICZ_URL = get(domoticz_info, "domot_url")
DOMOTICZ_POWER_GENERATED_ID = get(domoticz_info, "domot_power_generated_id", "0")
DOMOTICZ_AC_VOLT_ID = get(domoticz_info, "domot_ac_volt_id", "0")
DOMOTICZ_INVERTER_TEMP_ID = get(domoticz_info, "domot_inverter_temp_id", "0")
DOMOTICZ_VOLT_ID = get(domoticz_info, "domot_volt_id", "0")
DOMOTICZ_SOLARPOWER_ID = get(domoticz_info, "domot_solarpower_id", "0")
DOMOTICZ_ENERGYGENERATION_ID = get(domoticz_info, "domot_energygeneration_id", "0")
DOMOTICZ_BATTERYPOWER_ID = get(domoticz_info, "domot_batterypower_id", "0")
DOMOTICZ_GRIDPOWER_ID = get(domoticz_info, "domot_gridpower_id", "0")
DOMOTICZ_FAMILYLOADPOWER_ID = get(domoticz_info, "domot_familyloadpower_id", "0")
DOMOTICZ_HOMECONSUMPTION_ID = get(domoticz_info, "domot_homeconsumption_id", "0")

# == Constants ===============================================================
VERB = "POST"
CONTENT_TYPE = "application/json"
USER_STATION_LIST = "/v1/api/userStationList"
INVERTER_LIST = "/v1/api/inverterList"
INVERTER_DETAIL = "/v1/api/inverterDetail"
PVOUTPUT_ADD_URL = "http://pvoutput.org/service/r2/addbatchstatus.jsp"


TODAY = datetime.now().strftime("%Y%m%d")  # format yyyymmdd

logging.config.fileConfig(f"{SCRIPT_DIRNAME}/logging_config.ini")


# == post ====================================================================
def execute_request(url: str, data: str, headers: dict) -> str:
    """execute request and handle errors"""
    if data != "":
        post_data = data.encode("utf-8")
        request = Request(url, data=post_data, headers=headers)
    else:
        request = Request(url)
    errorstring = ""
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
            content = body.decode("utf-8")
            logging.debug(content)
            return content
    except HTTPError as error:
        errorstring = str(error.status) + ": " + error.reason
    except URLError as error:
        errorstring = str(error.reason)
    except TimeoutError:
        errorstring = "Request timed out"
    except socket.timeout:
        errorstring = "Socket timed out"
    except Exception as ex:  # pylint: disable=broad-except
        errorstring = "urlopen exception: " + str(ex)
        traceback.print_exc()

    logging.error(url + " -> " + errorstring)
    time.sleep(60)  # retry after 1 minute
    return "ERROR"


# == get_solis_cloud_data ====================================================
def get_solis_cloud_data(url_part: str, data: str) -> str:
    """get solis cloud data"""
    md5 = base64.b64encode(hashlib.md5(data.encode("utf-8")).digest()).decode("utf-8")
    while True:
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        encrypt_str = (
            VERB + "\n" + md5 + "\n" + CONTENT_TYPE + "\n" + now + "\n" + url_part
        )
        hmac_obj = hmac.new(
            SOLISCLOUD_API_SECRET,
            msg=encrypt_str.encode("utf-8"),
            digestmod=hashlib.sha1,
        )
        authorization = (
            "API "
            + SOLISCLOUD_API_ID
            + ":"
            + base64.b64encode(hmac_obj.digest()).decode("utf-8")
        )
        headers = {
            "Content-MD5": md5,
            "Content-Type": CONTENT_TYPE,
            "Date": now,
            "Authorization": authorization,
        }
        content = execute_request(SOLISCLOUD_API_URL + url_part, data, headers)
        # log(SOLISCLOUD_API_URL+url_part + "->" + content)
        if content != "ERROR":
            return content


# == send_pvoutput_data ======================================================
def send_pvoutput_data(pvoutput_string: str):
    """send pvoutput data with the provided parameters"""
    logging.info(pvoutput_string)
    headers = {
        "X-Pvoutput-Apikey": PVOUTPUT_API_KEY,
        "X-Pvoutput-SystemId": PVOUTPUT_SYSTEM_ID,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    retry = 0
    while True:
        retry += 1
        content = execute_request(PVOUTPUT_ADD_URL, pvoutput_string, headers)
        if content != "ERROR" or retry > 30:
            if content == "ERROR":
                logging.error("number of retries exceeded")
            return


# == send to Domoticz ========================================================
def send_to_domoticz(idx: str, value: str):
    """send_to_Domoticz"""
    if idx == "0":
        return  # nothing to do

    url = (
        DOMOTICZ_URL
        + "/json.htm?type=command&param=udevice&idx="
        + idx
        + "&svalue="
        + value
    )
    logging.info(url)
    retry = 0
    while True:
        retry += 1
        content = execute_request(url, "", {})
        if content != "ERROR" or retry > 30:
            if content == "ERROR":
                logging.error("number of retries exceeded")
            return


# == get_inverter_list_body ==================================================
def get_inverter_list_body() -> str:
    """get inverter list body"""
    body = '{"userid":"' + SOLISCLOUD_API_ID + '"}'
    content = get_solis_cloud_data(USER_STATION_LIST, body)
    station_info = json.loads(content)["data"]["page"]["records"][
        SOLISCLOUD_STATION_INDEX
    ]
    station_id = station_info["id"]

    body = '{"stationId":"' + station_id + '"}'
    content = get_solis_cloud_data(INVERTER_LIST, body)
    inverter_info = json.loads(content)["data"]["page"]["records"][
        SOLISCLOUD_INVERTER_INDEX
    ]
    inverter_id = inverter_info["id"]
    inverter_sn = inverter_info["sn"]

    body = '{"id":"' + inverter_id + '","sn":"' + inverter_sn + '"}'
    logging.info("body: %s", body)
    return body


# == do_work ====================================================================
def do_work():
    """do_work"""
    inverter_detail_body = get_inverter_list_body()
    timestamp_previous = "0"
    energy_generation = 0
    while True:
        time.sleep(60)  # wait 1 minute before checking again
        datetime_now = datetime.now()
        # only check between 5 and 23 hours
        if datetime_now.hour < 5 or datetime_now.hour > 22:
            logging.info("Outside solar generation hours (5..23)")
            sys.exit("Exiting program to start fresh tomorrow")

        content = get_solis_cloud_data(INVERTER_DETAIL, inverter_detail_body)
        inverter_detail = json.loads(content)["data"]
        # json_formatted_str = json.dumps(inverter_detail, indent=2)
        # print(json_formatted_str)
        timestamp_current = inverter_detail["dataTimestamp"]
        dc_voltage = str(
            inverter_detail["uPv1"]
            + inverter_detail["uPv2"]
            + inverter_detail["uPv3"]
            + inverter_detail["uPv4"]
        )
        solar_watthour_today = round(inverter_detail["eToday"] * 1000)
        inverter_temperature = str(inverter_detail["inverterTemperature"])
        ac_voltage = str(
            max(
                inverter_detail["uAc1"],
                inverter_detail["uAc2"],
                inverter_detail["uAc3"],
            )
        )
        solar_power = round(inverter_detail["pac"] * 1000)
        family_load = round(inverter_detail["familyLoadPower"] * 1000)
        battery_power = round(inverter_detail["batteryPower"] * 1000)
        grid_power = round(inverter_detail["psum"] * 1000)
        home_consumption = solar_power - grid_power - battery_power
        if timestamp_previous == "0":
            energy_generation = solar_watthour_today

        # compute local time, soliscloud did not take care of leap year
        datetime_current = datetime.fromtimestamp(int(timestamp_current) / 1000)
        if (
            timestamp_current != timestamp_previous
            and datetime_current.day == datetime_now.day
        ):
            # only handle new values today
            if timestamp_previous != "0":  # check for multiple of 5 minutes
                # round to nearest 5 minutes
                elapsed_minutes = round(
                    (int(timestamp_current) - int(timestamp_previous)) / 60000
                )
                if elapsed_minutes <= 0:
                    logging.error(  # pylint:disable=logging-fstring-interpolation
                        f"TIMESTAMPERROR: {elapsed_minutes}, timestamp: {timestamp_current}, timestamp_previous: {timestamp_previous}"  # noqa
                    )
                    elapsed_minutes = 1

                # compute hiRes energy_generation with current watts/elapsed minutes
                energy_generation += int(solar_power / (60 / elapsed_minutes))
                if energy_generation < solar_watthour_today:
                    energy_generation = solar_watthour_today  # too low
                else:
                    if solar_watthour_today + 100 < energy_generation:
                        energy_generation = solar_watthour_today + 99  # too high

            current_time = datetime_current.strftime("%H:%M")
            if logging.DEBUG >= logging.root.level:
                debug_string = f"date={TODAY}, time={current_time}, energy_generation={energy_generation}, solar_power={solar_power}, battery_power={battery_power}, grid_power={grid_power}, family_load={family_load}, home_consumption={home_consumption}, inverter_temperature={inverter_temperature}, dc_voltage={dc_voltage}, ac_voltage={ac_voltage}"  # noqa
                logging.debug(debug_string)

            if SEND_TO_PVOUTPUT:
                energy_consumption = ""  # no energy consumption
                power_consumption = ""
                if PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_FAMILYLOADPOWER:
                    power_consumption = str(family_load)
                elif PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_HOMECONSUMPTION:
                    power_consumption = str(home_consumption)
                elif PVOUTPUT_FILL_POWER_CONSUMPTION_WITH_AC_VOLTAGE:
                    power_consumption = ac_voltage
                temperature = ""
                if PVOUTPUT_FILL_TEMPERATURE:
                    temperature = inverter_temperature  # inverter temp iso outside temp
                voltage = dc_voltage
                if PVOUTPUT_FILL_VOLTAGE_WITH_AC_VOLTAGE:
                    voltage = ac_voltage

                # PVOutput Add Batch Status Service fields
                #
                # Field                 Required	Format	    Unit	    Example
                # Date	                Yes	        yyyymmdd	date	    20210228
                # Time	                Yes	        hh:mm	    time	    13:00
                # Energy Generation	    Yes	        number	    watt hours	10000
                # Power Generation	    No	        number	    watts	    2000
                # Energy Consumption	No	        number	    watt hours	10000
                # Power Consumption	    No	        number	    watts	    2000
                # Temperature	        No	        decimal	    celsius	    23.4
                # Voltage	            No	        decimal	    volts	    240.7

                pvoutput_string = f"data={TODAY},{current_time},{energy_generation},{solar_power},{energy_consumption},{power_consumption},{temperature},{voltage}"  # noqa
                send_pvoutput_data(pvoutput_string)

            if SEND_TO_DOMOTICZ:
                send_to_domoticz(
                    DOMOTICZ_POWER_GENERATED_ID,
                    str(solar_power) + ";" + str(energy_generation),
                )
                send_to_domoticz(DOMOTICZ_AC_VOLT_ID, ac_voltage)
                send_to_domoticz(DOMOTICZ_INVERTER_TEMP_ID, inverter_temperature)
                send_to_domoticz(DOMOTICZ_VOLT_ID, dc_voltage)
                send_to_domoticz(DOMOTICZ_SOLARPOWER_ID, str(solar_power))
                send_to_domoticz(DOMOTICZ_ENERGYGENERATION_ID, str(energy_generation))
                send_to_domoticz(DOMOTICZ_BATTERYPOWER_ID, str(battery_power))
                send_to_domoticz(DOMOTICZ_GRIDPOWER_ID, str(grid_power))
                send_to_domoticz(DOMOTICZ_FAMILYLOADPOWER_ID, str(family_load))
                send_to_domoticz(DOMOTICZ_HOMECONSUMPTION_ID, str(home_consumption))
            timestamp_previous = timestamp_current


def main_loop():
    """main_loop"""
    finished = False
    while not finished:
        try:
            do_work()
            logging.info("Progam finished successful")
            finished = True
        except Exception as exception:  # pylint: disable=broad-except
            logging.error(  # pylint:disable=logging-fstring-interpolation
                f"Exception: {exception}, sleeping a minute"
            )
            traceback.print_exc()
            time.sleep(60)


# == MAIN ====================================================================
main_loop()
