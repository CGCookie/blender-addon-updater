# Blender Addon Updater

With this Python module, developers can create auto-checking for updates with their blender addons as well as one-click version installs. Updates are retrieved using GitHub's, GitLab's, or Bitbucket's code api, so the addon must have it's updated code available on GitHub/GitLab/Bitbucket and be making use of either tags or releases.

![alt](/images/demo_gif.gif)


:warning: **Please [see this page on known issues](https://github.com/CGCookie/blender-addon-updater/issues?q=is%3Aissue+is%3Aopen+label%3A%22Known+Issue%22), including available workarounds**

*Want to add this code to your addon? [See this tutorial here](http://theduckcow.com/2016/addon-updater-tutorial/)*

This addon has been updated to work with both blender 2.7x and 2.8x simultaneously, see [this section below](https://github.com/CGCookie/blender-addon-updater#Blender-27-and-28).


# Key Features
*From the user perspective*

- Uses [GitHub](https://github.com/), [GitLab](http://gitlab.com/) or [Bitbucket](https://bitbucket.org) repositories for source of versions and code
  - All mentions of GitHub hereafter also apply to GitLab and Bitbucket unless called out separately
- One-click to check if update is available
- Auto-check: Ability to automatically check for updates in the background (user must enable)
- Ability to set the interval of time between background checks (if auto-check enabled)
- On a background check for update, contextual popup to tell user update available
- One-click button to install update
- Ability to install other (e.g. older or dev) versions of the addon

With this module, there are essentially 3 different configurations:
- Connect an addon to a repository's releases & be notified when new releases are out and allow 1-click install (with an option to install master or another branch if enabled)
- Connect an addon to a repository's releases & be notified when new releases are out, but direct user to website or specific download page instead of one-click installing (code doesn't even need to be hosted in connected repo in this scenario, as it's only using the releases metadata)
- Connect an addon to a repository that doesn't have any releases, and allow use to 1-click install to a default branch and select from other explicitly included branches to install (does not us any version checking, will always pull the latest code even if the same)


*Note the repository is not currently setup to be used with single Python file addons, this must be used with a zip-installed addon. It also assumes the use of the user preferences panel dedicated to the addon.*

# High level setup

This module works by utilizing git releases on a repository. When a [release](https://github.com/CGCookie/blender-addon-updater/releases) or [tag](https://github.com/CGCookie/blender-addon-updater/tags) is created on GitHub/Bitbucket/Gitlab, the addon can check against the name of the tags/releases to know if an update is ready. The local addon version (in `bl_info`) is used to compare against that online name to know whether a more recent release is ready.

![alt](/images/file_diagram.png)

This repository contains a fully working example of an addon with the updater code, but to integrate into another or existing addon, only the `addon_updater.py` and `addon_updater_ops.py` files are needed.

`addon_updater.py` is an independent Python module that is the brains of the updater. It is implemented as a singleton, so the module-level variables are the same wherever it is imported. This file should not need to be modified by a developer looking to integrate auto-updating into an addon. Local "private" variables starting with _ have corresponding @property interfaces for interacting with the singleton instance's variables.

`addon_updater_ops.py` links the states and settings of the `addon_updater.py` module and displays the according interface. This file is expected to be modified accordingly to be integrated with into another addon, and serves mostly as a working example of how to implement the updater code.

In this documentation, `addon_updater.py` is referred to by "the Python Module" and `addon_updater_ops.py` is referred to by "the Operator File".

# About the example addon

Included in this repository is an example addon which is integrates the auto-updater feature. It is currently linked to this repository and it's tags for testing. To use in your own addon, you only need the `addon_updater.py` and `addon_updater_ops.py` files. Then, you simply need to make the according function calls and create a release or tag on the corresponding repository.

# Step-by-step as-is integration with existing addons

*These steps are for the configuration that provides notifications of new releases and allows one-click installation*

*These steps are also represented more thoroughly in [this text tutorial](http://theduckcow.com/2016/addon-updater-tutorial/)*

1) Copy the Python Module (addon_updater.py) and the Operator File (addon_updater_ops.py) to the root folder of the existing addon folder

2) import the updater operator file in `__init__.py` file e.g. `from . import addon_updater_ops` at the top with other module imports like `import bpy`

3) In the register function of `__init__.py`, run the addon's def register() function by adding `addon_updater_ops.register(bl_info)`.
  - Consider trying to place the updater register near the top of the addon's register function along with any preferences function so that if the user updates/reverts to a non-working version of the addon, they can still use the updater to restore backwards.

4) Edit the according fields in the register function of the `addon_updater_ops.py` file. See the documentation below on these options, but at the bare minimum set the GitHub username and repository.
  - Note that many of the settings are assigned in the `addon_updater_ops.py: register()` function to avoid having excess updater-related code in the addon's `__init__.py:register()` function, however because the updater module is shared across the addon, these settings could be made in either place.
  - If using GitLab or Bitbucket, then you must also assign the according engine value, the rest is the same setup.

5) To get the updater UI in the preferences draw panel and show all settings, add the line `addon_updater_ops.update_settings_ui(self,context)` to the end of the preferences class draw function.
  - Be sure to import the Operator File if preferences are defined in a file other than the addon's `__init__.py` where already imported, e.g. via `from . import addon_updater_ops` like before

-  Alternatively, a more condensed version of the UI preferences code may be draw with the sample function `addon_updater_ops.update_settings_ui_condensed(self, context, col)` instead of the above function.
-  Note that the `col` input is optional, but allows you to add this function into an existing structure of rows/columns. This condensed UI doesn't show settings for interval (just an auto-check toggle, will use default interval) nor does it provide the backup-restoring or target-install operations.

6) Add the needed blender properties to make the sample updater preferences UI work by copying over the blender properties from the sample demo addon's `DemoPreferences` class, located in the `__init__` file. Change the defaults as desired.

```
# addon updater preferences from `__init__`, be sure to copy all of them

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )

    ....

    updater_interval_minutes = bpy.props.IntProperty(
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
# updater.engine left at default assumes GitHub api/structure
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
    print("Updater returned " + str(res) + ", error occurred")
elif updater.update_ready == False:
  print("No update available")
elif updater.update_ready == None:
  print("You need to check for an update first")
```

**Update to a target version of the addon** *(Perform the necessary error checking, updater.tags will == [] if a check has not yet been performed or releases are not found. Additional direct branch downloads will be inserted as the first entries if `updater.include_branches == True`. Pass in a function object function_obj to run code once the updater has finished if desired, or pass in None)*

```
tag_version = updater.tags[2] # or otherwise select a valid tag
res = updater.run_update(force=False, revert_tag=None, callback=function_obj)
if res == 0:
  print("Update ran successfully, restart blender")
else:
  print("Updater returned " + str(res) + ", error occurred")
```


If utilizing updater.include_branches, you can grab the latest release tag by skipping the branches included (which appear first in the tags list)

```
n = len(updater.include_branch_list)
tag_version = updater.tags[n] # or otherwise select a valid tag
res = updater.run_update(force=False, revert_tag=None, callback=function_obj)
if res == 0:
  print("Update ran successfully, restart blender")
else:
  print("Updater returned " + str(res) + ", error occurred")
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
  - Note: Make sure to use the correct repo name based on the api engine used; {repo_name} is found in the following places:
    - GitHub: Retrieved from the url of the repository link. Example: https://github.com/cgcookie/{repo_name}
    - Bitbucket: Retrieved from the url of the repository link. Example: https://bitbucket.org/cgcookie/{repo_name}
    - GitLab: You must go to the repository settings page, and use the *project ID* provided; note that this is a (string-formated) number, not a readable name. Example url where found: https://gitlab.com/TheDuckCow/test-updater-gitlab/edit, only visible to owner/editors.
- **user:** The name of the user the repository belongs to
  - Type: String, e.g. "cgcookie"
  - Note: Required but not actually used with GitLab engine enabled

*Optional settings*

- **engine:**
  - Type: String, one of: ["github","gitlab","bitbucket"], not case sensitive
  - Default: "github"
  - This selection sets the api back end for retrieving the code. This must be set to match the appropriate online repository where releases/tags are hosted
- **private_token:**
  - Type: String
  - Default: None
  - Currently only supports private tokens for GitLab. Used only for granting access to private repositories for updating.
  - WARNING: Before providing or using a personal token, [PLEASE READ SECURITY COCNERN SECTION BELOW](https://github.com/CGCookie/blender-addon-updater/tree/dev#security-concerns-with-private-repositories)
- **addon:**
  - Type: String, e.g. "demo_addon_updater"
  - Default: derived from the `__package__` global variable, but recommended to change to explicit string as `__package__` can differ based on how the user installs the addon
  - Note this must be assigned once and at the very top of the UI file (addon_updater_ops.py) as the string is used in the bl_idname's for operator and panel registration.
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
- **updater_path:** Path location of stored JSON state file, backups, and staging of installing a new version
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
- **overwrite_patterns:** A list of patterns to match for which files of the local addon install should be overwritten by matching files in the downloaded version version
  - Type: List of strings, each item follows a match pattern supported by the python module fnmatch
  - Default: [], which is internally made equivalent to ["*.py","*.pyc"]
  - Notes: You can use wild card patterns, see documentation for fnmatch.filter. The new default behavior introduced here is setting ["*.py","*.pyc"] means it matches the default behavior of blender. Also note this only describes patterns to allow *overwriting*, if a file in the new update doesn't already exist locally, then it will be installed to the local addon.
  - Examples:
    - ["some.py"] In this method, only files matching the name some.py would be overwritten via the update. Thus, even if the updated addon had a newer __init__.py file, it would not replace the local version. This method could be used to build a file replacement whitelist.
    - ["*.json"] means all JSON files found in addon update will overwrite those of same name in current install. This would be useful if the addon only has configuration, read-only data that should be always updated with the addon. Note that default blender behavior would not overwrite such JSON files if already present in the local install, this gets around that
    - ["*"] means that all matching files found in the update would overwrite files in the local install. Note this was the behavior pre updater v1.0.4, this is also the safest option to use if you want to ensure all files always get updated with the newer version in the update, including resource files. Be mindful that any local or custom modified files may get overwritten.
    // also note that this is a new setting as of v1.0.4 of the updater; the previous behavior of the updater was using the equivalent setting of ["*"] which would mean that all files found in the update would overwrite files in the local install.
    - [] or ["*.py","*.pyc"] matches default blender behavior, ie same effect if user installs update manually through blender interface without deleting the existing addon first
- **remove_pre_update_patterns:** A list of patterns to match for which files of the currently installed addon should be removed prior to running the update
  - Type: List of strings, each item follows a match pattern supported by the python module fnmatch
  - Default: [], recommended/as configured in demo addon: ["*.pyc"]
  - Notes: This explicitly will delete all files in the local addon install which match any of the rules, and will run after a backup is taken (so the backup is complete), but before the overwrite_patterns are applied. If the structure or files of an addon may change in the future, it may be wise to set remove_pre_update_patterns to ["*.py","*.pyc"] which would ensure all python files are always removed prior to the update, thus ensuring no longer used files aren't present. Using it in this fashion would also negate the need to specify the same patterns in the overwrite_patterns option. Note this option only deletes files, not folders.
  - Examples:
    - ["*"] means all files in the addon (except those under the dedicated updater subfolder of the addon) will always be deleted prior to running the update. This is nearly equivalent to using clean=True in the run_update method (however that will also delete folders)
    -  ["*.pyc"] means pycache files are always removed prior to update, which is a safe
- **backup_ignore_patterns:** A setting to ignore certain files or folders when performing a backup prior to installing an update/target version, useful to avoid copying resources or large files that wouldn't be replaced by the update anyways (via not being included in the overwrite_patterns setting)
  - Type: List of strings
  - Default: None
  - Notes: You can use wild card patterns, see documentation for shutil.copytree `ignore` input parameter as this is where the list is passed into. This is similar but slightly different to the patterns used in overwrite_patterns and remove_pre_update_patterns, except these will also apply to folders
- **manual_only:** A setting which will permit only manual installs and not one-click updates
  - Type: Bool, e.g. False
  - Default: False
  - Notes: This is useful if you always want to direct the user to a specific download page, but still want them to receive update notifications.
- **showpopups:** A setting which when enabled will allow for popup notifications for new updates
  - Type: Bool, e.g. False
  - Default: True
  - Notes: This setting was introduced in v1.0.5, where previous functionality was equivalent to the setting being equal to True. Note that popups will only work if the proper configuration is provided to trigger them, ie triggering a background check for update in the appropriate location.
- **version_min_update:** A setting which sets the minimum allowable version to target installing, so that any earlier numbered releases will not appear in the target install dropdown or appear as notifications for updating
  - Type: Tuple e.g. (1,2) or (1,2,3), should match the number of separators in bl_info
  - Default: None
  - Notes:
    - This behaves as an "equal to or greater", example: if `version_min_update` is set to (1,1,1), then (1,1,1) and (1,1,2) are valid targets, but (1,1,0) would not be listed as an available install target.
    - This also impacts what is considered as an update. Example: if the current addon version locally is v1.5 with `version_min_update` set to be (1,8), the addon will not perceive v1.6 as an update and thus would not notify the user.
    - The most logical use for this setting is to assign the earliest addon version with a functional updater, so that users cannot downgrade to a version before there was an updater and thus not be able to easily revert back.
- **version_max_update:** A setting which sets the maximum allowable version to target installing, so the target version and any higher numbered releases will not appear in the target install dropdown or appear as notifications for updating
  - Type: Tuple e.g. (1,2) or (1,2,3), should match the number of separators in bl_info
  - Default: None
  - Notes:
    - This behaves as an "equal to or greater". Example: if `version_max_update` is set to (1,1,1), then (1,1,1) and (1,1,2) will be ignored targets (won't appear in target install dropdowns and won't trigger update notifications), but (1,1,0) would still be recognized as an available target and trigger update notifications.
     - This also impacts what is considered as an update. Example: if the current addon version locally is v1.5 with `version_max_update` set to be (1,6), the addon will not perceive v1.6 or v1.7 online as an update and thus would not notify the user.
- **skip_tag:** A setting which defines how to pre-process tag names
  - Type: Function, see example method `skip_tag_function` in the Operator File
  - Default: `skip_tag_function` defined in `addon_updater_ops.py`
  - Notes: This is where the `version_min_update` and `version_max_update` settings are utilized. Additionally, the source function `skip_tag_function` could be modified e.g. to parse out any tags including the text "dev" or similar such rules to limit what is counted as an available update and also what is listed in the target install dropdown.
- **subfolder_path:** Define the root location of the `__init__.py` file in the repository
  - Type: String
  - Default: "", meaning the root repository folder
  - Notes: Not required if your `__init__.py` file is in the root level of the addon. Otherwise, use this setting to indicate where it is located so the updater knows which folder to take updated files from
- **use_releases:** (GitHub only) Choose to pull updates from releases only instead of tags, and use release names instead of tag numbers in target-install dropdowns
  - Type: Bool
  - Default: False
  - Notes: If true, any tags that are not "annotated" (ie have release notes or attachments) will be filtered out, as tags are not necessarily releases. Additional note: if set to false, cannot pull release notes for GitHub repository (whereas BitBucket and GitLab do have release notes available via tags). This means that if in the future in-line release notes are included in the UI, this setting will need to be set to True in order to show release logs (not yet implemented as of v1.0.5)

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
- **async_checking:** If a background thread is currently active checking for an update, this flag is set to True and prevents additional checks for updates. Otherwise, it is set to false
  - Type: Bool
  - Default: False
  - Notes:
    - This may be used as a flag for conditional drawing, e.g. to draw a "checking for update" button while checking in the background
    - However, even if the user were to still press a "check for update" button, the module would still prevent an additional thread being created until the existing one finishes by checking against this internal boolean
- **json:** Contains important state information about the updater
  - Type: Dictionary with string keys
  - Default: {}
  - Notes: This is used by both the module and the operator file to store saved state information, such as when the last update is and caching update links / versions to prevent the need to check the internet more than necessary. The contents of this dictionary object are directly saved to a JSON file in the addon updater folder. The contents are periodically updated, such as to save timestamps after checking for update, or saving locally the update link of not updated immediately, or storing the "ignore update" decision by user.
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

Most of the key settings for the user are available in the user preferences of the addon, including the ability to restore the addon, force check for an update now, and allowing the user to immediately check for an update (still runs in the background)

![Alt](/images/condensed_ui.png)

This is an alternate, more condensed preferences UI example which removes more granular options such as settings for the intervals between update checks, restoring from backups, and targeting versions to install

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

# Configuring what files are removed, overwritten, or left alone during update

Since v1.0.4 of the updater module, logic exists to help control what is modified or left in place during the updating process. This is done through the overwrite_patterns and remove_pre_update_patterns settings detailed above. Below are the common scenarios or use cases

**I don't understand this feature and I just want to use the default configuration which matches blender's install behavior**

Fair enough, in that case use the following settings - or just remove the lines entirely from the Operator File as these are the default values assigned to the updater class object.

```
# only overwrite matching python files found in the update, files like .txt or .blend will not be overwritten even if newer versions are in the update
updater.overwrite_patterns = ["*.py","*.pyc"]
# don't delete any files preemptively
updater.remove_pre_update_patterns = [ ]
```

If you wanted to instead match the default behavior of the addon updater pre v1.0.4, then use the following
```
# overwrite any file found in the local install which has a corresponding file in the update
updater.overwrite_patterns = ["*"]
# don't delete any files files preemptively
updater.remove_pre_update_patterns = [ ]
```

**I want to shoot myself in the foot and make updating not work at all**

Or in other words... *don't* use the following setup, as it effectively prevents the updater from updating anything at all!

```
# don't overwrite any files matching the local install in the update
updater.overwrite_patterns = [ ]
# don't delete any files files preemptively
updater.remove_pre_update_patterns = [ ]
```

This would still add in *new* files present in the update not present in the local install. For this reason, this actually may be a valid setup if used in conjunction with clean_install set to True, which simulates a fresh install. When clean_install = True, these patterns are effectively rendered pointless, so it's still better to not define them in the way above.


**Addon contains only py files, no resources (e.g. JSON files, images, blends), and against better judgment, not even licenses or readme files**

In this example, we only need to worry about replacing the python files with the new python files. By default, this demo addon is configured so that new py files and pyc files will overwrite old files with matching paths/names in the local install. This is accomplished by setting `updater.overwrite_patterns = ["*.py","*.pyc"]` in the operator file. You could also be more explicit and specify all files which may be overwritten via `updater.overwrite_patterns = ["__init__.py", "module.py", "*.pyc"]` for example (noting the "*.pyc" is still there to ensure all caches are flushed).

Note that if in the future, a file is renamed e.g. from module.py to new_module.py, when the update runs (and assuming `remove_pre_update_patterns` has been left to it's empty list default), then the updater will copy in the new_module.py into the local install, while also leaving the previous version's module.py in place. The result will have both the module.py and new_module.py file in place.

If you wanted to future proof your updater to ensure no old python files are left around due to a changes in structure or filenames, it would be safe to instead set `updater.remove_pre_update_patterns = ["*.py","*.pyc"]` meaning all python files and cached files will always be removed prior to updating. After the update completes, the only python files that will be present are those that came directly from the update itself.

While you could also use `updater.remove_pre_update_patterns = ["*"]`, it is not recommended unless absolutely necessary. You never know when a user may try to place files in the addon subfolder, or if sometime down in the future you might want the updater to not clear everything out, so it's best to only explicitly delete the minimum which is needed, and be sure to plan ahead.

**Addon contains py files and resource files, but no user/local configuration files**

This is the more common use case. It is similar to the above, except now there are also additional files such as the readme.md, the license.txt, and perhaps a blend file with some models or other resources.

If the user were to install the update manually through the blender UI with an older version of the addon in place, it would actually only overwrite the py files. The readme.md and licenses.txt that existed previously would not change, they would not be overwritten. However, any new files in the update not in the local install (such as a new blend file) will be moved into the local install folder. If a blend file is in the local install prior to updating but is not found in the new addon update, it would still be left in place. Essentially, blender's default behavior is to only overwrite and update python files, and when copying in new resources it favors the files already present in the local install.

Instead of this default behavior, the following settings would be more appropriate for the situation of readme's and asset blends, since they may change between versions.

```
updater.overwrite_patterns = ["README.md", "*.blend"]
```

In this setup, the updater is told to always replace the readme file explicitly (note the case sensitivity). No other files are indicated to be overwritten, indicating for example the license file will never be overwritten with an update - that shouldn't be changing anyways. This setup would actually mean not even the python files are overwritten if the update has matching files to the local install. Not even the __init__.py file would be updated, which is where the next setting becomes useful.

The "*.blend" will result in any blend file being overwritten if matching locally to the update. e.g. /addonroot/assets/resources.blend will be replaced with the e.g. /addonroot/assets/resources.blend found in update repository. This would make sense if the blend file is static and not expected to be ever user modified.

```
updater.remove_pre_update_patterns = ["*.py","*.pyc"]
```

The second line tells the updater to delete all .py and .pyc files prior to updating, no matter what. This why we don't need to also add *.py into the `overwrite_patterns`, because if the python files have already been removed, then there's no chance for the update to have a matching python file in the local install (and thus no need to check against overwriting rules). This setup also has the benefit of never leaving old, unused python code around. if module_new.py is used in one version but then removed in the next, this setup of pre-removing all py files ensures it is deleted. Note that this doesn't do anything to any other files. Meaning existing files such as blends, images, JSON etc will all be left alone. With the exception of blend files (as per `overwrite_patterns` above), they also won't be overwritten - even if there are updates.

**Addon contains py files, resource files, and user/local configuration files**

This is the most intricate setup, but layers on more useful behavior even in unique situations.

Imagine an addon has a changing python code structure, assets which should be updated with each update, but also configuration files with default settings provided in the master repository, but local changes wanted to be kept. Furthermore, the user may install custom image textures saved in the addon folder so you will not know the names ahead of time, but you also want to ensure custom icon file updates can be made.

```
# example addon setup
__init__.py
module.py
icons/custom_icon.png
images/   # folder where custom png images will be installed
README.md
assets/default.blend
assets/customizable.blend

```

To accomplish the mentioned behavior, use the below configuration.

```
updater.overwrite_patterns = ["README.md", "custom_icon.png"]
updater.remove_pre_update_patterns = ["*.py", "*.pyc", "default.blend"]
```

Breaking this down, we always specify to overwrite the README and custom_icon.png files explicitly. No need to remove either in pre update since we expect they will be found in the update, and the overwrite patterns ensures they always get overwritten and only those files.

Then, we specify to delete all python files before running the update, to ensure the only python files are part of the latest release. We also force delete the file matching the name *default.blend.* If this was added as an overwrite pattern instead and the default.blend file name were ever renamed in the master repository, the updater would not end up removing this extra asset. And so we delete it directly, and presume the update will contain the appropriately named and updated blend file.

Just as importantly, note how the customizable.blend is not mentioned in either line. This means that there are no rules which would allow for this file to be overwritten or removed. This is desired since the user could have modified this file per their own needs, and we don't want to reset it. If the file was manually removed by the user or otherwise not present in a previous version of the addon, the update would still copy it over as found in the master repository.


**In conclusion**

If you are planning to modify the `overwrite_patterns` or `remove_pre_update_patterns` settings, be sure to plan and test it works as you expect. It's important to have "*.py" in at least one of them, or alternatively individually name all python file basenames in either of the two settings.

It is redundant to have the same rule in both settings, behavior of the `remove_pre_update_patterns` will supersede the more passive overwriting permission rules of `overwrite_patterns`

The pattern matching is done on an "or" basis, meaning in the set ["*.py", "module.py"], the second list item is redundant as the "*.py" already

The patterns only match to filenames, so there is no use in including in paths like assets/icon.png or directory names.

Finally, enabled verbose and check the console output after running an update! There are explicit printouts for when any files is "pre-removed", overwritten, or ignored for overwriting due to not matching a pattern. Use this to debug.


# Blender 2.7 and 2.8

This repository and example addon has been updated to work simultaneously for both Blender 2.7x and Blender 2.8x, though addon developers could still choose to host dedicated 2.8x versions separate from 2.7x versions while using this updater system. Note that annotations are applied to class fields programmatically instead of through coding syntax (e.g. you will not see `propname: bpy.props...`, but the same effect will be in place and there should be no console warnings)

Note that, as an addon developer, you have different options for supporting Blender 2.7 and 2.8 while still using this updater system. These are:

1) Make the addon work for 2.7x and 2.8x simultaneously (in the same way that this module and demo addon does).
    - This requires some extra work, in particular note the workaround of annotations as accomplished by the `make_annotations` function.
2) Have dedicated, separate releases for Blender 2.7x and 2.8x which are separated by a major version, and use min/max conversioning to isolate which users can update to which versions.
    - For instance, if an existing addon is version 1.5 and works on blender 2.79, then a feature-parity version for Blender 2.8 could be released as addon version 2.0; this 2.0 addon with have a `version_min_update` set to be 2.0 for the blender 2.8 code, and the Blender 2.7x code would set `version_max_update` to be 2.0 as well as a ceiling.
    - The next update to the Blender 2.79-compatible addon (released at the same time or earlier, to prevent 2.7x users from accidentally updating to breaking 2.8 code) should push this settings change to make sure users don't accidentally update to a version they shouldn't.
    - Note in this scenario, you also prevent being able to update Blender 2.7x version numbers to or beyond 2.0. Note that there is no obligation to simultaneously update the Blender 2.7x and 2.8x versions at the same time as the version numbers themselves are not actually linked in any way.
    - The 2.7x and 2.8x code would be kept in different branches, and tags would be made targeting those different branches accordingly. Given Blender 2.8x will be the long term future, it may make most sense to dedicate the master branch to be 2.8 and create a 2.7x branch for parallel legacy support, but the choice doesn't really matter as a tag is treated the same regardless of the source branch.
3) Parallel version releases with build attachments for each new version.
    - This method is in one way simple as the same version numbers would work for both Blender 2.7x and 2.8x code, while still having separate code in different branches so you don't have to make code (such as annotation syntax) compatible for both at the same time in the same files. You could even have everything in the same branch with just duplicate files (e.g. a ui.py and ui_28.py).
    - The crux of this method is that instead of the updater pulling down the raw code associated with the tag/release, it uses release attachments instead. You would need to build
    - This does require releasing the 2.7x and 2.8 code at the same time
    - Extra logic will need to be programmed in the `addon_updater_ops.py: select_link_function` function to parse for the correct attachment given the running version of blender (instead of just the first release attachment, the default behavior), as well as enabling the `use_releases` setting in the ops file
    - For reference, this is essentially the method developers use to maintain and distribute updates for operating-specific builds of addons


# Security concerns with private repositories

Support for private repositories is still a work in progress for Bitbucket and GitHub, while already available for GitLab. At this time, they are only supported via authentication through personal or private tokens. These are assigned to an individual user and while can be restricted what access they do or don't have, they can **effectively act as an alternate to a password.** While this updater module is configured to only *read/download* code, a private token would allow both read and write capabilities to anyone who knows how to use the according api. By nature of python modules, this private token is easily read in source code or can be reverse compiled in pyc code and used for malicious or unintended purposes.

For this reason, it is very important to be aware and setup tokens accordingly. As the authentication implementation advances here, the recommendations may change but in the meantime:
- GitLab: Supported through Personal Tokens
  - Tokens are not needed and should not be used for public repositories
  - Personal access tokens can be [viewed and created here](https://gitlab.com/profile/personal_access_tokens)
  - Consider whether to provide an expiration date. Once expired any existing installs using the token will no longer successfully pull updates from private repositories. Therefore, if a user has the updater-enabled addon installed but leverages an expired token, they will not be able to update.
  - Tokens should be enabled for api *read access* only, to limit (mis) uses.
  - This token is *user* specific, *not* repository specific; therefore, anyone with the token is able to read anything via the GitLab api to any repository this user has access to. **For this reason,** it is very important to **NOT USE YOUR PERSONAL ACCOUNT** to create a token. Rather, you are better suited to create a secondary "machine user" account which is used only for the purpose of api access. This 'user' should be assigned to the project as a "reporter" for minimum required capabilities.
  - Use at own risk and ensure to do according research to ensure there are no security risks or possible backlashes due to providing updating for private repositories on GitLab.
  - When in doubt, you can always revoke a personal token - but once revoked, it cannot be re-enabled and thus any existing installs using the token will no longer be able to pull from the private repo unless manually updating the addon themselves.
  - These are only recommendations. As indicated by the GPL license, software is provided as-is and developers are not held liable to mishandling which results in unwanted consequences such as malicious exploit of a badly implemented private repository updating.
- GitHub: Not yet supported
- Bitbucket: Not yet supported

# Issues or help

If you are attempting to integrate this code into your addon and run into problems, [please open a new issue](https://github.com/CGCookie/blender-addon-updater/issues). As the module improves, it will be easier for more developers to integrate updating and improve blender's user experience overall!

Please note that the updater code is built to be dependent on existing api's of the mentioned major source code repository sites. As these api's may be subject to change or interruption, updating capabilities may be impacted for existing users.
