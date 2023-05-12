<a name="R1.11.0"></a>
# [Added support for multiple inverters (R1.11.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.11.0) - 12 May 2023

See this [discussion](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/discussions/23).

Added configuration item (make sure to add this new configuration item to soliscloud_to_pvoutput.cfg if you have an existing configuration) :
- soliscloud_inverter_index = 0

Added below information about multiple inverters to the README.md.


## Domoticz
[Domoticz](https://www.domoticz.com/) is a very light weight home automation system that lets you monitor and configure miscellaneous devices, including lights, switches, various sensors/meters like temperature, rainfall, wind, ultraviolet (UV) radiation, electricity usage/production, gas consumption, water consumption and many more. Notifications/alerts can be sent to any mobile device.

If you want to know how to configure in Domoticz your inverter, see [this discussion](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/discussions/18).

![alt text](https://user-images.githubusercontent.com/17342657/237064859-b7bcb83a-a753-4399-b60d-801bdd2741a3.png)

![alt text](https://user-images.githubusercontent.com/17342657/237064582-59fcd74b-5b04-4578-98a4-18819bf8482f.png)

## Configuration with multiple inverters in one SolisCloud station

Make 2 PVOutput accounts (you need 2 email addresses) for each inverter a separate PVOutput account. Make sure to configure the PVOutput accounts and get the PVOutput API keys.

The solution is to have 2 scripts running in different directories (one for each inverter) and for the each directory you do modifications, e.g. the configuration to get the appropriate inverter and send the output to a appropriate PVOutput account as target.

Create two directories, copy the SolisCloud2PVOutput files to each directory and configure in each directory soliscloud_to_pvoutput.cfg:
- solis
- solis2

In solis2 directory you change the following:
- modify soliscloud_to_pvoutput.cfg to point the second PVOutput account secrets and change the soliscloud_inverter_index to 1 (to get the data of the second inverter)
- rename solis.sh to solis2.sh and modify solis2.sh to go to directory solis2 (line 9: cd ~/solis2)

Have two cronrabs running (for solis.sh and solis2.sh)

## Combined data of two PVOutput accounts/inverters

if you also want the combined data of the two inverters, use a third PVOutput account (yet another email address) and use my python tool [CombinePVOutputSystems](https://github.com/ZuinigeRijder/CombinePVOutputSystems#combine-pvoutput-systems).




[Changes][R1.11.0]


<a name="R1.10.0"></a>
# [Fixed DOMOTICZ Volt value (R1.10.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.10.0) - 08 May 2023

https://github.com/ZuinigeRijder/SolisCloud2PVOutput/discussions/18#discussioncomment-5831867

[Changes][R1.10.0]


<a name="R1.9.1"></a>
# [minor domoticz fixes/defaults (R1.9.1)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.9.1) - 07 May 2023

- Check for DOMOTICZ_POWER_GENERATED_ID not zero
- Default domoticz id's are zero (so id is not send)

[Changes][R1.9.1]


<a name="R1.9.0"></a>
# [added option to send to pvoutput and/or to domoticz (R1.9.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.9.0) - 06 May 2023

 Added option to send to pvoutput and/or to domoticz.
Please make sure to add and configure new configuration lines to soliscloud_to_pvoutput.cfg if you had already installed SolisCloud2PVOuptup before:
* send_to_pvoutput = True
* [Domoticz]
* send_to_domoticz = False
* domot_url = http://192.168.0.222:8081
* domot_power_generated_id = 214
* domot_ac_volt_id = 215
* domot_inverter_temp_id = 0
* domot_volt_id = 0


[Changes][R1.9.0]


<a name="R1.8.0"></a>
# [fix error and warnings slipped in previous pull request (R1.8.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.8.0) - 28 Apr 2023

Last Pull Request there was an error in the logging call on line 109: logg**g**ing

https://github.com/ZuinigeRijder/SolisCloud2PVOutput/pull/16

Fixed error and also solved warnings.

[Changes][R1.8.0]


<a name="R1.7.0"></a>
# [Use Python logging, with a config file close to the previous format. (R1.7.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.7.0) - 17 Apr 2023

Externalise the basic logging configuration.
https://github.com/ZuinigeRijder/SolisCloud2PVOutput/pull/16


[Changes][R1.7.0]


<a name="R.16.0"></a>
# [Changed from API1.1.1 to API1.2 (R.16.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R.16.0) - 29 Nov 2022

Changed from API1.1.1 to API1.2 (SolisCloud has fixed typos in method names)

[Changes][R.16.0]


<a name="R1.5.0"></a>
# [Fix socket.timeout issue #8 (R1.5.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.5.0) - 18 Sep 2022

Fix for issue https://github.com/ZuinigeRijder/SolisCloud2PVOutput/issues/8
- catch socket.timeout and any other exception
- increase timeout from 10 to 30 (seconds)


[Changes][R1.5.0]


<a name="R1.4.0"></a>
# [AC voltage is max of 3 phases + bugfix high resolution watt (R1.4.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.4.0) - 05 Sep 2022

- AC voltage is max of 3 phases, so it works for 3 phase systems and 1 phase system
- fixed high resolution watt no longer used (bug slipped in previous release)


[Changes][R1.4.0]


<a name="R1.3.0"></a>
# [Added inverter temperature and AC Voltage to PVOutput fields (R1.3.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.3.0) - 04 Sep 2022

- Added inverter temperature for PVOutput Temperature column (instead of outside temperature, you can still overrule with weather device)
- Added AC Voltage for Power Used column (assuming 1 phase system, used "Power Consumption" field, so read "AC Volt" for the "Power Used" column of PVOutput and ignore "Energy Used" column)


[Changes][R1.3.0]


<a name="R1.2.0"></a>
# [Increased retries to 30 minutes and improved function naming (R1.2.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.2.0) - 13 Aug 2022

Small improvements, increased retries to 30 (minutes) instead of 10 (minutes)

[Changes][R1.2.0]


<a name="R1.1.0"></a>
# [API Secrets configuration moved out of python script into .cfg file (R1.1.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.1.0) - 05 Aug 2022

Change your API SECRETS in the configuration file "soliscloud_to_pvoutput.cfg". This way a new python script will not overwrite your API SECRETS. 


[Changes][R1.1.0]


<a name="R1.0.0"></a>
# [First release (R1.0.0)](https://github.com/ZuinigeRijder/SolisCloud2PVOutput/releases/tag/R1.0.0) - 05 Aug 2022

- added TODAY constant as yyyymmdd to compute it only once
- added inverter temperature and AC volt logging
- made pylint compliant
- make flake8 and black linters compliant
- improved readme
- small fixes
- moved sys.exit earlier
- exit outside 5-23 hours and small script improvements

[Changes][R1.0.0]


[R1.11.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.10.0...R1.11.0
[R1.10.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.9.1...R1.10.0
[R1.9.1]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.9.0...R1.9.1
[R1.9.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.8.0...R1.9.0
[R1.8.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.7.0...R1.8.0
[R1.7.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R.16.0...R1.7.0
[R.16.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.5.0...R.16.0
[R1.5.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.4.0...R1.5.0
[R1.4.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.3.0...R1.4.0
[R1.3.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.2.0...R1.3.0
[R1.2.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.1.0...R1.2.0
[R1.1.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/compare/R1.0.0...R1.1.0
[R1.0.0]: https://github.com/ZuinigeRijder/SolisCloud2PVOutput/tree/R1.0.0

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.7.0 -->
