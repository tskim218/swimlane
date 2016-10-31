#!/usr/bin/python

import sys,os,string
import json
from urllib import urlopen, quote

def print_response(data, indent):
  if (isinstance(data, dict)):
    print " " * indent + "{"
    sorted_keys = data.keys()
    sorted_keys.sort()
    for k in sorted_keys:
      if (isinstance(data[k], list)):
        print " " * indent + '"'+ k + '"'+ ": ["
        print_response(data[k], indent+2)
        #print "1-------"
      elif (isinstance(data[k], basestring)):
        #print "2-", k, ": ", data[k]
        print " " * indent + '"' + k + '"'+ ": " + '"'+data[k].strip() +'"'
        #del data[k]
      elif (isinstance(data[k], dict)):
        print_response(data[k], indent+2)
    print " " * indent + "},"
  elif(isinstance(data, list)):
    for d in data:
      if (isinstance(d, dict)):
        #print "3- "
        print_response(d, indent+2)
        #print "2-------"
      elif(isinstance(d, basestring)):
        #print "4 - "
        print " " * indent + '"'+ d.strip() + '"'
        #data.remove(d)
      elif(isinstance(d, list)):
        print " " * indent, "["
        print_response(d, indent+2)

    print " " * indent + "]"
    ##sys.exit(1)

#country = urlopen("https://rdap.arin.net/bootstrap/").read()
#country = urlopen("http://rdap.arin.net/registry/domain/google.com").read()
#country = urlopen("http://rdap.arin.net/registry/ip/75.166.15.202").read()
country = urlopen("http://rdap.apnic.net/ip/75.166.15.202").read()
#country = urlopen("http://rdap.apnic.net/ip/173.194.67.99").read()
json_data = json.loads(country)

#print json.dumps(json_data, sort_keys=True, indent=2, separators=(',', ': '))
print print_response(json_data, 0)
