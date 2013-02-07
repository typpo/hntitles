#!/usr/bin/env python

import json
import redis
import urllib
import datetime
import time

FRONTPAGE = 'http://hndroidapi.appspot.com/news/format/json/page/?appid=&callback='
NEWEST = 'http://hndroidapi.appspot.com/newest/format/json/page/?appid=&callback='
REDIS_PREFIX = 'hntitles:'

def fetch(url):
  now = datetime.datetime.now()

  try:
    json_obj = json.load(urllib.urlopen(url))
  except:
    print 'failed'
    return

  ids_and_titles = [(item['item_id'], item['title'].encode('utf-8')) \
      for item in json_obj['items'] if 'item_id' in item]

  r = redis.StrictRedis(host='localhost', port=6379, db=2)
  for id, title  in ids_and_titles:
    key = REDIS_PREFIX + id
    existing = r.get(key)
    if existing and existing != title:
      outstr = '%s: TITLE CHANGED (%s): "%s" -> "%s"\n' % \
          (now.strftime("%Y-%m-%d %H:%M"), id, existing, title)
      f = open('output/log2', 'a')
      f.write(outstr)
      f.close()
      print outstr
    r.set(key, title)

while True:
  print 'checking...'
  fetch(NEWEST)
  fetch(FRONTPAGE)
  time.sleep(60*5)
