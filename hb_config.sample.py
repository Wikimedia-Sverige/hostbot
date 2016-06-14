#! /usr/bin/env python2.7

# Wiki login details
username = 'MyBot'
password = 'mybotspassword'
apiurl = 'http://en.wikipedia.org/w/api.php'
indexurl = 'http://en.wikipedia.org/w/index.php'

# OAuth details
oauth_user_agent = 'Myuseragent'
consumer_token = u'...'
consumer_secret = u'secret'
access_token = u'...'
access_secret = u'secret'

# db details
host = 'enwiki.labsdb'
wikidb = 'enwiki_p'
dbname = 'mybotdb'
defaultcnf = '/data/project/labsusername/.my.cnf'
invitee_table = 'th_up_invitees'

# Teahouse settings
rootpage = 'Wikipedia:Teahouse'
editsumm = 'automatic edits by [[User:HostBot|HostBot]]'

## Invitation
# The message that is posted on an invitee's talk page. {inviter:s} is the
# name of the user being mentioned as contact.
message = '{{subst:Wikipedia:Teahouse/HostBot_Ivitation|inviter={inviter:s}}}'

# The summary for the message. {invitee:s} is the name of the invited user.
summary = '{invitee:s}, you are invited to the Teahouse!'
