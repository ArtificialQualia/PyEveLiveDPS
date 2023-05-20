# PyEveLiveDPS <img src="/app.ico" width="40" height="40">
PyEveLiveDPS (PELD) is a live DPS calculator and grapher for EVE Online

PELD uses EVE's combat logs making it fully compliant with EVE's EULA

It has the ability to track the following:  
- Outgoing and Incoming DPS
- Outgoing and Incoming Shield/Armor/Hull Logistics
- Outgoing and Incoming Cap transfers
- Outgoing and Incoming Neut/Nos
- Amount Mined in m3 or units mined

Here is an example of what it looks like in regular mode and compact mode:  
![PELD regular](http://i.imgur.com/lCzJGx1.png) ![PELD compact](http://i.imgur.com/MBKb4jo.png)

As of 2.0, PELD includes a breakdown of values based on pilot and weapon type.  Here are some examples:  
![Breakdown pvp](https://i.imgur.com/Id7wUuE.png) ![Breakdown pve](https://i.imgur.com/GAUtC5a.png)

~PELD now has a Fleet Mode that allows you to view the combat statistics of your entire fleet when they use PELD.~  
Note: the primary peld-fleet.com website has been taken offline due to lack of user interest, changes in the EVE API, and hosting fees.  
The source code for peld-fleet.com is still available on github and could be hosted by someone else if it were to be fixed. ([peld-fleet source code](https://github.com/ArtificialQualia/PELD-Server))  

## Download and Running
Download the latest version from here:  
https://github.com/ArtificialQualia/PyEveLiveDPS/releases

You have two download options:  
PELD-standalone requires no installation, but takes a few seconds to start up.  
PELD-installer will install PELD to your computer like a traditional application, and is much faster to start up.

If you plan on using PELD long term, it is recommended to use the PELD-installer version.

If you want PELD to overlay on top of your eve client, make sure you are running eve in borderless windowed mode.

You can run multiple copies to track different characters at the same time.  You can also set up profiles to save different graph settings and window position/size.

The packaged release is for Windows.  To run on Linux, run from source.  See below about how to run from source.  Other OSes are untested.

## Why a live DPS grapher?

There are a number of utilities that analyze your combat logs.  However, almost all of these utilities analyze your logs after the fact, which isn't as useful as getting that data in real time.

This tool provides a moving average of your DPS so you can make adjustments mid-fight and instantly see the results.  It also includes many additional features like pilot/weapon breakdowns, log playback, and fleet mode, along with many settings to customize your experience.  This program is also open source, so anyone can modify and improve it as they see fit.

How long of a time period to average your DPS over is a user configurable setting so you can adjust it to your weapon type(s).

Note that since it is a moving average, you will see peaks and valleys as hits fall 'off' the graph, and new ones are added.  You can increase the time period (up to 10 minutes) of the moving average to minimize this effect, but then it will be harder to see how much of an effect each hit is having.

## Why does PELD need my overview settings?

If you are using an overview pack that changes the display of your in-game DPS messages from the defaults that EVE uses, you must export your overview settings for PELD to use.  These overview settings are needed because the configuration of your overview changes the actual content of the text log messages that PELD monitors.  In order to properly parse the combat logs and extract information like weapon types, targets, etc., the overview settings are required.

PELD will ask you for your overview settings the first time you run it.  You can change the overview settings PELD uses at anytime in the 'Character' menu.

## Problems?  Feedback?

If you encounter any bugs or you think there are missing features please let me know [on the issues page](https://github.com/ArtificialQualia/PyEveLiveDPS/issues).

If you wish to contribute to the project codebase, I accept pull requests.

If you love the program enough that you feel compelled to donate, ISK donations are welcome to my eve character: **Demogorgon Asmodeous**

## Running from source
To run PELD directly from the source code, run the following commands with **Python 3.3-3.6**:
```
pip install -r requirements.txt
python ./PyEveLiveDPS/peld.py
```
If you want to build an .exe yourself, see BUILDING.md

If you are running on Linux, you may need to modify logreader.py to point to the correct directory where your eve logs are stored.  Also ensure your python includes tkinter.
