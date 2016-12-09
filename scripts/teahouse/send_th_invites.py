#! /usr/bin/env python

# Copyright 2012, 2016 Jtmorgan, Sebastian Berlin

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
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import random

import hb_toolkit
import hb_output_settings
import hb_profiles
import page_reader
import hb_config

def getEligibleInviters(elig_check, potential_inviters):
    """Filter out inviters with no edits in the last 21 days."""
    eligible_inviters = [x for x in potential_inviters if elig_check.determineInviterEligibility(x, 21)]
    return eligible_inviters

def getEligibleInvitees(elig_check, potential_invitees):
    """
    Takes an eligibility checker object, a list of keywords, and
    a list of invite candidates (user_name, user_id, talkpage_id).
    Returns a dictionary with lists of eligible and ineligible invitees.
    """
    eligible_invitees = [x for x in potential_invitees if elig_check.determineInviteeEligibility(x)]
    return eligible_invitees

def runSample(invitee, inviter):
    prof = hb_profiles.Profiles(
        user_name=invitee["name"],
        user_id=invitee["id"],
        page_id=invitee["talkpage_id"]
    )
    prof.invited = False
    prof.skip = False
    prof = inviteGuests(prof, inviter)
    return prof

def inviteGuests(prof, inviter):
    """
    Invites todays newcomers.
    """
    if inviter:
        prof.invite = hb_config.message.format(inviter=inviter).encode('utf-8')
    else:
        # Calling format even if there is no inviter field, to always
        # have the same amount of curly brackets in the message.
        prof.invite = hb_config.message.format().encode('utf-8')
    prof.getToken()
    prof.publishProfile()
    return prof

if __name__ == "__main__":
    # params contains information about skipped templates, user talk
    # namespace and the query for getting candidates below.
    elig_check = hb_toolkit.Eligible()

    daily_sample = hb_profiles.Samples()
    daily_sample.insertInvitees("teahouse experiment newbies") #need to generalize for TWA too
    daily_sample.updateTalkPages("th add talkpage") #need to generalize for TWA too
    select_query_key = "th experiment invitees"
    candidates = daily_sample.selectSample(select_query_key, sub_sample=False)
    #make this a function
#     user_name = sys.argv[2]
#     user_id = int(sys.argv[3]) #int so it will be committed to the db
#     page_id = sys.argv[4]
#     candidates = [(user_name, user_id, page_id)]
    if len(candidates) > 150:
        candidates = random.sample(candidates, 150) #pull 150 users out randomly
#     inviters = params['inviters'] #for TWA
    if hb_config.inviters and "{inviter:s}" not in hb_config.message:
        print "WARNING: Inviters specified ({}), but no inviter field in message ('{}').".format(hb_config.inviters, hb_config.message)
        inviters = None
    elif not hb_config.inviters and "{inviter:s}" in hb_config.message:
        raise Exception("Inviter field in message ('{}'), but no inviters specified.".format(hb_config.message))
    else:
        # Only make eligible inviter list if there is a list of
        # inviters to choose from *and* the message contain inviter
        # slot.
        inviters = getEligibleInviters(elig_check, hb_config.inviters)
    invitees = getEligibleInvitees(elig_check, candidates)

    print "Invitees ({}): {}".format(len(invitees), invitees)
    print "Inviters: {}".format(inviters)

    skipped_editors = [x for x in candidates if x not in invitees]
#     print skipped_editors
    for invitee in invitees:
        if not inviters:
            inviter = None
        else:
            inviter = random.choice(inviters)
        profile = runSample(invitee, inviter)
        daily_sample.updateOneRow("update th invite status", [int(profile.invited), int(profile.skip), profile.user_id])
    for s in skipped_editors:
        daily_sample.updateOneRow("update th invite status", [0, 1, s[1]])

    daily_sample.updateTalkPages("th add talkpage") #need to generalize for TWA too
