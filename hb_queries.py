#! /usr/bin/python2.7

# Copyright 2013, 2016 Jtmorgan, Lokal_Profil, Sebastian Berlin

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

import hb_config

class Query:
    """Queries for database tracking tables."""

    def __init__(self, wikidb, invitee_table):
        self.wikidb = wikidb
        self.invitee_table = invitee_table
        self.mysql_queries = {}
        self.make_teahouse_experiment_newbies()
        self.make_th_add_talkpage()
        self.make_th_experiment_invitees()
        self.make_update_th_invite_status()

    def make_teahouse_experiment_newbies(self):
        """Find invitee candidates.

        Invitiees must have:
        * registered in the last 2 days,
        * made 5 or more edits,
        * not been blocked.
        """

        query = u"""
INSERT IGNORE INTO {table:s}
(user_id, user_name, user_registration, user_editcount, sample_date)
SELECT user_id, user_name, user_registration, user_editcount, NOW()
FROM {wikidb:s}.user
WHERE user_registration > DATE_FORMAT(
    DATE_SUB(NOW(),INTERVAL {max_user_age:d} DAY),'%Y%m%d%H%i%s')
AND user_editcount >= {min_edits:d}
AND user_id NOT IN (
    SELECT ug_user FROM {wikidb:s}.user_groups WHERE ug_group = 'bot')
AND user_name not in (
    SELECT REPLACE(log_title,"_"," ") from {wikidb:s}.logging
    where log_type = "block" and log_action = "block"
    and log_timestamp >  DATE_FORMAT(
        DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))
""".format(table=self.invitee_table,
           wikidb=self.wikidb,
           max_user_age=hb_config.max_user_age,
           min_edits=hb_config.min_edits)
        self.mysql_queries['teahouse experiment newbies'] = query

    def make_th_add_talkpage(self):
        """Add talkpage page id for all invitees from today."""
        query = u"""
UPDATE {table:s} as i, {wikidb:s}.page as p
SET i.user_talkpage = p.page_id, i.ut_is_redirect = p.page_is_redirect
WHERE date(i.sample_date) = date(NOW())
AND p.page_namespace = 3
AND REPLACE(i.user_name, " ", "_") = p.page_title
AND i.user_talkpage IS NULL
""".format(table=self.invitee_table, wikidb=self.wikidb)
        self.mysql_queries['th add talkpage'] = query

    def make_th_experiment_invitees(self):
        """Find all invitees from today."""
        query = u"""
SELECT user_name, user_id, user_talkpage
FROM {table:s}
WHERE date(sample_date) = date(NOW())
AND invite_status IS NULL
AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)
""".format(table=self.invitee_table)
        self.mysql_queries['th experiment invitees'] = query

    def make_update_th_invite_status(self):
        query = u"""
UPDATE {table:s}
SET invite_status = %d, hostbot_skipped = %d
WHERE user_id = %d
""".format(table=self.invitee_table)
        self.mysql_queries['update th invite status'] = query

    def getQuery(self, query_type, query_vars=False):
        if query_type in self.mysql_queries:
            query = self.mysql_queries[query_type].encode("utf8")
            if query_vars:
                # should accept a list containing any number of vars
                query = query % tuple(query_vars)
            else:
                pass
            return query
        else:
            logging.warning(
                "Something went wrong with query of type {:s}."
                    .format(query_type)
            )
