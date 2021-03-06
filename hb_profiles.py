#! /usr/bin/env python

# Copyright 2013, 2016 Jtmorgan, Sebastian Berlin

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

import logging

import MySQLdb
import requests
from requests_oauthlib import OAuth1

import config_reader
import hb_output_settings as output_settings
import hb_queries
import hb_templates as templates

#TODO: add in logging again, more try statements
#hb_config to config
#get DB class out of profiles.py, rename

class Samples:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self):
        """
        Set up the db connection.
        """
        self.conn = MySQLdb.connect(
            host=config_reader.get("host"),
            db=config_reader.get("dbname"),
            read_default_file=config_reader.get("defaultcnf"),
            use_unicode=1,
            charset="utf8"
        )
        self.cursor = self.conn.cursor()
        self.queries = hb_queries.Query(config_reader.get("wikidb"),
                                        config_reader.get("invitee_table"))

    def insertInvitees(self, query_key):
        """
        Insert today's potential invitees into the database
        """
        query = self.queries.getQuery(query_key)
        self.cursor.execute(query)
        self.conn.commit()

    def updateTalkPages(self, query_key):
        """
        Updates the database with user talkpage ids (if they have one)
        """
        query = self.queries.getQuery(query_key)
        self.cursor.execute(query)
        self.conn.commit()

    def selectSample(self, query_key, sub_sample=False):
        """
        Returns a list of usernames and ids of candidates for invitation
        """
        sample_query = self.queries.getQuery(query_key)
        self.cursor.execute(sample_query)
        rows = self.cursor.fetchall()
        sample_set = [
            {
                "name": row[0],
                "id": row[1],
                "talkpage_id": row[2]
            }
            for row in rows
        ]
        if sub_sample:
        	sample_set = sample_set[:5]
        return sample_set

#         self.cursor.close()
#         self.conn.close()

    def updateOneRow(self, query_key, qvars):
        """
        Updates the database: was the user invited, or skipped?
        """
#         try:
        query = self.queries.getQuery(query_key, qvars)
        self.cursor.execute(query)
        self.conn.commit()
#         except:
#             print "something went wrong with this one"

class Profiles:
    """Create, parse, and post formatted messages to wiki."""

    def __init__(self, user_name=False, user_id=False, page_id=False):
        """
        Instantiate your editing session.
        """
        if user_name:
            self.user_name = user_name
            self.edit_summ = config_reader.get("summary").format(
                invitee=self.user_name
            )
        if user_id:
            self.user_id = user_id
        if page_id:
            self.page_id = str(page_id)
        self.api_url = config_reader.get("apiurl")
        self.user_agent = config_reader.get("oauth_user_agent")
        self.auth1 = OAuth1(unicode(config_reader.get("consumer_token")),
                client_secret=unicode(config_reader.get("consumer_secret")),
                resource_owner_key=unicode(config_reader.get("access_token")),
                resource_owner_secret=unicode(config_reader.get("access_secret")))

    def getToken(self):
        """
        Request a token for your request
        """
        response = requests.get(
            self.api_url,
            params={
                'action': "query",
                'meta': "tokens",
                'type': "csrf",
                'format': "json"
            },
            headers={'User-Agent': self.user_agent},
            auth=self.auth1,
        )
        doc = response.json() #why name this variable doc?
        try:
            self.token = doc['query']['tokens']['csrftoken']
        except:
            self.token = None

    def formatProfile(self, val):
        """
        takes in a dictionary of parameter values and plugs them into the specified template
        """

        # NOTE: This function is no longer used for inviting, but is
        # still used elswhere.
        message = config_reader.get("message").format(**val).encode('utf-8')
        return message

    def publishProfile(self):
        """
        Publishes one or more formatted messages on a wiki.
        """
        data = {
            'action': "edit",
            'title': "User talk:{}".format(self.user_name),
            'section': "new",
            'summary': self.edit_summ,
            'text': self.invite,
            'bot': 1,
            'token': self.token,
            'format': "json"
        }
        logging.debug("Sending request: {}".format(data))
        try:
#             print self.page_path
#             print self.edit_summ
#             print self.invite
            response = requests.post(
                self.api_url,
                data=data,
                headers={'User-Agent': self.user_agent},
                auth=self.auth1
                )
            self.invited = True
        except:
            logging.warning(
                "Unable to invite user '{}' at this time."
                    .format(self.user_name)
            )
