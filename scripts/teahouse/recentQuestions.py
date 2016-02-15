#! /usr/bin/python2.7

# Copyright 2012 Jtmorgan

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

import requests
import re
import hostbot_settings

# GET params from param class (we'll hard-code them for now)
# GET page section data through the API
# GET page section text for recent page sections
# TRUNCATE that text
# Pull the heading out
# PASTE that section number to a template
# POST the whole thing to a page

def main():
    api_url = hostbot_settings.oauth_api_url
    user_agent = hostbot_settings.oauth_user_agent
    page_path = hostbot_settings.rootpage + '/Questions'
    page_id = 34745517    
    output_path = hostbot_settings.rootpage + '/Questions-recent/%i'
    output_template = '''%s

    <!-- Fill in the "section" parameter with the question title from the Q&A page -->
    {{Wikipedia:Teahouse/Questions-answer|section=%s}}
    '''
    page_sections = getPageSectionData(api_url, page_path, toc_level = True)
    page = 1
    
    
def getPageSectionData(api_url, page_path, toc_level = False):
    """
    Returns the section titles and numbers for a given page in a list.
    Level arg can be used to return only sections of a given indentation level.
    Sample request: https://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia:Teahouse/Questions&prop=sections&format=jsonfm
    """
    api_params={
        'action': 'parse',
        'prop': 'sections',
        'page': page_path,
        'format': "json"            
    }        
    response = requests.get(api_url, params=api_params)                   
    data = response.json()
    secs_list = data['parse']['sections']  
    if toc_level:
        secs_list = [x for x in secs_list if x['toclevel'] == toc_level]
    return secs_list

def getPageText(api_url, page_path, page_id, section = False):
    """
    Gets the raw text of a page or page section.
    Sample: https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Wikipedia:Teahouse/Questions&rvprop=content&rvsection=3&format=jsonfm
    """
    api_params={
        'action': 'query',
        'prop': 'revisions',
        'titles': page_path,
        'rvprop' : 'content',
        'format': 'json'            
    }        
    if section:
        api_params['rvsection'] = section
    response = requests.get(api_url, params=api_params)                   
    data = response.json()
    raw_wikitext = data['query']['pages'][page_id]['revisions'][0]['*']
    return raw_wikitext

def snipQuestionContent(text):
    #snip everything between title and first UTC, including UTC

def checkQuestionLength(text):
    #if it's too long, throw it out

def formatProfile(title, anchor, text, template)
    #mush it all together
    
def getEditToken(api_url, user_agent):
    """
    Request a token for your edit
    """
    auth1 = OAuth1(unicode("b5d87cbe96174f9435689a666110159c"),
            client_secret=unicode(hostbot_settings.client_secret),
            resource_owner_key=unicode("ca1b222d687be9ac33cfb49676f5bfd2"),
            resource_owner_secret=unicode(hostbot_settings.resource_owner_secret))

    response = requests.get(
        api_url,
        params={
            'action': "query",
            'meta': "tokens",
            'type': "csrf",
            'format': "json"
            },
        headers={'User-Agent': user_agent},
        auth=auth1,        
        )
    doc = response.json() #why name this variable doc?
    try:
        token = doc['query']['tokens']['csrftoken'] 
    except:
        token = None
    return token
    
def publishProfile(api_url, page_path, edit_summ, text, token, user_agent):
    """
    Publishes one or more formatted messages on a wiki.
    """
    response = requests.post(
        api_url,
        data={
            'action': "edit",
            'title': page_path,
            'section': "new",
            'summary': edit_summ,
            'text': invite,
            'bot': 1,
            'token': token,
            'format': "json"
            },
        headers={'User-Agent': user_agent},
        auth=auth1
        )     
              
if __name__ == "__main__": 
    main()
        

# 	qraw = q.renderContents()
# 	qtitle = re.match("\=\=(.*?)\=\=", qraw)
# 	qlink = qtitle.group(1)
# 	qclean = re.sub("\=\=(.*?)\=\=", "", qraw)
# 	qstone = BeautifulStoneSoup(qclean, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
# 	report = wikitools.Page(wiki, report_title % page)
# 	report_text = report_template % (qstone, qlink)
# #	report_text = report_text.encode('utf-8')
# 	report.edit(report_text, section=0, summary="Automatic recent question update by [[User:HostBot|HostBot]]", bot=1)