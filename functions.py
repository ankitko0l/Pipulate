import requests, datetime, json, time
from flask import session
import globs
from common import *

def walkdict(obj, key):
  stack = obj.items()
  while stack:
    k, v = stack.pop()
    if isinstance(v, dict):
      stack.extend(v.iteritems())
    else:
      if k == key:
        return v
  return None

def crawl(url):
  CellList = globs.sheet.range('C1:D2')
  vals = ['Title', 'Description', '?', '?']
  for i, val in enumerate(vals):
    CellList[i].value = val
  globs.sheet.update_cells(CellList)
  from urlparse import urlparse
  apex = urlparse(url).hostname.split(".")
  apex = ".".join(len(apex[-2]) < 4 and apex[-3:] or apex[-2:])
  import lxml.html
  ro = requests.get(url)
  doc = lxml.html.fromstring(ro.text)
  somelinks = doc.xpath('/html/body//a/@href')
  links = set()
  for alink in somelinks:
    print(urlparse(alink)[1][-len(apex):])
    if urlparse(alink)[1][-len(apex):] == apex:
      links.add(alink)
  links = list(links)
  y = len(links)
  linkslist = zip(links,['1']*y,['?']*y,['?']*y)
  InsertRows(globs.sheet, linkslist, 2)
  return "0"

def serps(keyword):
  times = 2
  api = "http://ajax.googleapis.com/ajax/services/search/web"
  returnme = []
  for start in [8*n for n in range(0,times)]:
    pdict = {'rsz':'large', 'v':'1.0', 'q': keyword, 'start':start}
    respobj = requests.get(api, params=pdict)
    returnme.append(respobj.json())
    time.sleep(1)
  return json.dumps(returnme)

def positions(keyword, serps=''):
  if not serps:
    def gserps(keyword):
      global serps
      return serps(keyword)
    serps = gserps(keyword)
  if serps:
    serps = json.loads(serps)
    easydict = {}
    serpos = 1
    for serpage in serps:
      serpage = serpage["responseData"]["results"]
      for result in serpage:
        easydict[serpos] = result['url']
        serpos += 1
    return json.dumps(easydict)
  else:
    return "Error"

def position(keyword, site, positions=''):
  if not positions:
    def gpositions(keyword):
      global positions
      return positions(keyword)
    positions = gpositions(keyword)
  if positions:
    urldict = json.loads(positions)
    for thepos, aurl in urldict.iteritems():
      if site in aurl:
        return thepos
    #return "> " % len(positions)

def topurl(site, positions=''):
  if positions:
    urldict = json.loads(positions)
    for thepos, aurl in urldict.iteritems():
      if site in aurl:
        return aurl

def response(url):
  if globs.hobj:
    return globs.hobj.status_code
  else:
    try:
      return requests.get(url).status_code
    except:
      return "Error"

def plusses(url):
  api = "https://clients6.google.com/rpc"
  jobj = '''{
    "method":"pos.plusones.get",
    "id":"p",
    "params":{
        "nolog":true,
        "id":"%s",
        "source":"widget",
        "userId":"@viewer",
        "groupId":"@self"
        },
    "jsonrpc":"2.0",
    "key":"p",
    "apiVersion":"v1"
  }''' % (url)
  respobj = requests.post(api, jobj)
  adict = respobj.json()
  return walkdict(adict, 'count')

def tweets(url):
  api = "http://urls.api.twitter.com/1/urls/count.json?url="
  respobj = requests.get(api + url)
  adict = respobj.json()
  return walkdict(adict, 'count')

def shares(url):
  respobj = requests.get('https://graph.facebook.com/' + url) 
  adict = respobj.json()
  return walkdict(adict, 'shares')

def likes(url): 
  respobj = requests.get('https://graph.facebook.com/' + url) 
  adict = respobj.json()
  return walkdict(adict, 'likes')
