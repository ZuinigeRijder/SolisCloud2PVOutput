#== SolisCloud2PVOutput.py Author: Zuinige Rijder ====================
import base64
import hashlib
import hmac
import json
import time
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

#== Secrets, fill in yours ====================================================
SOLISCLOUD_API_ID = 'xxxx'
SOLISCLOUD_API_SECRET = b'xxxx'
SOLISCLOUD_API_URL = 'https://www.soliscloud.com:13333'
PVOUTPUT_API_KEY = 'xxxx'
PVOUTPUT_SYSTEM_ID = 'xxxx'

#== Constants =================================================================
VERB = "POST"
CONTENT_TYPE = "application/json"
USER_STATION_LIST = '/v1/api/userStationList'
INVERTER_LIST = '/v1/api/inveterList'
INVERTER_DETAIL = '/v1/api/inveterDetail'
PVOUTPUT_ADD_BATCH_STATUS_URL = 'http://pvoutput.org/service/r2/addbatchstatus.jsp'

#== log ======================================================================= 
def log(msg):
    print(datetime.now().strftime("%Y%m%d %H:%M:%S") + ': ' + msg)

#== post ======================================================================
def post(url, data, header) -> str: 
    post_data = data.encode("utf-8")
    request = Request(url, data=post_data, headers=header)
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
    time.sleep(60) # retry after 1 minute
    return 'ERROR'

#== solisCloudPost ============================================================
def solisCloudPost(urlPart, data) -> str: 
    content_md5 = base64.b64encode(hashlib.md5(data.encode('utf-8')).digest()).decode('utf-8')
    while True:
        date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        encrypt_str = (VERB+"\n"+content_md5+"\n"+CONTENT_TYPE+"\n"+date+"\n"+urlPart)
        hmac_obj = hmac.new(SOLISCLOUD_API_SECRET, msg=encrypt_str.encode('utf-8'), digestmod=hashlib.sha1)
        authorization = 'API ' + SOLISCLOUD_API_ID + ':' + base64.b64encode(hmac_obj.digest()).decode('utf-8')
        header = {'Content-MD5':content_md5, 'Content-Type':CONTENT_TYPE, 'Date':date, 'Authorization':authorization}
        content = post(SOLISCLOUD_API_URL+urlPart, data, header) 
        if content != 'ERROR':
            return content

#== pvoutputPost ==============================================================
def pvoutputPost(dt, totalWattHour, watt, dcPV) -> str:
    pvoutputString = 'data='+dt.strftime("%Y%m%d")+','+dt.strftime("%H:%M")+','+str(totalWattHour)+','+str(watt)+',-1,-1,,'+str(dcPV)
    log(pvoutputString)
    header = {'X-Pvoutput-Apikey': PVOUTPUT_API_KEY, 'X-Pvoutput-SystemId': PVOUTPUT_SYSTEM_ID, 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
    retry = 0
    while True:
        retry = retry + 1
        content = post(PVOUTPUT_ADD_BATCH_STATUS_URL, pvoutputString, header)
        if content != 'ERROR' or retry > 10:
            return content

#== MAIN ======================================================================
body = '{"userid":"' + SOLISCLOUD_API_ID + '"}'
content = solisCloudPost(USER_STATION_LIST, body)
stationInfo = json.loads(content)['data']['page']['records'][0]
stationId = stationInfo['id']

body = '{"stationId":"'+ stationId + '"}'
content = solisCloudPost(INVERTER_LIST, body)
inverterInfo = json.loads(content)['data']['page']['records'][0]
inverterId = inverterInfo['id']
inverterSn = inverterInfo['sn']

body = '{"id":"'+ inverterId + '","sn":"' + inverterSn + '"}'
prevDataTimestamp = '0'
hiResTotalWattHour = 0
while True:
    dateNow = datetime.now()
    if dateNow.hour < 5 or dateNow.hour > 22: # only check between 5 and 23 hour
        log('Outside solar generation hours (5..23)')
        sys.exit('Exiting program to avoid possible memory leaks') # if you want this program to run forever, comment this line with #
        time.sleep(round((60-dateNow.minute)*60)) # wait till next hour
        prevDataTimestamp = '0'
        continue # start loop over again

    content = solisCloudPost(INVERTER_DETAIL, body)
    inverterDetail = json.loads(content)['data']
    dataTimestamp = inverterDetail['dataTimestamp']
    acVoltage = inverterDetail['uAc1']
    dcPV = inverterDetail['uPv1'] + inverterDetail['uPv2'] + inverterDetail['uPv3'] + inverterDetail['uPv4']
    watt = round(inverterDetail['pac'] * 1000)
    totalWattHour = round(inverterDetail['eToday'] * 1000)

    if prevDataTimestamp == '0':
        hiResTotalWattHour = totalWattHour
  
    dt = datetime.fromtimestamp(int(dataTimestamp)/1000) # compute local time, soliscloud did not take care of leap year
    if dataTimestamp != prevDataTimestamp and dt.day == dateNow.day: # only handle new values today
        if prevDataTimestamp != '0': # check for multiple of 5 minutes
            elapsedMinutes = round((int(dataTimestamp) - int(prevDataTimestamp)) / 60000) # round to nearest 5 minutes
            hiResTotalWattHour += int(watt/(60/elapsedMinutes)) # compute hiResTotalWattHour with current watts (assuming same solar radiation) over elapsed minutes
            if hiResTotalWattHour < totalWattHour:
                hiResTotalWattHour = totalWattHour # hiResTotalWattHour was too low
            else: 
                if totalWattHour + 100 < hiResTotalWattHour: 
                    hiResTotalWattHour = totalWattHour + 99 # hiResTotalWattHour was too high
            
        pvoutputPost(dt, hiResTotalWattHour, watt, dcPV)
        prevDataTimestamp = dataTimestamp

    time.sleep(60) # wait 1 minute before checking again
