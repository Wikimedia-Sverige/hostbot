# Copyright 2016 Sebastian Berlin

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

import json
import re
import logging

import requests

import hb_config

cache = {
    'pages': {},
    're_user_name': None,
    'local_user_namespace': None
}

class PageReaderError(Exception): pass

def read_json_value(page, name):
    """Read the value from a page formatted as JSON, given a name."""

    try:
        data_as_dict = read_json(page)
        return data_as_dict[name]
    except KeyError:
        raise PageReaderError("Couldn't read variable '{}' from page '{}'"
                              .format(name, page))

def read_json(page):
    """Read a page with JSON."""

    page_content = read_page(page)
    page_json = json.loads(page_content)
    return page_json

def read_page(raw_page):
    """Read the content of a page, given its title.

    The content will be cached the first time a page is read, allowing
    multiple calls to this function for the same page without sending
    multiple requests.
    """

    # Normalize page title for caching, in case the same page is
    # accessed using different title formats.
    page = normalize_title(raw_page)
    if page in cache["pages"]:
        # Read cached page, if available.
        page_content = cache["pages"][page]
    else:
        response = _send_api_request(
            {
                'action': "query",
                'titles': page,
                'format': "json",
                'prop' : "revisions",
                'rvprop': "content"
            }
        )
        response_pages = response["query"]["pages"]
        # Just look at the first page, since there should only be one.
        page_content = \
            response_pages[response_pages.keys()[0]]["revisions"][0]["*"]
        # Chache page content.
        cache["pages"][page] = page_content
    return page_content

def _send_api_request(parameters, url=None):
    """Send a GET request to the API and return the response."""

    if url is None:
        url = hb_config.apiurl
    response = requests.get(
        url,
        parameters,
        headers={'User-Agent': hb_config.oauth_user_agent},
    ).json()
    return response

def normalize_title(title):
    """Normalize a page title.

    If the title contains a colon, it is assumed that it is a
    namespace delimiter.
    """

    prefix, delimiter, suffix = title.partition(":")
    if suffix:
        namespace = prefix[0].upper() + prefix[1:]
        name = suffix
    else:
        name = prefix
        namespace = ''
    name = name[0].upper() + name[1:]
    capitalized_title = "{}{}{}".format(namespace, delimiter, name)
    normalized_title = capitalized_title.replace("_", " ")
    return normalized_title

def read_list_page(page):
    """Read a new line separated list from a page."""

    page_content = read_page(page)
    list_ = page_content.split("\n")
    return list_

def read_user_list_page(page):
    """Read a page with user links, as a list."""

    inviters = []
    page_list = read_list_page(page)
    for i, inviter_wikitext in enumerate(page_list):
        inviter_name = user_name_from_wikitext(inviter_wikitext)
        if inviter_name is None:
            logging.info(
                u"Ignoring item #{} on page '{}', '{}' is not a valid user link.".format(i, page, inviter_wikitext)
            )
        else:
            inviters.append(inviter_name)
    return inviters

def user_name_from_wikitext(wikitext):
    """
    Extract the user name from a wikitext string.

    E.g:
      [[User:FikarummetBot]] -> FikarummetBot
    To allow for signatures (~~~~), the following also works:
      [[User:FikarummetBot|FikarummetBot]] ([[User talk:FikarummetBot|talk]]) 09:12, 17 October 2016 (UTC) -> FikarummetBot

    Returns None if no valid user name was found.
    """

    if cache["re_user_name"] is None:
        _compile_re_user_name()
    match = cache["re_user_name"].match(wikitext)
    if match is None:
        return None
    else:
        return match.group(2)

def _compile_re_user_name():
    """Compile a regex for getting the user name from a wikitext string.

    Accepts the user namspace defined for the current wiki and the
    canonical 'User'.
    """

    cache["re_user_name"] = \
        re.compile(u"\[\[(User|{:s}):(.*?)(\]\]|\|)".format(
            get_local_user_namespace()
        ))

def get_local_user_namespace():
    """Get the user namespace name defined for the current wiki."""

    if cache["local_user_namespace"] is None:
        local_user_namespace = cache["local_user_namespace"]
    else:
        response = _send_api_request(
            {
                'action': "query",
                'format': "json",
                'meta': "siteinfo",
                'siprop': "namespaces"
            },
            'https://sv.wikipedia.org/w/api.php'
        )
        local_user_namespace = response["query"]["namespaces"]["2"]["*"]
        cache["local_user_namespace"] = local_user_namespace
    return local_user_namespace

def read_json_array(page):
    """Read a JSON array from a page."""

    data = read_json(page)
    if not isinstance(data, list):
        raise PageReaderError("Couldn't read data on page '{}' as array.".format(page))
    return data
