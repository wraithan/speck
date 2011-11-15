#!/usr/bin/env python
import os
from ConfigParser import ConfigParser
from baker import command, run
from urllib2 import Request, urlopen
from urllib import urlencode, quote
from datetime import date, timedelta
from StringIO import StringIO
import csv
import json

config = ConfigParser()
config.read([os.path.expanduser('~/.speckrc')])

project_list = {
    '20%': '12925',
    'admin duties': '31350',
    'admind duties': '18791',
    'alfajor': '24306',
    'aquameta': '27634',
    'beehive': '10449',
    # 'client off-hours': '64638',
    'comb tests': '34450',
    'consulting': '14145',
    'datasphere': '54901',
    'errands': '69367',
    'exile': '38326',
    'holiday': '18884',
    'idle': '12927',
    'innovation': '76064',
    'internal': '10543',
    'metamodel': '16747',
    # 'off-hours': '27762',
    'open source': '27892',
    'sick time': '12924',
    'sponge': '16597',
    'time mgmt': '10445',
    'truthifier': '68117',
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

    token = token or config.get('freckle', 'token')
    req = Request(url='http://aquameta.letsfreckle.com/api/projects.xml',
                  headers={'X-FreckleToken': token})
    response = urlopen(req)
    tree = etree.fromstring(response.read())
    project_and_id = dict([(i[10].text.lower(),i[7].text) for i in tree])
    pprint(project_and_id)

@command
def report_last_week(token=None, billable='true'):
    last_week = get_week_days(date.today().year, int(date.today().strftime("%W"))-1)
    report(start=last_week[0], end=last_week[1], token=token, billable=billable)

@command
def weeks_since(start_year, start_month, token=None, billable='true'):
    current = date(int(start_year), int(start_month), 1)
    week = get_week_days(current.year, int(current.strftime("%W")))
    print "start of week, minutes of overtime"
    while week[1] < date.today():
        report(start=week[0], end=week[1], token=token, billable=billable)
        current += timedelta(days=7)
        week = get_week_days(current.year, int(current.strftime("%W")))

@command
def report_current_week(token=None, billable='true'):
    report(token=token, billable=billable)

@command
def report(start=None, end=None, token=None, billable='true'):
    token = token or config.get('freckle', 'token')
    current_week = get_week_days(date.today().year, int(date.today().strftime("%W")))
    start = start or current_week[0]
    end = end or current_week[1]
    user_id = config.get('freckle', 'user_id')

    projects = ','.join(project_list.values())
    projects = quote(projects)
    req = Request(url='http://aquameta.letsfreckle.com/api/entries.json?search[from]=%s&search[to]=%s&search[people]=%s&search[billable]=%s&search[projects]=%s' % (start, end, user_id, billable, projects),
                  headers={'X-FreckleToken': token})
    try:
        response = urlopen(req)
        report = json.loads(response.read())
        total_minutes =  sum(e['entry']['minutes'] for e in report)
        if total_minutes > 40*60:
            print "%s, %s" % (start, total_minutes - 40*60)
    except:
        import traceback
        import sys
        print "######################## Exception #############################"
        print '\n'.join(traceback.format_exception(*sys.exc_info()))
        print "################################################################"
        return 1

def get_week_days(year, week):
    d = date(year,1,1)
    if(d.weekday()>3):
        d = d+timedelta(7-d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days = (week-1)*7-1)
    return d + dlt,  d + dlt + timedelta(days=6)

run()
