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

In this documentation, `addon_updater.py` is referred to by "the Python Module" and `addon_updater.py` is referred to by "the Operator File".

# About the example addon

Included in this repository is an example addon which is integrates the auto-updater feature. It is currently linked to this repository and it's tags for testing. To use in your own addon, you only need the `addon_upder.py` and `addon_updater_ops.py` files. Then, you simply need to make the according function calls

# Minimal example setup / use cases

If interested in implemented a purely customized UI implementation of this code, it is also possible to not use the included Operator File. This section covers the typical steps required to accomplish the main tasks and what needs to be connected to an interface. This also exposes the underlying ideas implemented in the provided files.

**Check for update** *(foreground using/blocking the main thread, after pressing an explicit "check for update button")*
- TBD

**Check for update** *(foreground using background thread, after pressing an explicit "check for update button")*
- TBD

**Check for update** *(background using background thread, triggered without notifying user)*
- TBD

**Update to newest addon**
- TBD

**Update to a target version of the addon**
- TBD

**
- TBD

# addon_updater module settings

This section is a work in progress, but ultimately will provide simple documentation for all of the addon_updater module settings available and required. These are the settings applied directly to the addon_updater module itself.

*Required settings*

- **current_version:** The current version of the installed addon
  - Type: Tuple, e.g. (1,1,0)
- **repo:** The name of the repository as found in the github link
  - Type: String, e.g. "addon-updater"
- **user:** The name of the user the repository belongs to
  - Type: String, e.g. "cgcookie"

*Optional settings*

- **addon:**
  - Type: String, e.g. "retopoflow"
  - Default: derived from the `__package__` global variable, but recommended to change to explicit string as `__package__` can differ based on how the user installs the addon
- **auto_reload_post_update:** If True, attempt to auto disable, refresh, and then re-enable the addon without needing to close blender
  - Type: Bool, e.g. False
  - Default: False
  - Notes: Depending on the addon and class setup, it may still be necessary to restart blender to fully load. In some cases, this may lead to instability and thus it is advised to keep as false and accordingly inform the user to restart blender. 
- **fake_install:** Used for debugging, to simulate in the user interface installing an update without actually modifying any files
  - Type: Bool, e.g. False
  - Default: False
  - Notes: Should be only used for debugging, and always set to false for production
- **updater_path:** Path location of stored json state file, backups, and staging of installing a new version
  - Type: String, absolute path location
  - Default: "{path to blender files}/addons/{addon name}/{addon name}_updater/"
- **verbose:** A debugging setting that prints additional information to the console
  - Type: Bool, e.g. False
  - Default: False
  - Notes: Messages will still be printed if errors occur, but verbose is helpful to keep enabled while developing or debugging this code. It may even be worthwhile to expose this option to the user through a blender interface property
- **website:** Website for this addon, specifically for manually downloading the addon
  - Type: String, valid url
  - Default: None
  - Notes: Used for no purpose other than allowing a user to manually install an addon and its update. It should be very clear from this webpage where to get the download, and thus may not be a typical landing page.

*User preference defined (ie optional but good to expose to user)*

- **check_interval_enable:** Allow for background checking.
- **check_interval_minutes:** Set the interval of minutes between the previous check for update and the next
- **check_interval_hours:** Set the interval of hours between the previous check for update and the next
- **check_interval_days:** Set the interval of days between the previous check for update and the next
- **check_interval_months:** Set the interval of months between the previous check for update and the next

*Internal values (read only)*

- **addon_package:** The package name of the addon, used for enabling or disabling the addon
  - Must use the provided default value of `__package__` , automatically assigned
- **addon_root:** 
- **api_url:** The GitHub API url
  - Notes: Should not be changed, but in future may be possible to select other API's and pass in custom retrieval functions
- **async_checking:** If a background thread is currently active checking for an update, this flag is set to True and prevents additional checks for updates. Otherwise, it is set to false
  - This may be used as a flag for conditional drawing, e.g. to draw a "checking for update" button while checking in the background
  - However, even if the user were to still press a "check for update" button, the module would still prevent an additional thread being created until the existing one finishes
- **backup_current** # doc WIP
- **connection_failed** # doc WIP
- **json:** Contains important state information about the updater
  - Type: Dictionary with string keys
  - This is used by both the module and the operator file to store saved state information, such as when the last update is and caching update links / versions to prevent the need to check the internet more than necessary.
- **latest_release** # doc WIP
- **releases** # doc WIP
- **source_zip:** The zip file containing the updated code
  Type: String, path to the zip file named source.zip already downloaded
- **tag_latest** # doc WIP
- **tag_names** # doc WIP
- **tags:** Contains a list of the tags (version numbers) of the addon
- **update_link:** 
- **update_ready:** 
- **update_version:** 


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
