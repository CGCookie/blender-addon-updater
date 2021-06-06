# How to contribute to the Blender Addon Updater.

We use the standard GitHub forking workflow. You can fork this repostiory, make your changes, and then merge them back with a pull request.

To ensure developers have easy access to the latest version of the addon updater, we only have a single branch. This should be the target of all pull requests.

## Running tests

If you are making anything beyond a trivial change or documentation edit, please try to run the automated tests. There are two ways to run the tests, listed below. However these do not fully cover all behavior of the updater, especially the user interface flow, so be sure to manually test by installing your version of the addon too. Be sure to test the full update/revert flow, which you can manually force by artificially lowering the addon version number (e.g. to 0.1.0).

Word to the wise: Don't shoot yourself in the foot! Be sure to make your edits to the updater in a place outside of the blender addons folder, and then install it like a normal addon (or use a script to copy the python files into place) between edits. This way you can test the full addon, without risking having your code delete (since the addon updater will indeed replace itself if you trigger an update/install version target).

### Run tests from Blender text editor

Open up any (recent) version of blender, such that you have a console window visible (Windows users: Window > Toggle console, Mac/Linux: start blender from command line). Then, load in the `/tests/addon_updater_test.py` file. Press run, and verify "All tests pass" in the output.

### Run tests on command line

You can run the tests by specifying it as a script to run on command line. For instance:

```
cd tests
Blender -b -P addon_updater_test.py
cd ../

```

You should be able to validate you get tests outputs like so:

```
..
----------------------------------------------------------------------
Ran 5 tests in 4.969s

OK

```

If there are any errors, please correct these before submitting a pull request!