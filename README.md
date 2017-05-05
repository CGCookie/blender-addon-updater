# Blender Addon Updater

With this python module, developers can create auto-checking for updates with their blender addons as well as one-click version installs. Updates are retrieved using GitHubs code api, so the addon must have it's updated code available on GitHub and be making use of either GitHub tags or releases.

**This code is ready for production with public repositories**

*Want to add this code to your addon? [See this tutorial here](http://theduckcow.com/2016/addon-updater-tutorial/)*


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

With this module, there are essentially 3 different configurations:
- Connect an addon to GitHub releases & be notified when new releases are out and allow 1-click install (with an option to install master or another branch if enabled)
- Connect an addon to GitHub releases & be notified when new releases are out, but direct user to website or specific download page instead of one-click installing
- Connect an addon to GitHub that doesn't have any releases, and allow use to 1-click install to a default branch and select from other explicitly included branches to install (does not us any version checking, will alway pull the latest code even if the same)


*Note the repository is not currently setup to be used with single python file addons, this must be used with a zip-installed addon. It also assumes the use of the user preferences panel dedicated to the addon.*

# High level setup

This module works by utilizing git releases on a repository. When a [release](https://github.com/CGCookie/blender-addon-updater/releases) or [tag](https://github.com/CGCookie/blender-addon-updater/tags) is created on GitHub, the addon can check for and update to the code included in that tag. The local addon version number is checked against the versions on GitHub based on the name of the release or tag itself. 

![alt](/images/file_diagram.png)

This repository contains a fully working example of an addon with the updater code, but to integrate into another or existing addon, only the `addon_updater.py` and `addon_updater_ops.py` files are needed. 

`addon_updater.py` is an independent python module that is the brains of the updater. It is implemented as a singleton, so the module-level variables are the same wherever it is imported. This file should not need to be modified by a developer looking to integrate auto-updating into an addon. Local "private" variables starting with _ have corresponding @property interfaces for interacting with the singleton instance's variables.

`addon_updater_ops.py` links the states and settings of the `addon_updater.py` module and displays the according interface. This file is expected to be modified accordingly to be integrated with into another addon, and serves mostly as a working example of how to implement the updater code. 

In this documentation, `addon_updater.py` is referred to by "the Python Module" and `addon_updater_ops.py` is referred to by "the Operator File".

# About the example addon

Included in this repository is an example addon which is integrates the auto-updater feature. It is currently linked to this repository and it's tags for testing. To use in your own addon, you only need the `addon_upder.py` and `addon_updater_ops.py` files. Then, you simply need to make the according function calls and create a release or tag on the corresponding GitHub repository.

# Step-by-step as-is integration with existing addons

*These steps are for the configuration that provides notifications of new releases and allows one-click installation*

*These steps are also represented more thoroughly in [this text tutorial](http://theduckcow.com/2016/addon-updater-tutorial/)*

1) Copy the Python Module (addon_updater.py) and the Operator File (addon_updater_ops.py) to the root folder of the existing addon folder

2) import the updater operator file in `__init__.py` file e.g. `from . import addon_updater_ops` at the top with other module imports like `import bpy`

3) In the register function of `__init__.py`, run the addon's def register() function by adding `addon_updater_ops.register(bl_info)`.
  - Consider trying to place the updater register near the top of the addon's register function along with any preferences function so that if the user updates/reverts to a non-working version of the addon, they can still use the updater to restore backwards.

4) Edit the according fields in the register function of the `addon_updater_ops.py` file. See the documentation below on these options, but at the bare minimum set the GitHub username and repository. 
  - Note that many of the settings are assigned in the `addon_updater_ops.py: register()` function to avoid having excess updater-related code in the addon's `__init__.py:register()` function, however because the updater module is shared across the addon, these settings could be made in either place.

5) To get the updater UI in the preferences draw panel and show all settings, add the line `addon_updater_ops.update_settings_ui(self,context)` to the end of the preferences class draw function.
  - Be sure to import the Operator File if preferences are defined in a file other than the addon's `__init__.py` where already imported, e.g. via `from . import addon_updater_ops` like before

6) Add the needed blender properties to make the sample updater preferences UI work by copying over the blender properties from the sample demo addon's `DemoPreferences` class, located in the `__init__` file. Change the defaults as desired.

```
# addon updater preferences from `__init__`, be sure to copy all of them

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )
    
    ....

    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )
```

7) Add the draw call to any according panel to indicate there is an update by adding this line to the end of the panel or window: `addon_updater_ops.update_notice_box_ui()`
  - Again make sure to import the Operator File if this panel is defined in a file other than the addon's `__init__.py` file.
  - Note that this function will only be called once per blender session, and will only do anything if auto-check is enabled, thus triggering a background check for update provided the interval of time has passed since the last check for update. This is safe to trigger from draw as it is launched in a background thread and will not hang blender. 

8) Ensure at least one [release or tag](https://help.github.com/articles/creating-releases/) exists on the GitHub repository
  - As an alternative or in addition to using releases, the setting `updater.include_branches = True` in the `addon_updater_ops.py` register function allows you to update to specific git branches. You can then specify the list of branches for updating by using `updater.include_branche_list = ['branch','names']` for which the default is set to ['master']
  - If no releases are found, the user preferences button will always show "Update to Master" without doing any version checking


# Minimal example setup / use cases

If interested in implementing a purely customized UI implementation of this code, it is also possible to not use the included Operator File (addon_updater_ops.py). This section covers the typical steps required to accomplish the main tasks and what needs to be connected to an interface. This also exposes the underlying ideas implemented in the provided files.

**Required settings** *Attributes to define before any other use case, to be defined in the registration of the addon*

```
from .addon_updater import Updater as updater # for example
updater.user = "cgcookie"
updater.repo = "blender-addon-updater"
updater.current_version = bl_info["version"]
```

**Check for update** *(foreground using/blocking the main thread, after pressing an explicit "check for update button" - blender will hang)*

```
updater.check_for_update_now()

# convenience returns, values also saved internally to updater object
(update_ready, version, link) = updater.check_for_update()
	
```

**Check for update** *(foreground using background thread, i.e. after pressing an explicit "check for update button")*

```
updater.check_for_update_now(callback=None)
```

**Check for update** *(background using background thread, intended to trigger without notifying user - e.g. via auto-check after interval of time passed. Safe to call e.g. in a UI panel as it will at most run once per blender session)*

```
updater.check_for_update_async(background_update_callback)
# callback could be the function object to trigger a popup if result has updater.update_ready == True
```

**Update to newest version available** *(Must have already checked for an update. This uses/blocks the main thread)*

```
if updater.update_ready == True:
  res = updater.run_update(force=False, revert_tag=None, callback=function_obj)
  if res == 0:
  	print("Update ran successfully, restart blender")
  else:
  	print("Updater returned "+str(res)+", error occurred")
elif updater.update_ready == False:
  print("No update available")
elif updater.update_ready == None:
  print("You need to check for an update first")
```

**Update to a target version of the addon** *(Perform the necessary error checking, updater.tags will == [] if a check has not yet been performed or releases are not found. Additional direct branch downloads will be inserted as the first entries if `updater.include_branches == True`. Pass in a function object function_obj to run code once the updater has finished if desired, or pass in None)*

```
tag_version = updater.tags[2] # or otherwise select a valid tag
res = updater.run_update(force=False,revert_tag=None, callback=function_obj)
if res == 0:
	print("Update ran successfully, restart blender")
else:
	print("Updater returned "+str(res)+", error occurred")
```


If utilizing updater.include_branches, you can grab the latest release tag by skipping the branches included (which appear first in the tags list)

```
n = len(updater.include_branch_list)
tag_version = updater.tags[n] # or otherwise select a valid tag
res = updater.run_update(force=False,revert_tag=None, callback=function_obj)
if res == 0:
  print("Update ran successfully, restart blender")
else:
  print("Updater returned "+str(res)+", error occurred")
```



# addon_updater module settings

This section provides documentation for all of the addon_updater module settings available and required. These are the settings applied directly to the addon_updater module itself, imported into any other python file. 

**Example changing or applying a setting:**

```
from .addon_updater import Updater as updater
updater.addon = "addon_name"
```

*Required settings*

- **current_version:** The current version of the installed addon, typically acquired from bl_info
  - Type: Tuple, e.g. (1,1,0) or (1,1) or bl_info["version"]
- **repo:** The name of the repository as found in the GitHub link
  - Type: String, e.g. "blender-addon-updater"
- **user:** The name of the user the repository belongs to
  - Type: String, e.g. "cgcookie"

*Optional settings*

- **addon:**
  - Type: String, e.g. "demo_addon_updater"
  - Default: derived from the `__package__` global variable, but recommended to change to explicit string as `__package__` can differ based on how the user installs the addon
- **auto_reload_post_update:** If True, attempt to auto disable, refresh, and then re-enable the addon without needing to close blender
  - Type: Bool, e.g. False
  - Default: False
  - Notes: Depending on the addon and class setup, it may still be necessary or more stable to restart blender to fully load. In some cases, this may lead to instability and thus it is advised to keep as false and accordingly inform the user to restart blender unless confident otherwise. 
    - If this is set to True, a common error is thinking that the update completed because the version number in the preferences panel appears to be updated, but it is very possible the actual python modules have not fully reloaded or restored to an initial startup state. 
    - If it is set to True, a popup will appear just before it tries to reload, and then immediately after it reloads to confirm it worked. 
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
  - **backup_current** Create a backup of the current code when performing an update or reversion.

*User preference defined (ie optional but good to expose to user)*

- **check_interval_enable:** Allow for background checking.
- **check_interval_minutes:** Set the interval of minutes between the previous check for update and the next
- **check_interval_hours:** Set the interval of hours between the previous check for update and the next
- **check_interval_days:** Set the interval of days between the previous check for update and the next
- **check_interval_months:** Set the interval of months between the previous check for update and the next

*Internal values (read only by the Python Module)*

- **addon_package:** The package name of the addon, used for enabling or disabling the addon
  - Type: String
  - Default: `__package__`
  - Must use the provided default value of `__package__` , automatically assigned
- **addon_root:** The location of the root of the updater file
  - Type: String, path
  - Default: `os.path.dirname(__file__)`
- **api_url:** The GitHub API url
  - Type: String
  - Default: "https://api.github.com"
  - Notes: Should not be changed, but in future may be possible to select other API's and pass in custom retrieval functions
- **async_checking:** If a background thread is currently active checking for an update, this flag is set to True and prevents additional checks for updates. Otherwise, it is set to false
  - Type: Bool
  - Default: False
  - Notes:
    - This may be used as a flag for conditional drawing, e.g. to draw a "checking for update" button while checking in the background
    - However, even if the user were to still press a "check for update" button, the module would still prevent an additional thread being created until the existing one finishes by checking against this internal boolean
- **json:** Contains important state information about the updater
  - Type: Dictionary with string keys
  - Default: {}
  - Notes: This is used by both the module and the operator file to store saved state information, such as when the last update is and caching update links / versions to prevent the need to check the internet more than necessary. The contents of this dictionary object are directly saved to a json file in the addon updater folder. The contents are periodically updated, such as to save timestamps after checking for update, or saving locally the update link of not updated immediately, or storing the "ignore update" decision by user.
- **source_zip:** Once a version of the addon is downloaded directly from the server, this variable is set to the absolute path to the zip file created.
  - Type: String, OS path
  - Default: None
  - Notes: Path to the zip file named source.zip already downloaded
- **tag_latest** Returns the most recent tag or version of the addon online
  - Type: String, URL
  - Default: None
- **tag_names** Returns a list of the names (versions) for each tag of the addon online
  - Type: list
  - Default: []
  - Note: this is analogous to reading tags from outside the Python Module.
- **tags:** Contains a list of the tags (version numbers) of the addon
  - Type: list
  - Default: []
  - Notes: Can be used if the user wants to download and install a version other than the most recent. Can be used to draw a dropdown of the available versions.
- **update_link:** After check for update has completed and a version is found, this will be set to the direct download link of the new code zip file. 
- **update_ready:** Indicates if an update is ready
  - Type: Bool
  - Default: None
  - Notes:
    - Set to be True if a tag of a higher version number is found after checking for updates
    - Set to be False if a tag of a higher version number is not found after checking for updates
    - Set to be None before a check has been performed or cached
    - Using `updater.update_ready == None` is a good check for use in draw functions, e.g. to show different options if an update is ready or not or needs to be checked for still
- **update_version:** The version of the update downloaded or targeted
  - Type: String
  - Default: None
  - Notes: This is set to the new addon version string, e.g. `(1,0,1)` and is used to compare against the installed addon version
- **error:** If an error occurs, such as no internet or if the repo has no tags, this will be a string with the name of the error; otherwise, it is `None`
  - Type: String
  - Default: None
  - It may be useful for user interfaces to check e.g. `updater.error != None` to draw a label with an error message e.g. `layout.label(updater.error_msg)`
- **error_msg:** If an error occurs, such as no internet or if the repo has no tags, this will be a string with the description of the error; otherwise, it is `None`
  - Type: String
  - Default: None
  - It may be useful for user interfaces to check e.g. `updater.error != None` to draw a label with an error message e.g. `layout.label(updater.error_msg)`



# About addon_updater_ops

This is the code which acts as a bridge between the pure python addon_updater.py module and blender itself. It is safe and even advised to modify the Operator File to fit the UI/UX wishes. You should not need to modify the addon_updater.py file to make a customized updater experience.

### User preferences UI

![Alt](/images/updater_preferences.png)

Most of the key settings for the user are available in the user preferences of the addon, including the ability to restore the addon, force check for an update now, and allowing the addon to check for an update in the background

### Integrated panel UI

![Alt](/images/integrated_panel.png)

*If a check has been performed and an update is ready, this panel is displayed in the panel otherwise just dedicated to the addon's tools itself. The draw function can be appended to any panel.*

### Popup notice after new update found

![Alt](/images/popup_update.png)

*After a check for update has occurred, either by the user interface or automatically in the background (with auto-check enabled and the interval passed), a popup is set to appear when the draw panel is first triggered. It will not re-trigger until blender is restarted. Pressing ignore on the integrate panel UI box will prevent popups in the future.*


### Install different addon versions

![Alt](/images/install_versions.png)

*In addition to grabbing the code for the most recent release or tag of a GitHub repository, this updater can also install other target versions of the addon through the popup interface.* 


### If your repository doesn't have any releases...

![Alt](/images/no_releases.png)

*This is what you will find. See below on creating tags and releases* 


# How to use git and tags/releases

## What are they

From a [good reference website](https://git-scm.com/book/en/v2/Git-Basics-Tagging), a tag acts much like a branch except it never changes - it is linked with a specific commit in time. Tags can be annotated to have information like release logs or binaries, but at the base they allow one to designate major versions of code. This addon updater uses tag names in order to base the comparison version numbers, and thus to also grab the code from those points in times.

## Through the interface (GitHub specific)

View the releases tab at the top of any GitHub repository to create and view all releases and tags. Note that a release is just an annotated tag, and that this repository will function with both tags and releases. 

## Through command line (for any git-based system)

To show all tags on your local git repository use `git tag`

To create a new tag with the current local or pushed commit, use e.g. `git tag -a v0.0.1 -m "v0.0.1 release"` which will create an annotated tag. 

To push this tag up to the server (which won't happen automatically via `git push`), use `git push origin v0.0.1` or whichever according tag name


# Issues or help

If you are attempting to integrate this code into your addon and run into problems, please open a new issue. As the module improves, it will be easier for more developers to integrate updating and improve blender's user experience overall! 
