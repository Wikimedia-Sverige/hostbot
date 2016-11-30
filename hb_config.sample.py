import page_reader

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
# Parameters can be defined as a value (see max_user_age) or be read
# from a page (see min_edits). The latter takes page title and
# variable name as parameters.

# The page on the wiki where the invitation parameters are defined as
# JSON.
invitation_parameters_page = "User:FikarummetBot/Invitation_parameters"

# The maximum age (time since account registration), in days, that a
# user may have to qualify for invitation.
max_user_age = 2

# The minimum number of edits that a user must have made to qualify
# for invitation.
min_edits = page_reader.read_json_value(
    invitation_parameters_page,
    "min_edits"
)

# The message that is posted on an invitee's talk page. {inviter:s} is the
# name of the user being mentioned as contact.
# Each literal { or } must be escaped by a second instance of the same character.
message = '{{{{subst:Wikipedia:Teahouse/HostBot_Ivitation|inviter={inviter:s}}}}}'

# The summary for the message. {invitee:s} is the name of the invited user.
summary = '{invitee:s}, you are invited to the Teahouse!'

# The user that can be mentioned in `message` above. A user will be
# selected at random from this list, for each
# message. page_reader.read_user_list_page() can be used to retrieve
# user names from a wiki page with one user link per line.
inviters = ["Inviting_user"]
