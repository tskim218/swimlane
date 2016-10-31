#!/usr/bin/python

from urllib import urlopen
from Parse import *
import json, getopt

##########################################
## Use for enum
##########################################
class ENUM(object): pass
class Equal(ENUM) : pass  ## item match
class Hasit(ENUM) : pass  ## item contain
class FindA(ENUM) : pass  ## find all items

##########################################
## Parent for lookup data
##########################################

class LookUp(object):
  def __init__(self, server, resourceid):
    self.server     = server
    self.resourceid = resourceid
    self.entryFound = False
    self.result     = []
    self.enum       = Equal
    self.enumExtra  = None

  def __del__ (self):
    del self.result[:]

  def getResponse(self, ip):
    url = "%s://%s/%s/%s   " % ("http",self.server,self.resourceid,ip)
    return urlopen(url).read()

  def getJsonFormat(self, ip):
    return json.loads(self.getResponse(ip))

  ## recursion search for finding all info
  def recursion(self, dat, item):
    if (isinstance(dat, list)):
      self.getEntities(dat, item)
    elif (isinstance(dat, basestring)):
      pass
    elif (isinstance(dat, dict)):
      self.getEntities(dat, item)

  ## start search for finding all info
  def getEntities(self, info, item):
    if (self.entryFound == True):
      return

    if (isinstance(info, dict)):
      sorted_keys = info.keys()
      sorted_keys.sort()

      for val in sorted_keys:
        VAL = val.upper()
        if ( self.enum == Equal and VAL == item ):
          self.entryFound = True
          self.result.append(info[val])
          break
        elif (self.enum == Hasit and 
              isinstance(val, basestring) and VAL == "OBJECTCLASSNAME" and
              isinstance(info[val], basestring) and info[val].upper().find(item) >= 0 ):
	  if (self.enumExtra != FindA):
            self.entryFound = True
          self.result.append(info)
          break
	elif (self.enum == FindA and VAL == item):
	  self.result.append(info[val])

	self.recursion(info[val], item)

    elif(isinstance(info, list)):
      for val in info:
	self.recursion(val, item)

  ## init for search rules
  def getItem(self, ip, item, search, dat=None, enumextra=None):
    del self.result[:]
    self.enum       = search
    self.enumExtra  = enumextra
    self.entryFound = False

    if (self.enum == Equal or self.enum == Hasit):
      info = self.getJsonFormat(ip)
    else:  ## self.enum == FindA
      info = dat

    self.getEntities(info, item)

    if (self.entryFound == True or len(self.result) > 0):
      return self.result
    else:
      return None

################################
## GeoIP Lookup
################################
class GeoIP(LookUp):
  def __init__ (self, config, iplist):
    self.confDict    = ConfigParse(config).getConfigList()
    self.server      = self.confDict['server'][0]
    self.resourceid  = self.confDict['resourceid'][0]
    self.ipadrlist   = iplist
    self.geolistdict = {}
    super(GeoIP, self).__init__(self.server, self.resourceid)

  def queryGeoIPInfo(self):
    for ip in self.ipadrlist:
      dict = {}
      for item in self.confDict['info']:
        ITEM = item.upper()
        content = super(GeoIP,self).getItem(ip, ITEM, Equal)

	try:
          dict[ITEM] = content[0]
        except KeyError:
          dict[ITEM] = ""

      self.geolistdict[ip] = dict

  def getGeoIPDB(self):
    return self.geolistdict

################################
## RDAP Lookup
################################
class RDAP(LookUp):
  def __init__ (self, config, iplist):
    self.confDict   = ConfigParse(config).getConfigList()
    self.server     = self.confDict['server'][0]
    self.resourceid = self.confDict['resourceid'][0]
    self.ipadrlist  = iplist
    self.ips        = {}
    self.contacts   = {}
    self.vardresult = []
    self.vardbool   = False
    super(RDAP, self).__init__(self.server, self.resourceid)

  def queryRDAPInfo(self):
    for ip in self.ipadrlist:
      for objCN in self.confDict['objectClassName']:
	try:
          getattr(self, objCN)(ip,self.confDict[objCN][0])
        except KeyError:
	  print 'Configuration file Error'
	  sys.exit(2)

  def getRDAPIPDB(self):
    return self.ips

  def getRDAPContactsDB(self):
    return self.contacts

  ## Get IP network contents only 
  def getIPContent(self, ip, objcn):
    ipDict = {}
    ipContent = super(RDAP,self).getItem(ip, objcn.upper(), Hasit)[0]

    ipDict = self.getIPAndContact(ipContent, 'ip')

#    for k in self.confDict['ipfielfield']:
#      if (ipDict.has_key(k)):
#        print k, ipDict[k]

    self.ips[ip] = ipDict

  ## Get Contact contents of the IP
  def getContactContent(self, ip, objcn):
    contactContent = super(RDAP,self).getItem(ip, objcn.upper(),
		                              Hasit, enumextra=FindA)

    ## initialize dict to store
    n = len(contactContent)
    cList = [{} for _ in range(n)]

    for ind in range (n):
      contact = contactContent[ind]
      cList[ind] = self.getIPAndContact(contact, 'entity')
      contactDict = cList[ind]

      ## get address, email, telephone, name (fn)
      try:
        contactDict.update(self.getVcardArray(contactDict['VCARDARRAY']))
        del contactDict['VCARDARRAY']
      except KeyError:
        pass

      try:
        contactDict['ROLES'] = self.getRoles(contactDict['ROLES'])
      except KeyError:
        contactDict['ROLES'] = ""

#    for c in cList:
#       for e in self.confDict['entityfield']:
#         if (c.has_key(e)):
#           print e, c[e]
#       print "========"

    self.contacts[ip] = cList

  def getEvents(self, eventContent):
    eventsDict = {}
    for event in eventContent:
      eventkeys = event.keys()
      eventkeys.sort()
      i = 0
      key = ""
      val = ""
      for k in eventkeys:
        if (i == 0):
          key = event[k]
          key = key.replace(' ','_')
        else:  ## val
          val = event[k]
        i += 1

	eventsDict[key.upper()] = val

    return eventsDict

  def getIPAndContact(self, content, title):
    Dict = {}
    for confval in self.confDict[title]:
      CONFVAL = confval.upper()
      for contkey in content.keys():
	CONTKEY = contkey.upper()
	if (isinstance(contkey,basestring) and CONTKEY == CONFVAL):
	  if (CONTKEY == "EVENTS"):
            Dict.update(self.getEvents(content[contkey]))
	  else:
	    Dict[CONFVAL] = content[contkey] 
	  del content[contkey]
	  break

    return Dict

  def getVcardArray(self, arraylist):
    arrayDict = {}

    for item in self.confDict['vcardarray']:
      ##print "item is -> ", item
      self.vardbool   = False
      del self.vardresult[:]
      self.getVcardItem(arraylist, item)
      if (self.vardbool == True):
        if (item == 'adr'):
	  adrLabel = self.confDict[item][0]
	  for vr in self.vardresult:
	    if (isinstance(vr,dict) and vr.has_key(adrLabel)):
	      arrayDict['ADDRESS'.upper()] = vr[adrLabel]
	      ##print item, vr[adrLabel]
        else:
	  try:
	    if (item == 'fn'):
	      arrayDict['NAME'] = self.vardresult[3]
            else:
	      arrayDict[item.upper()] = self.vardresult[3]
	  except IndexError:
	    arrayDict[item.upper()] = None

    return arrayDict

  def getVcardItem(self, alist, item):
    if (self.vardbool == True):
      return 

    if item in alist:
      #print alist
      self.vardbool = True
      self.vardresult = alist
    else:
      for l in alist:
        if (isinstance(l,list)):
          self.getVcardItem(l, item)
	  if (self.vardbool == True):
	    return

  def getRoles(self, arraylist):
    roleStr = ""
    szAry = len(arraylist)
    for i in range(szAry):
      if (i == szAry - 1):
	roleStr += arraylist[i]
      else:
        roleStr += arraylist[i] + ","

    return roleStr

########################################
## LookUp Factory
#######################################
class LookUpFactory:
  def __init__ (self, objName):
    self.obj = objName

  def initLookUp(self, config, iplist):
    if (self.obj == "RDAP"):
      return RDAP(config, iplist)
    elif (self.obj == "GeoIP"):
      return GeoIP(config, iplist)
