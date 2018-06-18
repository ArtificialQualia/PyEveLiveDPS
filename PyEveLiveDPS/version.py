# Note: this is overwritten when a build is ran in AppVeyor, see appveyor.yml
import subprocess
try:
    version = subprocess.check_output(["git", "describe"]).decode('utf-8').strip()
except:
    version = 'please_install_git'