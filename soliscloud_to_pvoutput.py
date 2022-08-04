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
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request


# == Secrets, fill in yours ==================================================
SOLISCLOUD_API_ID = 'xxxx'
SOLISCLOUD_API_SECRET = b'xxxx'
SOLISCLOUD_API_URL = 'https://www.soliscloud.com:13333'
PVOUTPUT_API_KEY = 'xxxx'
PVOUTPUT_SYSTEM_ID = 'xxxx'

# == Constants ===============================================================
VERB = "POST"
CONTENT_TYPE = "application/json"
USER_STATION_LIST = '/v1/api/userStationList'
INVERTER_LIST = '/v1/api/inveterList'
INVERTER_DETAIL = '/v1/api/inveterDetail'
PVOUTPUT_ADD_URL = 'http://pvoutput.org/service/r2/addbatchstatus.jsp'


# == log =====================================================================
def log(msg):
    """log a message prefixed with a date/time format yyyymmdd hh:mm:ss"""
    print(datetime.now().strftime("%Y%m%d %H:%M:%S") + ': ' + msg)


# == post ====================================================================
def post(url, data, headers) -> str:
    """post data and header and handle errors"""
    post_data = data.encode("utf-8")
    request = Request(url, data=post_data, headers=headers)
    errorstring = ''
    try:
        with urlopen(request, timeout=10) as response:
            body = response.read()
            content = body.decode("utf-8")
            return content
    except HTTPError as error:
        errorstring = str(error.status) + ': ' + error.reason
    except URLError as error:
        errorstring = str(error.reason)
    except TimeoutError:
        errorstring = 'Request timed out'

    log('ERROR: ' + url + ' -> ' + errorstring)
    time.sleep(60)  # retry after 1 minute
    return 'ERROR'


# == solis_cloud_post ========================================================
def solis_cloud_post(url_part, data) -> str:
    """post solis cloud data and encode/authorize"""
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
        header = {
            'Content-MD5': md5,
            'Content-Type': CONTENT_TYPE,
            'Date': now,
            'Authorization': authorization
        }
        content = post(SOLISCLOUD_API_URL+url_part, data, header)
        if content != 'ERROR':
            return content


# == pvoutput_post ===========================================================
def pvoutput_post(prefix, datetime_current, watthour_today, watt, volt) -> str:
    """pvoutput post data with the provided parameters"""
    pvoutput_string = (
        'data=' +
        datetime_current.strftime("%Y%m%d") +
        ',' + datetime_current.strftime("%H:%M") +
        ',' + str(watthour_today) +
        ',' + str(watt) +
        ',-1,-1,,' + str(volt)
    )
    log(prefix + ' ' + pvoutput_string)
    headers = {
        'X-Pvoutput-Apikey': PVOUTPUT_API_KEY,
        'X-Pvoutput-SystemId': PVOUTPUT_SYSTEM_ID,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }
    retry = 0
    while True:
        retry = retry + 1
        content = post(PVOUTPUT_ADD_URL, pvoutput_string, headers)
        if content != 'ERROR' or retry > 10:
            return content


# == get_inverter_list_body ==================================================
def get_inverter_list_body() -> str:
    """get inverter list body"""
    body = '{"userid":"' + SOLISCLOUD_API_ID + '"}'
    content = solis_cloud_post(USER_STATION_LIST, body)
    station_info = json.loads(content)['data']['page']['records'][0]
    station_id = station_info['id']

    body = '{"stationId":"' + station_id + '"}'
    content = solis_cloud_post(INVERTER_LIST, body)
    inverter_info = json.loads(content)['data']['page']['records'][0]
    inverter_id = inverter_info['id']
    inverter_sn = inverter_info['sn']

    body = '{"id":"' + inverter_id + '","sn":"' + inverter_sn + '"}'
    return body


# == MAIN ====================================================================
def main_loop():
    """main_loop"""
    inverter_detail_body = get_inverter_list_body()
    timestamp_previous = '0'
    hi_res_watthour_today = 0
    while True:
        datetime_now = datetime.now()
        # only check between 5 and 23 hours
        if datetime_now.hour < 5 or datetime_now.hour > 22:
            log('Outside solar generation hours (5..23)')
            sys.exit('Exiting program to start fresh tomorrow')

        content = solis_cloud_post(INVERTER_DETAIL, inverter_detail_body)
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
        ac_volt = inverter_detail['uAc1']
        prefix = (
            'inverter temperature: ' + str(inverter_temp) +
            ', AC voltage: ' + str(ac_volt)
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
                # compute hiResTotalWattHour with current watts/elapsed minutes
                hi_res_watthour_today += int(watt/(60/elapsed_minutes))
                if hi_res_watthour_today < watthour_today:
                    hi_res_watthour_today = watthour_today  # was too low
                else:
                    if watthour_today + 100 < hi_res_watthour_today:
                        # hi_res_total_watthour was too high
                        hi_res_watthour_today = watthour_today + 99

            pvoutput_post(
                prefix, datetime_current, hi_res_watthour_today, watt, volt)
            timestamp_previous = timestamp_current

        time.sleep(60)  # wait 1 minute before checking again


# == MAIN ====================================================================
main_loop()
