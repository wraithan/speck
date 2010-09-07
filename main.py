#!/usr/bin/env python
import os
from ConfigParser import ConfigParser
from baker import command, run

config = ConfigParser()
config.read([os.path.expanduser('~/.speckrc')])

project_list = {
    '20%': '12925',
    'admind duties': '18791',
    'alfajor': '24306',
    'beehive': '10449',
    'beehvie': '17599',
    'consulting': '14145',
    'holiday': '18884',
    'idle': '12927',
    'internal': '10543',
    'metamodel': '16747',
    'sick time': '12924',
    'sponge': '16597',
    'time mgmt': '10445',
    'vacation time': '12926'
    }

@command(default=True,
         params={'time': 'in minutes or hours: 30 or 2h',
                 'description': 'Tags and description',
                 'when': 'YYYY-MM-DD defaults to today',
                 'project': 'Project name',
                 'user': 'Email account associated with your freckle account',
                 'token': 'API Token',}
         )
def add(time, description, when=None,
        project=None, user=None,
        token=None):
    """Adds the given parameters to freckle."""

    from urllib2 import Request, urlopen
    from datetime import date

    when = when or str(date.today())
    project = project or config.get('freckle', 'project')
    user = user or config.get('freckle', 'user')
    token = token or config.get('freckle', 'token')

    project_id = project_list[project.lower()]

    entries_string = """<entry>
  <minutes>%s</minutes>
  <description>%s</description>
  <date>%s</date>
  <project-id>%s</project-id>
  <user>%s</user>
</entry>""" % (time, description, when, project_id, user)

    print(entries_string)

    req = Request(url='http://aquameta.letsfreckle.com/api/entries.xml',
                  data=entries_string,
                  headers={'Content-type': 'text/xml',
                           'X-FreckleToken': token})
    try:
        response = urlopen(req)
        print response.code, response.msg
    except:    
        import traceback
        import sys
        print "######################## Exception #############################"
        print '\n'.join(traceback.format_exception(*sys.exc_info()))
        print "################################################################"
        return 1

    return 0

@command
def list(token=None):
    from lxml import etree
    from pprint import pprint
    from urllib2 import Request, urlopen

    token = token or config.get('freckle', 'token')
    req = Request(url='http://aquameta.letsfreckle.com/api/projects.xml',
                  headers={'X-FreckleToken': token})
    response = urlopen(req)
    tree = etree.fromstring(response.read())
    project_and_id = dict([(i[7].text.lower(),i[5].text) for i in tree])
    pprint(project_and_id)

run()
