# PyEveLiveDPS
PyEveLiveDPS (PELD) is a live DPS calculator and grapher for EVE Online

# Download and Running
Download the latest version from here: 
https://github.com/ArtificialQualia/PyEveLiveDPS/releases

Extract zip file anywhere and run peld.exe

# Packaging and Building
To build locally, run the following commands with Python 3.5:

pip install -r requirements.txt
pyinstaller setup.spec

Executable will then be located in ./dist/peld/

Alternatively, if you want to run the python code without building, simply run:

python ./PyEveLiveDPS/peld.py