# PyEveLiveDPS
PyEveLiveDPS (PELD) is a live DPS calculator and grapher for EVE Online

## Download and Running
Download the latest version from here:  
https://github.com/ArtificialQualia/PyEveLiveDPS/releases

To run, simply unzip and run peld.exe

You can run multiple copies to track different characters at the same time.

If you want PELD to overlay on top of your eve client, make sure you are running eve in borderless windowed mode.

## What is it?

PyEveLiveDPS (PELD) is a utility you can use to visualize both the incoming and outgoing DPS you are doing in real time.  

PELD runs in a window that sits on top of EVE, providing instant feedback in combat scenarios.  Is that target painter really helping you?  Is your angular velocity too high?  Are you shooting into the wrong resist?  PELD can help you find out what is helping and hurting your DPS.

## Why another DPS grapher?

There are a number of utilities already that analyze your combat logs.  However, almost all of these utilities analyze your logs after the fact, which isn't as useful in some scenarios as getting that data in real time.

There is one other live DPS grapher out there, but it only averages your DPS for the entire duration of the fight.  While that is still useful in its own right, this program provides a moving average of your DPS so you can make adjustments mid-fight and instantly see the results.  This program is also open source, so anyone can modify and improve it as they see fit.

How long of a time period to average your DPS over is a user configurable setting so you can adjust it to your weapon type(s).

Note that since it is a moving average, you will see peaks and valleys as hits fall 'off' the graph, and new ones are added.  You can increase the time period (up to 10 minutes) of the moving average to minimize this effect, but then it will be harder to see how much of an effect each hit is having.

## Packaging and Building Locally
To build locally, run the following commands with Python 3.5:
```
pip install -r requirements.txt
pyinstaller setup.spec
```
Executable will then be located in ./dist/peld/

Alternatively, if you want to run the python code without building, simply run:  
`python ./PyEveLiveDPS/peld.py`