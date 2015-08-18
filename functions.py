#  _   _                 _____                 _   _                 
# | | | |___  ___ _ __  |  ___|   _ _ __   ___| |_(_) ___  _ __  ___ 
# | | | / __|/ _ \ '__| | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |_| \__ \  __/ |    |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
#  \___/|___/\___|_|    |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#                                                                    
# Welcome to User Functions, a file that lets you extend Pipulate's capability.
# Let's meet some libraries and modules we make available to every function.

import os, requests, datetime, json, time, urlparse, re   #All standard system libraries
from flask import session                                 #For if user function needs session info
import globs                                              #All objects treated as global variables (but somehow less despised)
from common import *                                      #For if user function neeeds framework functions

#  _   _      _                   _____                 _   _                 
# | | | | ___| |_ __   ___ _ __  |  ___|   _ _ __   ___| |_(_) ___  _ __  ___ 
# | |_| |/ _ \ | '_ \ / _ \ '__| | |_ | | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# |  _  |  __/ | |_) |  __/ |    |  _|| |_| | | | | (__| |_| | (_) | | | \__ \
# |_| |_|\___|_| .__/ \___|_|    |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#              |_|                                                            
# Take a look at some support-functions you can call from your own functions.
# The jobs done by these are so common, they get used almost everywhere.

def walkdict(obj, key):
  """Take a JSON object and key and return the first matched value from the object."""
  stack = obj.items()
  while stack:
    k, v = stack.pop()
    if isinstance(v, dict):
      stack.extend(v.iteritems())
    else:
      if k == key:
        return v
  return None

def regex(text, pattern):
  """Take text and a Regular Expression using a group named scrape, and return match."""
  if text[:4].lower() == 'http':
    text = requests.get(text).text
  match = re.search(pattern, text, re.S | re.I)
  if match:
    if "scrape" in match.groupdict().keys():
      return match.group("scrape")
  else:
    return None

def scraper(text, anxpath):
  """Take html and an XPATH, and return match."""
  if text[:4].lower() == 'http':
    text = requests.get(text).text
  import lxml.html
  searchme = lxml.html.fromstring(text)
  match = searchme.xpath(anxpath)
  if match:
    return match[0]
  else:
    return None

def xml(url):
  text = requests.get(url).text
  import lxml.html
  xobj = lxml.html.document_fromstring(text)
  from lxml import etree
  return (etree.tostring(xobj, pretty_print=True))

def jsonapi(endpoint, url, jkey):
  """Take a JSON API endpoint, a URL as a parameter and key name to return value pair."""
  thecall = endpoint + url
  respobj = requests.get(thecall, timeout=5)
  adict = respobj.json()
  return walkdict(adict, jkey)

#  ____                                   ____        __ _       _ _   _                 
# / ___|  ___ _ __ __ _ _ __   ___ _ __  |  _ \  ___ / _(_)_ __ (_) |_(_) ___  _ __  ___ 
# \___ \ / __| '__/ _` | '_ \ / _ \ '__| | | | |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \/ __|
#  ___) | (__| | | (_| | |_) |  __/ |    | |_| |  __/  _| | | | | | |_| | (_) | | | \__ \
# |____/ \___|_|  \__,_| .__/ \___|_|    |____/ \___|_| |_|_| |_|_|\__|_|\___/|_| |_|___/
#                      |_|                                                               
# Many times, you don't even need to write a function when a scraper will do.
# If you did something nifty in the Scrapers tab, just make a new entry here.

def scrapes():
  """Define the functions available and modifiable from the Scrapers tab."""
  s = []
  s.append(['title',       'xpath', "//title/text()"])
  s.append(['description', 'xpath', "//meta[translate(@name, 'ABCDEFGHJIKLMNOPQRSTUVWXYZ', 'abcdefghjiklmnopqrstuvwxyz')='description']/@content"])
  s.append(['canonical',   'xpath', "/html/head/link[@rel = 'canonical']/@href"])
  s.append(['mobile',      'xpath', "/html/head/link[@media = 'only screen and (max-width: 640px)']/@href"])
  s.append(['tweettotal',  'xpath', "//span[.='Tweets']/following-sibling::span/text()"])
  s.append(['following',   'xpath', "//span[.='Following']/following-sibling::span/text()"])
  s.append(['followers',   'xpath', "//span[.='Followers']/following-sibling::span/text()"])
  s.append(['views',       'xpath', "//div[@class='watch-view-count']/text()"])
  s.append(['thumbsup',    'xpath', "//button[@id='watch-like']/span/text()"])
  s.append(['thumbsdown',  'xpath', "//button[@id='watch-dislike']/span/text()"])
  s.append(['subscribers', 'regex', r"subscriber-count.*?>(?P<scrape>[0-9,]+?)<"])
  s.append(['ga',          'regex', r"(?:\'|\")(?P<scrape>UA-.*?)(?:\'|\")"])
  return s

#  ____                 ___                     _                
# |  _ \ _____      __ |_ _|_ __  ___  ___ _ __| |_ ___ _ __ ___ 
# | |_) / _ \ \ /\ / /  | || '_ \/ __|/ _ \ '__| __/ _ \ '__/ __|
# |  _ < (_) \ V  V /   | || | | \__ \  __/ |  | ||  __/ |  \__ \
# |_| \_\___/ \_/\_/   |___|_| |_|___/\___|_|   \__\___|_|  |___/
#                                                                
# Not all functions you encounter here will have the ability to add new rows.
# They require special init functions to set up the column names beforehand.

def crawl(source):
  """Grab HTML from a link, parse links and add a row per link to spreadsheet."""
  fcols = ['target', 'depth', 'getlinks']
  therange = 'B1:%s2' % globs.letter[len(fcols)+1]
  CellList = globs.sheet.range(therange)
  vals = fcols + [] + [] + []
  for i, val in enumerate(vals): # First, we add the columns we know we're going to need.
    CellList[i].value = val
  globs.sheet.update_cells(CellList)
  links = setolinks(source)
  y = len(links)
  linkslist = zip([source]*y, links, ['0']*y, ['?']*y)
  InsertRows(globs.sheet, linkslist, 2)
  return ""

def setolinks(source):
  import lxml.html
  apexdom = apex(source)
  ro = requests.get(source, timeout=5, verify=False)
  doc = lxml.html.fromstring(ro.text)
  doc.make_links_absolute(source)
  somelinks = doc.xpath('/html/body//a/@href')
  links = set()
  for alink in somelinks:
    if urlparse.urlparse(alink)[1][-len(apexdom):] == apexdom:
      if alink != source:
        links.add(alink)
  links = list(links)
  return links

def getlinks(target, depth='0'):
  links = setolinks(target)
  y = len(links)
  globs.numrows = len(globs.sheet.col_values(1))
  if depth:
    depth = int(depth) + 1
  linkslist = zip([target]*y, links, [depth]*y)
  InsertRows(globs.sheet, linkslist, globs.numrows)
  return "done"

def crawl2(url):
  """Grab HTML from a URL, parse links and add a row per link to spreadsheet."""
  fcols = ['Depth', 'Title', 'Description']
  therange = 'B1:%s2' % globs.letter[len(fcols)+1]
  CellList = globs.sheet.range(therange)
  vals = fcols + ['0'] + ['?']*(len(fcols)-1)
  for i, val in enumerate(vals):
    CellList[i].value = val
  globs.sheet.update_cells(CellList)
  apexdom = apex(url)
  import lxml.html
  ro = requests.get(url, timeout=5)
  doc = lxml.html.fromstring(ro.text)
  doc.make_links_absolute(url)
  somelinks = doc.xpath('/html/body//a/@href')
  links = set()
  for alink in somelinks:
    if urlparse.urlparse(alink)[1][-len(apexdom):] == apexdom:
      links.add(alink)
  links = list(links)
  y = len(links)
  q = ['']*y
  linkslist = zip(links,['1']*y,q,q,q)
  InsertRows(globs.sheet, linkslist, 2)
  return "0"

def crawlinit(gsp):
  """Do the spreadsheet setup requried by crawl function."""
  pass

#   ___                         _ ____   ___  _   _      _    ____ ___     
#  / _ \ _ __   ___ _ __       | / ___| / _ \| \ | |    / \  |  _ \_ _|___ 
# | | | | '_ \ / _ \ '_ \   _  | \___ \| | | |  \| |   / _ \ | |_) | |/ __|
# | |_| | |_) |  __/ | | | | |_| |___) | |_| | |\  |  / ___ \|  __/| |\__ \
#  \___/| .__/ \___|_| |_|  \___/|____/ \___/|_| \_| /_/   \_\_|  |___|___/
#       |_|                                                                
# All these have high volume, publically available (no login) endpoints
# meaning they're almost as simple as the Scraper functions.

def tweets(url):
  """Return the number of times a given URL had been tweeted."""
  endpoint = "http://urls.api.twitter.com/1/urls/count.json?url="
  return jsonapi(endpoint, url, 'count')

def stumbles(url):
  """Return the number of times a given URL was viewed in StumbleUpon."""
  endpoint = 'http://www.stumbleupon.com/services/1.01/badge.getinfo?url='
  return jsonapi(endpoint, url, 'views')

def pins(url):
  """Return the number of times a given URL has been pinned in Pinterest."""
  endpoint = 'http://api.pinterest.com/v1/urls/count.json?url='
  return jsonapi(endpoint, url, 'count')

#      _       _     _   ____  _          __  __   _   _               
#     / \   __| | __| | / ___|| |_ _   _ / _|/ _| | | | | ___ _ __ ___ 
#    / _ \ / _` |/ _` | \___ \| __| | | | |_| |_  | |_| |/ _ \ '__/ _ \
#   / ___ \ (_| | (_| |  ___) | |_| |_| |  _|  _| |  _  |  __/ | |  __/
#  /_/   \_\__,_|\__,_| |____/ \__|\__,_|_| |_|   |_| |_|\___|_|  \___|
#                                                                      
# And now what you've all been waiting for! If you write a Python function that
# just works stand-alone elsewhere, simply paste it here to extend Pipulate.

def d2(keyword):
  if 'keyword' in globs.row1:
    letter = globs.letter[globs.row1.index('keyword') + 1]
    chunks = ['%s%s:%s%s' % (letter, chunk, letter, chunk+49) for chunk in range(2, globs.numrows, 50)]
  else:
    return "You must have a column named keyword."
  for chunk in chunks:
    out(chunk)
    CellList = globs.sheet.range(chunk)
  return "Did it!"
  # raise StopIteration()

def difficulty(keyword):
  if 'semrush' in globs.config:
    apikey = globs.config['semrush']
    try:
      call = 'http://api.semrush.com/?type=phrase_kdi&export_columns=Kd&phrase=%s&key=%s&database=us' % (keyword, apikey)
      respobj = requests.get(call, timeout=5)
      rtext = respobj.text
    except:
      return "Double-check your semrush entry in the Config tab."
    try:
      return rtext.splitlines()[1]
    except:
      return "N/A"
  else:
    return "In the Config tab, put semrush under name and the api key under value to proceed."

def twitter_followers(twitter_name):
  api = 'https://twitter.com/'
  un = twitter_name
  if un.lower().strip() in ('na', 'n/a'):
    return un
  if un[0] == '@':
    un = un[1:]
  url = "%s%s" % (api, un)
  xpath = "//span[.='Followers']/following-sibling::span/text()"
  sendback = scraper(url, xpath)
  if ',' in sendback:
    sendback = sendback.replace(',', '')
  return sendback

def instagram_followers(instagram_name):
  api = 'https://instagram.com/'
  un = instagram_name
  if un.lower().strip() in ('na', 'n/a'):
    return un
  if un[0] == '@':
    un = un[1:]
  url = "%s%s" % (api, un)
  #pattern = 'followed_by":{"count":(?P<scrape>\d+)}'
  pattern = r'(followed_by":{"count":)(?P<scrape>\d+)}'
  sendback = regex(url, pattern)
  return sendback

def serps(keyword):
  """Return non-customized JSON search results for keyword from Google."""
  times = 2
  api = "http://ajax.googleapis.com/ajax/services/search/web"
  returnme = []
  for start in [8*n for n in range(0,times)]:
    pdict = {'rsz':'large', 'v':'1.0', 'q': keyword, 'start':start}
    respobj = requests.get(api, params=pdict, timeout=5)
    returnme.append(respobj.json())
    time.sleep(1)
  return json.dumps(returnme)

def positions(keyword, serps=''):
  """Return a position/url paired JSON dict of all results for keyword."""
  if not serps:
    def gserps(keyword):
      global serps
      return serps(keyword)
    serps = gserps(keyword)
  elif serps:
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
  """Return the position a provided site is in for a given keyword."""
  if not positions:
    def gpositions(keyword):
      global positions
      return positions(keyword)
    positions = gpositions(keyword)
  elif positions:
    urldict = json.loads(positions)
    for thepos, aurl in urldict.iteritems():
      if site in aurl:
        return thepos
    #return "> " % len(positions)

def topurl(site, positions=''):
  """Return the top performing URL for a site given a positions object."""
  if positions:
    urldict = json.loads(positions)
    for thepos, aurl in urldict.iteritems():
      if site in aurl:
        return aurl

def response(url):
  """Return a numeric http response code for given URL."""
  if globs.hobj:
    return globs.hobj.status_code
  else:
    try:
      return requests.get(url, timeout=5).status_code
    except:
      return "Error"

def plusses(url):
  """Return the number of times the given URL was plussed in Google+"""
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

def fb(url):
  """Return Facebook likes, shares, clicks and comment counts for a given URL."""
  thecall = "https://graph.facebook.com/fql?q=SELECT+like_count,total_count,share_count,click_count,comment_count+FROM+link_stat+WHERE+url=%22"+url+"%22"
  try:
    respobj = requests.get(thecall, timeout=5)
    adict = respobj.json()
    return json.dumps(adict['data'][0])
  except:
    return None

def shares(url, fb=''):
  """Return the number of times a given URL was shared in Facebook."""
  if not fb:
    def gfb(url):
      global fb
      return fb(url)
    fb = json.loads(gfb(url))
  else:
    fb = json.loads(fb)
  return walkdict(fb, "share_count")

def likes(url, fb=''):
  """Return the number of times a given URL was liked in Facebook."""
  if not fb:
    def gfb(url):
      global fb
      return fb(url)
    try:
      fb = json.loads(gfb(url))
    except:
      return "Error"
  else:
    try:
      fb = json.loads(fb)
    except:
      return "Error"
  return walkdict(fb, "like_count")

def comments(url, fb=''):
  """Return the number of times a URL was commented on in Facebook."""
  if not fb:
    def gfb(url):
      global fb
      return fb(url)
    fb = json.loads(gfb(url))
  else:
    fb = json.loads(fb)
  return walkdict(fb, "comment_count")

def linkedin(url):
  """Return the number of times a given URL was shared in LinkedIn."""
  api = "https://www.linkedin.com/countserv/count/share?url=" + url
  respobj = requests.get(api, timeout=5)
  rtext = respobj.text
  spattern = '"count":(?P<scrape>[0-9,]+?),'
  return regex(rtext, spattern)

def pagerank(url):
  """Return the PageRank number that would show for this URL in Google Toolbar."""
  import urllib
  def CheckHash(HashInt):
    HashStr = "%u" % (HashInt)
    Flag = 0
    CheckByte = 0
    i = len(HashStr) - 1
    while i >= 0:
      Byte = int(HashStr[i])
      if 1 == (Flag % 2):
        Byte *= 2;
        Byte = Byte / 10 + Byte % 10
      CheckByte += Byte
      Flag += 1
      i -= 1
    CheckByte %= 10
    if 0 != CheckByte:
      CheckByte = 10 - CheckByte
      if 1 == Flag % 2:
        if 1 == CheckByte % 2:
          CheckByte += 9
        CheckByte >>= 1
    return '7' + str(CheckByte) + HashStr
  def HashURL(Str):
    def  IntStr(String, Integer, Factor):
      for i in range(len(String)) :
        Integer *= Factor
        Integer &= 0xFFFFFFFF
        Integer += ord(String[i])
      return Integer
    C1 = IntStr(Str, 0x1505, 0x21)
    C2 = IntStr(Str, 0, 0x1003F)
    C1 >>= 2
    C1 = ((C1 >> 4) & 0x3FFFFC0) | (C1 & 0x3F)
    C1 = ((C1 >> 4) & 0x3FFC00) | (C1 & 0x3FF)
    C1 = ((C1 >> 4) & 0x3C000) | (C1 & 0x3FFF)
    T1 = (C1 & 0x3C0) << 4
    T1 |= C1 & 0x3C
    T1 = (T1 << 2) | (C2 & 0xF0F)
    T2 = (C1 & 0xFFFFC000) << 4
    T2 |= C1 & 0x3C00
    T2 = (T2 << 0xA) | (C2 & 0xF0F0000)
    return (T1 | T2)
  hsh = CheckHash(HashURL(url))
  gurl = 'http://toolbarqueries.google.com/tbr?client=navclient-auto&features=Rank:&q=info:%s&ch=%s' % (urllib.quote(url), hsh)
  f = urllib.urlopen(gurl)
  st = f.read()
  st = st.lstrip().rstrip()
  st = st[9:]
  try:
    st = int(st)
  except:
    st = 0
  return st

def mcanonical(mobile):
  """Return the canonical tag found in the URL referred to by under the mobile column."""
  try:
    ro = requests.get(mobile, timeout=5)
    text = ro.text
    xpth = "/html/head/link[@rel = 'canonical']/@href"
    revcon = scraper(text, xpth)
    return revcon
  except:
    return None

def mobilicious(url, mobile, mcanonical):
  """Compare the URL of desktop version with the mobile canonical and return Pass if the same."""
  if mobile:
    if url == mcanonical:
      return "Pass"
    else:
      return "Fail"
  else:
    return "Fail"

def sheetinitializer(sheet1key):
  """ For any given menu-selection, return lists to become row 1 and 2."""
  sinit = {}
  sinit['crawl'] = (['source', 'crawl'], [globs.PIPURL, '?'])
  return sinit[sheet1key]
