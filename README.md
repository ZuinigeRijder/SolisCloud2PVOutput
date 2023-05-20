- [SolisCloud to PVOutput and/or Domoticz](#soliscloud-to-pvoutput-andor-domoticz)
  - [SolisCloud](#soliscloud)
  - [PVOutput](#pvoutput)
  - [Domoticz](#domoticz)
- [Configuration](#configuration)
- [Usage: Windows 10](#usage-windows-10)
- [Usage: Linux or Raspberry pi](#usage-linux-or-raspberry-pi)
  - [Linux or Raspberry pi configuration](#linux-or-raspberry-pi-configuration)
  - [log files](#log-files)
  - [Configuration with multiple inverters in one SolisCloud station](#configuration-with-multiple-inverters-in-one-soliscloud-station)
  - [Combined data of two PVOutput accounts/inverters](#combined-data-of-two-pvoutput-accountsinverters)
- [Example standard output of SolisCloud2PVoutput](#example-standard-output-of-soliscloud2pvoutput)

# SolisCloud to PVOutput and/or Domoticz
Simple Python3 script to copy latest (normally once per 5 minutes) SolisCloud portal inverter update to PVOutput portal and/or Domoticz.

The soliscloud_to_pvoutput.py script will get the first station id with the secrets of SolisCloud (see next section). Thereafter it will get the inverter id and serial number via the configured SOLISCLOUD_INVERTER_INDEX (default the first inverter). Then in an endless loop the inverter details are fetched and the following information is used:
* timestamp
* DC PV voltage (assuming no more than 4 strings)
* watt (current)
* watthour today
* inverter temperature (instead of outside temperature, you can still overrule with weather device)
* AC voltage (max voltage of 3 phases, used "Power Consumption" field, so read "AC Volt" for the "Power Used" column of PVOutput and ignore "Energy Used" column)

This information is used to compute the new information to be send to PVOutput and/or Domoticz, when the timestamp is changed.

Notes
* only between 5 and 23 hour data is fetched from SolisCloud and copied to PVOutput and/or Domoticz
* the script will exit outside 5 and 23
* Each new day the "watthour today" starts with 0
* Because the resolution of the SolisCloud watthour is in 100 Watt, a higher resolution is computed with current Watt
* if you have more than 1 station, more than 4 strings or a 3 phase inverter, you need to adapt the script

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

## Domoticz
[Domoticz](https://www.domoticz.com/) is a very light weight home automation system that lets you monitor and configure miscellaneous devices, including lights, switches, various sensors/meters like temperature, rainfall, wind, ultraviolet (UV) radiation, electricity usage/production, gas consumption, water consumption and many more. Notifications/alerts can be sent to any mobile device.

If you want to know how to configure in Domoticz your inverter, see [this discussion](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/discussions/18).

![alt text](https://user-images.githubusercontent.com/17342657/237064859-b7bcb83a-a753-4399-b60d-801bdd2741a3.png)

![alt text](https://user-images.githubusercontent.com/17342657/237064582-59fcd74b-5b04-4578-98a4-18819bf8482f.png)

# Configuration
Change in soliscloud_to_pvoutput.cfg the following lines with your above obtained secrets and domoticz configuration, including if you want to send to PVOutput, Domoticz or both. By default only output is send to PVOutput:
* send_to_pvoutput = True
* soliscloud_api_id = 1300386381123456789
* soliscloud_api_secret = 304abf2bd8a44242913d704123456789
* soliscloud_api_url = https://www.soliscloud.com:13333
* soliscloud_inverter_index = 0
* pvoutput_api_key = 0f2dd8190d00369ec893b059034dde1123456789
* pvoutput_system_id = 12345
* send_to_domoticz = False
* domot_url = http://192.168.0.222:8081
* domot_power_generated_id = 0
* domot_ac_volt_id = 0
* domot_inverter_temp_id = 0
* domot_volt_id = 0

# Usage: Windows 10
Make sure to go to the directory where soliscloud_to_pvoutput.py and soliscloud_to_pvoutput.cfg is located.
````
python soliscloud_to_pvoutput.py
````

# Usage: Linux or Raspberry pi
soliscloud_to_pvoutput.py scripts runs on my Raspberry pi with Raspbian GNU/Linux 11 (bullseye).

## Linux or Raspberry pi configuration
Steps:
* create a directory solis in your home directory
* copy solis.sh, soliscloud_to_pvoutput.py, soliscloud_to_pvoutput.cfg and logging_config.ini in this solis directory
* change inside soliscloud_to_pvoutput.cfg the API secrets
* chmod +x solis.sh
* add the following line in your crontab -e:

```
2 5 * * * ~/solis/solis.sh > /dev/null
@reboot sleep 123 && ~/solis/solis.sh > /dev/null
```

## log files
Log files are written in the home subdirectory solis
* solis.log containing the data send to PVOutput (and maybe error messages)
* solis.crontab.log containing the crontab output (normally it will say that solis.sh is running).

## Configuration with multiple inverters in one SolisCloud station

Make 2 PVOutput accounts (you need 2 email addresses) for each inverter a separate PVOutput account. Make sure to configure the PVOutput accounts and get the PVOutput API keys.

The solution is to have 2 scripts running in different directories (one for each inverter) and for the each directory you do modifications, e.g. the configuration to get the appropriate inverter and send the output to a appropriate PVOutput account as target.

Create two directories, copy the SolisCloud2PVOutput files (soliscloud_to_pvoutput.py, soliscloud_to_pvoutput.cfg, solis.sh and logging_config.ini) to each directory and configure in each directory soliscloud_to_pvoutput.cfg:
- solis
- solis2

In solis2 directory you change the following:
- modify soliscloud_to_pvoutput.cfg to point the second PVOutput account secrets and change the soliscloud_inverter_index to 1 (to get the data of the second inverter)
- rename solis.sh to solis2.sh and modify solis2.sh to go to directory solis2 (line 9: cd ~/solis2)

Have two cronrabs running (for solis.sh and solis2.sh)

## Combined data of two PVOutput accounts/inverters

if you also want the combined data of the two inverters, use a third PVOutput account (yet another email address) and use my python tool [CombinePVOutputSystems](https://github.com/ZuinigeRijder/CombinePVOutputSystems#combine-pvoutput-systems).

# Example standard output of SolisCloud2PVoutput

```
20220730 23:00:17: Outside solar generation hours (5..23)
Exiting program to start fresh tomorrow
....
20220904 17:52:32: data=20220904,17:50,7600,90,-1,227.7,36.5,161.5
20220904 17:56:34: data=20220904,17:55,7600,100,-1,227.3,36.4,161.5
20220904 18:01:42: data=20220904,18:00,7600,100,-1,226.7,36.2,161.4
20220904 18:05:46: data=20220904,18:05,7700,100,-1,226.9,36.1,161.4
20220904 18:10:51: data=20220904,18:10,7700,110,-1,227.4,36.1,161.4

```
