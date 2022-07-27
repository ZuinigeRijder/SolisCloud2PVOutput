[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# SolisCloud to PVOutput
Simple Python3 script to copy latest (normally once per 5 minutes) SolisCloud portal updates to PVOutput portal. 

The SolisCloud2PVOutput.py will get the first stationId with the secrets of SolisCloud (see next section). Thereafter it will get the first inverter id and serial number. Then in an endless loop the inverter details are fetched and the following information is used:
* timestamp
* acVoltage (assuming 1 phase system)
* dcPV (assuming no more than 4 strings)
* watt 
* totalWattHour

This information is used to compute the new information to be send to PVOutput, when the timestamp is changed.

Notes
* only between 5 and 23 hour data is fetched from SolisCloud and copied to PVOutput
* Each new day the totalWatthour starts with 0
* Because the resolution of the SolisCloud totalWatt is in 100 Watt, a higher resolution totalWatt is computed with current Watt
* if you have more than 1 station/inverter or a 3 phase inverter, you need to adapt the script

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
Change in SolisCloud2PVOutpy.py the following lines with your above obtained secrets:

SOLISCLOUD_API_ID = 'xxxx'
SOLISCLOUD_API_SECRET = b'xxxx'
SOLISCLOUD_API_URL = 'https://www.soliscloud.com:13333'
PVOUTPUT_API_KEY = 'xxxx'
PVOUTPUT_SYSTEM_ID = 'xxxx'

## Usage
### Windows 10
python SolisCloud2PVoutput.py

### Raspberry pi
python3 SolisCloud2PVoutput.py

## Raspberry pi Weezy
I have still an old Raspberry pi running at home, running SMASpot for transferring PV data via bluetooth from SMA Sunny Boy 4000TL to PVOutput. Wheezy is no longer supported, but I did not want to change my Raspberry pi OS to the latest, because of the configuration hassle of the already running raspberry pi since 2012. However, Python 3.2.3 is running on this Raspberry pi, and the SolisCloud2PVOutput.py scripts runs on this OS.

### Configuration
Steps:
* create a directory /home/pi/solis
* copy solis.sh and SolisCloud2PVOutput.py in this directory
* chmod + x solis.sh
* add the following line in your crontab -e:
```
*/30 5-23 * * * /home/pi/solis/solis.sh > /dev/null
```

### log files
Log files are written in directory /home/pi/solis
* solis.log containing the data send to PVOutput (and maybe error messages)
* solis.crontab.log containing the crontab output (normally it will say that solis.sh is running).

