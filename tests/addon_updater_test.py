# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""Tests for the addon updater module python code

Runs tests for each of the engines and major modules, including integration
tests with the actual services.

How to run inside blender interface (script editor):
    Open this file in a blender text editor, and press run.
    Because some code in the addon_updater.py file still require bpy, it must
    be run this way in the context of blender. However, tests will run by
    directly reading the code next this python file in the git repository.

How to run from command line (run blender from within tests folder)
    # Run all tests
    blender -b -P addon_updater_test.py

    # Run all tests within single class
    blender -b -P addon_updater_test.py -- TestEngines

    # Run specific test
    blender -b -P addon_updater_test.py -- TestEngines.test_gitlab
    blender -b -P addon_updater_test.py -- TestFunctions.test_version_tuple_from_text

Note! Running multiple tests in succession could lead to API rate limitations,
which will manifest primarily as errors in the TestEngines unit tests.
"""

import os
import sys
import unittest

import bpy

if "text" in dir(bpy.context.space_data):
    # Running inside the python console in blender
    UPDATER_MODULE_DIR = os.path.dirname(os.path.dirname(
        bpy.path.abspath(bpy.context.space_data.text.filepath)))
    QUIT_ON_COMPLETE = False
else:
    # Commandline script passed to blender, directory should be //tests/
    UPDATER_MODULE_DIR = os.path.dirname(os.getcwd())
    QUIT_ON_COMPLETE = True

sys.path.append(UPDATER_MODULE_DIR)
import addon_updater


class TestEngines(unittest.TestCase):

    def test_gitlab(self):
        """Test the gitlab updater"""

        updater = addon_updater.SingletonUpdater()
        updater.engine = "GitLab"
        updater.private_token = None
        updater.user = "theduckcow"
        updater.repo = "3645616"
        updater.website = "https://gitlab.com/TheDuckCow/test-updater-gitlab"

        # Check rate limits
        # https://docs.gitlab.com/ee/api/README.html#rate-limits

        self.run_engine_test(updater)

    def test_github(self):
        """Test the Github updater"""

        updater = addon_updater.SingletonUpdater()
        updater.engine = "Github"
        updater.private_token = None
        updater.user = "cgcookie"
        updater.repo = "blender-addon-updater"
        updater.website = "https://github.com/CGCookie/blender-addon-updater"

        # Check rate limitations (command will show if local limit reached)
        # curl "https://api.github.com/rate_limit"
        # More info: https://developer.github.com/v3/rate_limit/

        self.run_engine_test(updater)

    def test_bitbucket(self):
        """Test the Bitbucket updater"""

        updater = addon_updater.SingletonUpdater()
        updater.engine = "Bitbucket"
        updater.private_token = None
        updater.user = "theduckcow"
        updater.repo = "blender-addon-updater-bitbucket"
        updater.website = "https://bitbucket.org/TheDuckCow/blender-addon-updater-bitbucket"

        # Check rate limitations
        # https://confluence.atlassian.com/bitbucket/rate-limits-668173227.html

        self.run_engine_test(updater)

    def run_engine_test(self, updater):
        """Run a test for a single engine."""

        # Redefine where updating occurs within testing framework
        os.path.join(UPDATER_MODULE_DIR, "")
        updater._addon = "test_updater"
        updater._addon_package = ""
        updater._updater_path = os.path.join(UPDATER_MODULE_DIR, "test_updater")
        updater._addon_root = UPDATER_MODULE_DIR
        updater.verbose = False

        updater.current_version = (1, 0, 0)
        updater.backup_current = False
        updater.include_branches = True
        updater.use_releases = False

        # Test raw API call
        tag_url = updater.form_tags_url()
        _ = updater.form_branch_url("master")
        # branch_url = updater.form_branch_url("master")
        # parsed_tag = updater._engine.parse_tags()

        # verify ths raw request doesn't fail
        res = updater.get_raw(tag_url)
        self.assertIsNotNone(res)
        self.assertNotEqual(res, "")

        # verify and check output of parse request
        res = updater.get_api(tag_url)
        self.assertIsNotNone(res)
        self.assertTrue(len(res) > 0)

        # Test the end to end get tag names request
        tags = updater._get_tag_names()
        self.assertTrue(len(tags) > 0)
        # print("Found {} tags".format(len(tags)))

        # Grab link to an archive (should be master for all)
        link = updater.select_link(updater, updater._tags[0])
        self.assertIsNotNone(link)
        # print(link)

        # Test downloading to the staging folder,
        # clear folder first if needed
        staged_master = updater.stage_repository(link)
        self.assertTrue(staged_master)

        # now try downloading a non-master branch
        link = updater.select_link(updater, updater._tags[1])
        self.assertIsNotNone(link)
        staged_tag = updater.stage_repository(link)
        self.assertTrue(staged_tag)

        # Test the synchronous check function, knowing it should have an update
        updater._update_ready = None
        updater.check_for_update()
        self.assertTrue(updater._update_ready)

        # Test the synchronous check function, knowing it should have no update
        updater.current_version = (99, 0, 0)
        updater._update_ready = None
        updater.check_for_update()
        self.assertFalse(updater._update_ready)


class TestFunctions(unittest.TestCase):
    """Unit tests not dependent on specific updater engines.

    Test will run with the GitHub engine

    TODO, add:
        # set_check_interval
        # create_backup
        # run_update
        # restore_backup
        # unpack_staged_zip
        # deepMergeDirectory
        # set_updater_json
        # set_tag
        # test with different min/max update versions set
    """

    def test_version_tuple_from_text(self):
        """Test tuple extraction examples"""

        updater = addon_updater.SingletonUpdater()
        updater.include_branches = False  # otherwise could treat as branch name

        # structure of: input, expected
        test_cases = [
            ["0.0.0", (0, 0, 0)],
            ["v0.0.0", (0, 0, 0)],
            ["v0.0", (0, 0)],
            ["v0.0 beta", (0, 0)],
            ["version 1,2,3 beta", (1, 2, 3)]
        ]

        for case in test_cases:
            res = updater.version_tuple_from_text(case[0])
            self.assertEqual(res, case[1])

    def test_reload_callback(self):
        """Test the reload function which disables and re-enables addon"""
        updater = addon_updater.SingletonUpdater()
        updater.auto_reload_post_update = True
        updater._addon_package = "blender-addon-updater-github"  # test override
        updater.reload_addon()  # assert no error


if __name__ == '__main__':
    print("Running Updater Tests")
    if QUIT_ON_COMPLETE:
        # Running in command line, exclude blender startup args
        test_args = (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
        sys.argv = [os.path.basename(__file__)] + test_args
        unittest.main(exit=QUIT_ON_COMPLETE, argv=sys.argv)
    else:
        # Running within blender UI script
        unittest.main(exit=QUIT_ON_COMPLETE)
