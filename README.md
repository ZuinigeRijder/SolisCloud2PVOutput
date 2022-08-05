[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# SolisCloud to PVOutput
Simple Python3 script to copy latest (normally once per 5 minutes) SolisCloud portal update to PVOutput portal. 

The soliscloud_to_pvoutput.py script will get the first station id with the secrets of SolisCloud (see next section). Thereafter it will get the first inverter id and serial number. Then in an endless loop the inverter details are fetched and the following information is used:
* timestamp
* DC PV voltage (assuming no more than 4 strings)
* watt (current)
* watthour today
* inverter temperature (logged only)
* AC voltage (assuming 1 phase system, logged only)

This information is used to compute the new information to be send to PVOutput, when the timestamp is changed.

Notes
* only between 5 and 23 hour data is fetched from SolisCloud and copied to PVOutput
* the script will exit outside 5 and 23
* Each new day the "watthour today" starts with 0
* Because the resolution of the SolisCloud watthour is in 100 Watt, a higher resolution is computed with current Watt
* if you have more than 1 station/inverter, more than 4 strings or a 3 phase inverter, you need to adapt the script

## SolisCloud
[SolisCloud](https://www.soliscloud.com/) is the next generation Portal for Solis branded PV systems from Ginlong.

The python script requires a SolisCloud API_ID, API_SECRET and API_URL to function.
* Go to https://www.soliscloud.com/#/apiManage
* Ativate API management and agree with the usage conditions.
* After activation, click on view key tot get a pop-up window asking for the verification code.
* First click on "Verification code" after which you get an image with 2 puzzle pieces, which you need to overlap each other using the slider below.
* After that, you will receive an email with the verification code you need to enter (within 60 seconds).
* Once confirmed, you get the API_ID, API_SECRET and API_URL

## PVOutput
[PVOutput](https://pvoutput.org/) is a free online service for sharing and comparing photovoltaic solar panel output data. It provides both manual and automatic data uploading facilities.

Output data can be graphed, analysed and compared with other pvoutput contributors over various time periods. The ability to compare with similar systems within close proximity allows both short and longer term performance issues to be easily identified. While PVOutput is primarily focused on monitoring energy generation, it also provides equally capabable facilities to upload and monitor energy consumption data from various energy monitoring devices.

The python script requires a PVOutput API_KEY and SYSTEM_ID to function.
* Login in PVOutput and goto your Settings page
* Select Enabled for API Access
* Click on New Key to generate your API key
* Make a note of your System Id
* Save your settings

## Configuration
Change in soliscloud_to_pvoutput.cfg the following lines with your above obtained secrets:
* soliscloud_api_id = 1300386381123456789
* soliscloud_api_secret = 304abf2bd8a44242913d704123456789
* soliscloud_api_url = https://www.soliscloud.com:13333
* pvoutput_api_key = 0f2dd8190d00369ec893b059034dde1123456789
* pvoutput_system_id = 12345

## Usage
### Windows 10
python soliscloud_to_pvoutput.py

### Raspberry pi
soliscloud_to_pvoutput.py scripts runs on my Raspberry pi with Raspbian GNU/Linux 11 (bullseye).

### Raspberry pi Configuration
Steps:
* create a directory solis in your home directory
* copy solis.sh, soliscloud_to_pvoutput.py and soliscloud_to_pvoutput.cfg in this solis directory
* change inside soliscloud_to_pvoutput.cfg the API secrets
* chmod + x solis.sh
* add the following line in your crontab -e:

```
2 5 * * * ~/solis/solis.sh > /dev/null
@reboot sleep 123 && ~/solis/solis.sh > /dev/null
```

### log files
Log files are written in the home subdirectory solis
* solis.log containing the data send to PVOutput (and maybe error messages)
* solis.crontab.log containing the crontab output (normally it will say that solis.sh is running).

### Example output solis.log

```
20220730 23:00:17: Outside solar generation hours (5..23)
Exiting program to start fresh tomorrow
20220731 06:34:07: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,06:33,0,20,-1,-1,,77.4
20220731 06:49:17: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,06:48,5,20,-1,-1,,82.0
20220731 06:54:20: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,06:53,6,20,-1,-1,,111.0
20220731 06:59:24: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,06:58,7,20,-1,-1,,170.1
20220731 07:04:28: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,07:03,8,20,-1,-1,,142.0
20220731 07:09:30: inverter temperature: 36.1, AC voltage: 237.2 data=20220731,07:08,9,20,-1,-1,,143.6
```
