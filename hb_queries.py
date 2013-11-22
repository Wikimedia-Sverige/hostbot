#! /usr/bin/python2.7

# Copyright 2013 Jtmorgan

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

class Query:
	"""queries for database tracking tables"""

	def __init__(self):
		self.mysql_queries = {
'twa sample' : {
	'string' : u"""INSERT IGNORE INTO twa_up_invitees (user_id, user_name, user_registration, edit_count, sample_group, dump_unixtime, invited, blocked, skipped) VALUES (%d, "%s", "%s", %d, "%s", %f, 0, 0, 0)""",
				},
'twa invites' : {
	'string' : u"""SELECT user_name, user_talkpage FROM twa_up_invitees WHERE dump_unixtime = (select max(dump_unixtime) from twa_up_invitees) AND invited = 0 AND blocked = 0 AND skipped = 0 AND sample_group = 'exp'""",
				},	
'twa blocked' : {
	'string' : u"""UPDATE twa_up_invitees AS t SET t.blocked = 1 WHERE REPLACE(t.user_name," ","_") IN (SELECT l.log_title FROM enwiki_p.logging AS l WHERE l.log_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 3 DAY),'%Y%m%d%H%i%s') AND l.log_type = "block" and l.log_action = "block")""",
				},
'twa talkpage' : {
	'string' : u"""UPDATE twa_up_invitees AS t, enwiki_p.page AS p SET t.user_talkpage = p.page_id WHERE p.page_namespace = 3 and p.page_is_redirect = 0 AND REPLACE(t.user_name," ","_") = p.page_title""",
				},						
'update invite status' : {
	'string' : u"""update twa_up_invitees set %s = 1 where user_name = '%s'""",
				},	
'username encoding test select' : {
	'string' : u"""select user_name FROM twa_up_invitees WHERE user_id = 20195519""",
				},								
			}		

	def getQuery(self, query_type, query_vars = False):
		if query_type in self.mysql_queries:
			query = self.mysql_queries[query_type]['string']
			if query_vars:
# 				print query_vars
				query = query % tuple(query_vars) #should accept a list containing any number of vars
# 				print query	
	
			else:
				pass
# 			print query		
			return query
		else:
			print "something went wrong with query of type " + query_type


