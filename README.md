# Blender Addon Updater

With this python module, developers can create auto-checking for updates with their blender addons as well as one-click version installs. Updates are retrieved using GitHubs code api, so the addon must have it's updated code available on GitHub and be making use of either GitHub tags or releases.

**This code is close but not yet production ready**
*This notice will change when ready for external use*

# Key Features
*From the user perspective*

- Uses GitHub repositories for source of versions and code
  - In the future, may have support for additional or custom code repositories
- One-click to check if update is available
- Auto-check: Ability to automatically check for updates in the background (user must enable)
- Ability to set the interval of time between background checks (if auto-check enabled)
- On a background check for update, contextual popup to tell user update available
- One-click button to install update
- Ability to install other (older) versions of the addon



# High level setup

![alt](/images/file_diagram.png)

This repository contains a fully working example of an addon with the updater code, but to integrate into another or existing addon, only the `addon_updater.py` and `addon_updater_ops.py` files are needed. 

`addon_updater.py` is an independent python module that is the brains of the updater. It is implemented as a singleton, so the module-level variables are the same wherever it is imported. This file should not need to be modified by a developer looking to integrate auto-updating into an addon. 

`addon_updater_ops.py` links the states and settings of the `addon_updater.py` module and displays the according interface. This file is expected to be modified accordingly to be integrated with into another addon, and serves mostly as a working example of how to implement the updater code. 


# About the example addon

Included in this repository is an example addon which is integrates the auto-updater feature. It is currently linked to this repository and it's tags for testing. To use in your own addon, you only need the `addon_upder.py` and `addon_updater_ops.py` files. Then, you simply need to make the according function calls

# addon_updater module settings

This section is a work in progress, but ultimately will provide simple documentation for all of the addon_updater module settings available and required. These are the settings applied directly to the addon_updater module itself.

*Required settings*

TBD

*Optional settings*

TBD

*User preference defined (ie optional but good to expose to user)*

TBD

Example changing or applying a setting:

```
from .addon_updater import Updater as updater
updater.addon = "addon_name"
```

# About addon_updater_ops

This is the code which acts as a bridge between the pure python addon_updater.py module and blender itself. It is safe and even advised to modify the addon_updater_ops file to fit the UI/UX wishes. You should not need to modify the addon_updater.py file.

### User preferences UI

![Alt](/images/updater_preferences.png)

Most of the key settings for the user are available in the user preferences of the addon, including the ability to restore the addon, force check for an update now, and allowing the addon to check for an update in the background

### Integrated panel UI

![Alt](/images/updater_preferences.png)

### Install different addon versions

![Alt](/images/install_versions.png)

In addition to grabbing the code for the most recent release or tag of a GitHub repository, this updater can also install other target versions of the addon through the popup interface. 



# Issues or help

If you are attempting to integrate this code into your addon and run into problems, please open a new issue. As the module improves, it will be easier for more developers to integrate updating and improve blender's user experience overall!
