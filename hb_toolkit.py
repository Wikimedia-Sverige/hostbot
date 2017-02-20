#! /usr/bin/env python

# Copyright 2015-2016 Jtmorgan, Lokal_Profil, Sebastian Berlin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from datetime import datetime, timedelta
import sys
import logging

import dateutil.parser
import requests
import requests.packages.urllib3

import hb_output_settings
import config_reader

requests.packages.urllib3.disable_warnings()

class Eligible:

    def __init__(self):
        self.api_url = config_reader.get("apiurl")

    def getLatestEditDate(self, user_name):
        """
        Get the date of the user's most recent edit
        See: https://www.mediawiki.org/wiki/API:Usercontribs
        Example: https://en.wikipedia.org/w/api.php/?ucprop=timestamp&ucuser=Jtmorgan&list=usercontribs&action=query&ucshow=top&uclimit=1&ucdir=older
        """

        parameters = {
            "action" : "query",
            "list" : "usercontribs",
            "ucuser" : user_name,
            "uclimit" : 1,
            "ucdir" : "older",
            "ucshow": "top",
            "ucprop": "timestamp",
            "format": "json",
            }

        api_req = requests.get(self.api_url, params=parameters)
        # print api_req.url
        api_data = api_req.json()
        try:
            edit_timestamp = api_data["query"]["usercontribs"][0]["timestamp"]
            latest_edit_date = dateutil.parser.parse(edit_timestamp, ignoretz=True).date()
        except IndexError:
            # TODO raise a different error which determineInviterEligibility()
            # can except for more clarity.
            logging.warning(
                "The user {:s} has not made any edits and should not be an inviter!".format(user_name)
            )
            raise
        return latest_edit_date

    def getBlockStatus(self, user_name):
        """
        Find out whether the user is currently blocked from editing
        See: https://www.mediawiki.org/wiki/API:Users
        Example: https://en.wikipedia.org/w/api.php?action=query&list=users&ususers=Willy_on_Wheels~enwiki&usprop=blockinfo
        """
        parameters = {
            "action" : "query",
            "list" : "users",
            "ususers" : user_name,
            "usprop" : "blockinfo",
            "format": "json",
            }
        blocked = False
        api_req = requests.get(self.api_url, params=parameters)
        # print api_req.url

        api_data = api_req.json()
        if "blockid" in api_data["query"]["users"][0].keys():
            blocked = True
        else:
            pass
        # print blocked
        return blocked

    def meetsEditDateThreshold(self, latest_edit_date, threshold):
        meets_threshold = False
        cur_date = datetime.utcnow().date()
        threshold_date = cur_date - timedelta(days=threshold)
        if latest_edit_date >= threshold_date:
            meets_threshold = True
        else:
            pass
        return meets_threshold

    def determineInviterEligibility(self, inviter, threshold):
        """
        Takes a username and a date.
        """
        is_eligible = False
        is_blocked = self.getBlockStatus(inviter)
        try:
            latest_edit_date = self.getLatestEditDate(inviter)
        except IndexError:
            return False
        is_active = self.meetsEditDateThreshold(latest_edit_date, threshold)
        if is_active and not is_blocked:
            is_eligible = True
        else:
            pass
        return is_eligible

    def determineInviteeEligibility(self, invitee):
        """
        Takes a tuple of user_name, user_id, userpage_id.
        """

        is_blocked = self.getBlockStatus(invitee["id"])
        if is_blocked:
            logging.info(
                "User '{}' was not eligible; blocked.".format(invitee["name"])
            )
            return False
        if invitee["talkpage_id"] is not None:
            talkpage_path = "User talk:{}".format(invitee["name"])
            has_skip_string = self.checkTalkPage(
                talkpage_path,
                invitee["talkpage_id"],
                config_reader.get("skip_strings")
            )
            if has_skip_string:
                logging.info(
                    "User '{}' was not eligible; has skip string.".format(
                        invitee["name"]
                    )
                )
                return False
            has_skip_template = self.checkTalkPage(
                talkpage_path,
                invitee["talkpage_id"],
                config_reader.get("skip_templates"),
                u"{{{{\s*{}\s*[}}|]"
            )
            if has_skip_template:
                logging.info(
                    "User '{}' was not eligible; has skip template."
                        .format(invitee["name"])
                )
                return False
#             print invitee[0] + str(has_skip_template)
        return True

    def checkTalkPage(self, page_path, page_id, strings, regex_template=None):
        """Takes a list of strings. If any of those words appear in the given
        page, return True, else False. If regex_template is given, a
        regex is created by inserting the strings in regex_template
        and the searching for that regex.

        """

        tp_text = self.getPageText(page_path, page_id)
        if regex_template is not None:
            for string in strings:
                regex = regex_template.format(string)
                if re.search(regex, tp_text, re.I | re.U):
                    return True
            return False
        else:
            # Check if any of the strings are present in the page content.
            return any(s in tp_text for s in strings)

    def getPageText(self, page_path, page_id, section=False): #create a generic class?
        """
        Gets the raw text of a page or page section.
        Sample: http://meta.wikimedia.org/w/api.php?action=query&prop=revisions&titles=Grants:IdeaLab/Introductions&rvprop=content&rvsection=21&format=jsonfm
        """
        api_params={
            'action': 'query',
            'prop': 'revisions',
            'titles': page_path,
            'rvprop' : 'content',
            'format': "json"
        }
        if section:
            api_params['rvsection'] = section
        else:
            pass
        try:
            response = requests.get(self.api_url, params=api_params)
            doc = response.json()
            text = doc['query']['pages'][str(page_id)]['revisions'][0]['*'] #note page_id as str
        except:#if there's an error, text is an empty string. Keeps the system working.
            text = ""
        return text

if __name__ == "__main__":
    """
    Run this script directly if you want to test it.
    Pass in the date threshold fron the command line.
    """
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1]) #what type of invites
    sub_date = int(sys.argv[2]) #numeric threshold (days ago)
    e = Eligible()
    potential_inviters = params['inviters']
    eligible_inviters = [x for x in potential_inviters if e.determineInviterEligibility(x, sub_date)]
    print potential_inviters
    print eligible_inviters
