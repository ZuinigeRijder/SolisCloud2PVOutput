# == soliscloud_to_pvoutput.py Author: Zuinige Rijder =========================
"""
Simple Python3 script to copy latest
(normally once per 5 minutes) SolisCloud portal update to PVOutput portal.
 """
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
parser = configparser.ConfigParser()
parser.read('soliscloud_to_pvoutput.cfg')
api_secrets = dict(parser.items('api_secrets'))

# == API Secrets, fill in yours in soliscloud_to_pvoutput.cfg ================
SOLISCLOUD_API_ID = api_secrets['soliscloud_api_id']  # userId
SOLISCLOUD_API_SECRET = api_secrets['soliscloud_api_secret'].encode('utf-8')
SOLISCLOUD_API_URL = api_secrets['soliscloud_api_url']
PVOUTPUT_API_KEY = api_secrets['pvoutput_api_key']
PVOUTPUT_SYSTEM_ID = api_secrets['pvoutput_system_id']

# == Constants ===============================================================
VERB = "POST"
CONTENT_TYPE = "application/json"
USER_STATION_LIST = '/v1/api/userStationList'
INVERTER_LIST = '/v1/api/inverterList'
INVERTER_DETAIL = '/v1/api/inverterDetail'
PVOUTPUT_ADD_URL = 'http://pvoutput.org/service/r2/addbatchstatus.jsp'

TODAY = datetime.now().strftime("%Y%m%d")  # format yyyymmdd

logging.config.fileConfig("logging_config.ini")

# == post ====================================================================
def execute_request(url, data, headers) -> str:
    """execute request and handle errors"""
    post_data = data.encode("utf-8")
    request = Request(url, data=post_data, headers=headers)
    errorstring = ''
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
            content = body.decode("utf-8")
            return content
    except HTTPError as error:
        errorstring = str(error.status) + ': ' + error.reason
    except URLError as error:
        errorstring = str(error.reason)
    except TimeoutError:
        errorstring = 'Request timed out'
    except socket.timeout:
        errorstring = 'Socket timed out'
    except Exception as ex:  # pylint: disable=broad-except
        errorstring = 'urlopen exception: ' + str(ex)
        traceback.print_exc()

    logging.error(url + " -> " + errorstring)
    time.sleep(60)  # retry after 1 minute
    return 'ERROR'


# == get_solis_cloud_data ====================================================
def get_solis_cloud_data(url_part, data) -> str:
    """get solis cloud data"""
    md5 = base64.b64encode(
        hashlib.md5(data.encode('utf-8')).digest()).decode('utf-8')
    while True:
        now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        encrypt_str = (
            VERB + "\n" + md5 + "\n" + CONTENT_TYPE + "\n" +
            now + "\n" + url_part
        )
        hmac_obj = hmac.new(
            SOLISCLOUD_API_SECRET,
            msg=encrypt_str.encode('utf-8'),
            digestmod=hashlib.sha1
        )
        authorization = (
            'API ' + SOLISCLOUD_API_ID + ':' +
            base64.b64encode(hmac_obj.digest()).decode('utf-8')
        )
        headers = {
            'Content-MD5': md5,
            'Content-Type': CONTENT_TYPE,
            'Date': now,
            'Authorization': authorization
        }
        content = execute_request(SOLISCLOUD_API_URL+url_part, data, headers)
        # log(SOLISCLOUD_API_URL+url_part + "->" + content)
        if content != 'ERROR':
            return content


# == send_pvoutput_data ======================================================
def send_pvoutput_data(pvoutput_string) -> str:
    """send pvoutput data with the provided parameters"""
    loggging.info(pvoutput_string)
    headers = {
        'X-Pvoutput-Apikey': PVOUTPUT_API_KEY,
        'X-Pvoutput-SystemId': PVOUTPUT_SYSTEM_ID,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }
    retry = 0
    while True:
        retry += 1
        content = execute_request(PVOUTPUT_ADD_URL, pvoutput_string, headers)
        if content != "ERROR" or retry > 30:
            if content == "ERROR":
                logging.error("number of retries exceeded")
            return content


# == get_inverter_list_body ==================================================
def get_inverter_list_body() -> str:
    """get inverter list body"""
    body = '{"userid":"' + SOLISCLOUD_API_ID + '"}'
    content = get_solis_cloud_data(USER_STATION_LIST, body)
    station_info = json.loads(content)['data']['page']['records'][0]
    station_id = station_info['id']

    body = '{"stationId":"' + station_id + '"}'
    content = get_solis_cloud_data(INVERTER_LIST, body)
    inverter_info = json.loads(content)['data']['page']['records'][0]
    inverter_id = inverter_info['id']
    inverter_sn = inverter_info['sn']

    body = '{"id":"' + inverter_id + '","sn":"' + inverter_sn + '"}'
    logging.info("body: " + body)
    return body


# == MAIN ====================================================================
def main_loop():
    """main_loop"""
    inverter_detail_body = get_inverter_list_body()
    timestamp_previous = '0'
    hi_res_watthour_today = 0
    while True:
        time.sleep(60)  # wait 1 minute before checking again
        datetime_now = datetime.now()
        # only check between 5 and 23 hours
        if datetime_now.hour < 5 or datetime_now.hour > 22:
            logging.info("Outside solar generation hours (5..23)")
            sys.exit('Exiting program to start fresh tomorrow')

        content = get_solis_cloud_data(INVERTER_DETAIL, inverter_detail_body)
        inverter_detail = json.loads(content)['data']
        # json_formatted_str = json.dumps(inverter_detail, indent=2)
        # print(json_formatted_str)
        timestamp_current = inverter_detail['dataTimestamp']
        volt = (
            inverter_detail['uPv1'] +
            inverter_detail['uPv2'] +
            inverter_detail['uPv3'] +
            inverter_detail['uPv4']
        )
        watt = round(inverter_detail['pac'] * 1000)
        watthour_today = round(inverter_detail['eToday'] * 1000)
        inverter_temp = inverter_detail['inverterTemperature']
        ac_volt = max(
            max(inverter_detail['uAc1'], inverter_detail['uAc2']),
            inverter_detail['uAc3']
        )

        if timestamp_previous == '0':
            hi_res_watthour_today = watthour_today

        # compute local time, soliscloud did not take care of leap year
        datetime_current = datetime.fromtimestamp(int(timestamp_current)/1000)
        if (timestamp_current != timestamp_previous and
                datetime_current.day == datetime_now.day):
            # only handle new values today
            if timestamp_previous != '0':  # check for multiple of 5 minutes
                # round to nearest 5 minutes
                elapsed_minutes = round(
                    (int(timestamp_current) - int(timestamp_previous)) / 60000
                )
                if elapsed_minutes <= 0:
                    logging.error(f"TIMESTAMPERROR: {elapsed_minutes}, timestamp: {timestamp_current}, timestamp_previous: {timestamp_previous}")  # noqa
                    elapsed_minutes = 1

                # compute hiResTotalWattHour with current watts/elapsed minutes
                hi_res_watthour_today += int(watt/(60/elapsed_minutes))
                if hi_res_watthour_today < watthour_today:
                    hi_res_watthour_today = watthour_today  # was too low
                else:
                    if watthour_today + 100 < hi_res_watthour_today:
                        # hi_res_total_watthour was too high
                        hi_res_watthour_today = watthour_today + 99

            pvoutput_string = (
                'data=' + TODAY +  # Date
                ',' + datetime_current.strftime("%H:%M") +  # Time
                ',' + str(hi_res_watthour_today) +  # Energy Generation
                ',' + str(watt) +  # Power Generation
                ',-1' +  # no Energy Consumption
                ',' + str(ac_volt) +  # Power generation used for AC voltage
                ',' + str(inverter_temp) +  # inverter temp iso outside temp
                ',' + str(volt)  # Voltage
            )
            send_pvoutput_data(pvoutput_string)
            timestamp_previous = timestamp_current


# == MAIN ====================================================================
main_loop()
