## Building a new release
New releases are automatically built using [AppVeyor](https://www.appveyor.com).  This allows non-Windows users to be able to make builds, and also makes the entire process of making a release easier.

If you are just building locally for testing, see below about "Building locally"

## How to use AppVeyor
AppVeyor is configured via the `appveyor.yml` file.  Currently, it automatically builds on tag and pushes the zipped executable and README back to GitHub Releases.

Whenever it's time for a new release, simply push a tag so AppVeyor takes notice.

Edit the release on GitHub afterwards to add patch notes, if applicable.  Else the release description may default to a blank message or the latest commit message.

Automatic builds need to be enabled at AppVeyor and the `auth_token` needs to be set from a GitHub account with write access to the repo.

### Configuring AppVeyor

1. [Log in at AppVeyor](https://ci.appveyor.com) using your GitHub credentials.
2. Click `(+) New Project` in the top left, then `GitHub` > `Authorize GitHub` for public projects.
3. Back in AppVeyor, mouse over `PyEveLiveDps` and click `(+) Add` on the far right.

### Configuring `auth_token`

1. [Log in at AppVeyor](https://ci.appveyor.com) using your GitHub credentials.
2. On GitHub, [generate a new access token](https://github.com/settings/tokens):
    1. Click `Generate new token` in the top right.
    2. Name it `AppVeyor` and check `public_repo`.
    3. Copy the resulting token somewhere safe.
3. On AppVeyor, [encrypt the token](https://ci.appveyor.com/tools/encrypt) for safe use in the config file:
    1. Paste the previously generated token and click `Encrypt`.
    2. In `appveyor.yml`, set `auth_token: secure:` to the encrypted token from last step.  *DO NOT* use the unencrypted token here or bad things can happen to your repos!
    3. Commit and tag the change containing the updated auth token, then push.

From here on, AppVeyor will autonomously process each tagged commit without further intervention.

## Building locally
To build locally, you must build from a Windows machine.  
You may encounter errors about missing libraries (api-ms-win-crt-*.DLL), depending on your version of Windows.  This is 'ok' in most cases, but may not work on all devices.  Follow the instructions [here](https://github.com/pyinstaller/pyinstaller/issues/1566) about downloading the Windows SDK and adding the .dll folders to your PATH.  
Run the following commands with **Python 3.5**:
```
pip install -r requirements.txt
pip install pyinstaller
pyinstaller setup.spec
```
Executable will then be located in ./dist/