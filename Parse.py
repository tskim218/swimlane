#!/usr/bin/python

import re
import sys

######################################
## Parent Parse 
#####################################

class Parse(object):
  def __init__ (self, inoutfile):
    self.inoutfile = inoutfile

  ## get read file descriptor
  def getInFilePtr (self):
    try:
      inf = open(self.inoutfile, 'r')
    except:
      print "can't open input file" + self.inoutfile
      sys.exit(2)

    return inf

  ## get write file descriptor
  def getOutFilePtr (self):
    try:
      outf = open(self.inoutfile, 'w')
    except:
      print "can't open output file" + self.inoutfile
      return None

    return outf

######################################
## Parse for configuration files
######################################

class ConfigParse(Parse):
  def __init__(self, cfile):
    self.confFile   = cfile
    self.configDict = {}
    super(ConfigParse,self).__init__(self.confFile)

  def getConfigList(self):
    inf = super(ConfigParse,self).getInFilePtr()

    for line in inf.readlines():
      if (line[0] == '#'):
        continue

      tok = line.strip().split('=')
      valList = tok[1].split(',')
      self.configDict[tok[0]] = valList

    inf.close()

    return self.configDict

##########################################################
## Parse for IP address only from non-formatted text file
##########################################################

class IPExtractor(Parse):
  def __init__ (self, inputfile):
    self.inFile  = inputfile
    self.ipList  = []
    self.regex   = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    self.regex  += '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
    self.pattern = re.compile(self.regex)
    super(IPExtractor,self).__init__(self.inFile)

  def getIPs (self):
    self.extractIPs()
    return self.ipList

  def extractIPs (self):
    inf = super(IPExtractor,self).getInFilePtr()

    line = inf.readline()
    while line:
      ips = list(set(self.pattern.findall(line.strip())))
      self.ipList = list(set(self.ipList + ips))

      line = inf.readline()

    inf.close()

###############################################################
## Parse for user input query (generic languages defined by me)
###############################################################

class userQueryParse(Parse):
  def __init__ (self, query, userqcfg, geocfg, rdapcfg, iplist):
    self.query       = query
    self.userqcfg    = userqcfg  ## UserQuery.cfg
    self.geocfg      = geocfg    ## GeoIP.cfg
    self.rdapcfg     = rdapcfg   ## RDAP.cfg
    self.iplist      = iplist
    self.nonullsql   = []
    self.geoquery    = []
    self.rdapipquery = []
    self.rdapcquery  = []
    self.usripquery  = []
    self.outputquery = ""

  def userAns (self):
    anstok = self.query.split(';')

    if anstok[-1].strip().upper() == "END" or len(anstok[-1].strip()) == 0:
      del anstok[-1]

    status = self.chkQuery(anstok)
    if status == False :
      return None,None,None,None,self.outputquery
    else:
      return list(set(self.geoquery)),list(set(self.rdapipquery)),\
	     list(set(self.rdapcquery)),list(set(self.usripquery)),\
	     self.outputquery

  def chkQuery (self, anstok):
    for atok in anstok:
      itok = atok.strip().split(' ')

      ## wrong format ex: "select field" or "from ip"
      if (len(itok) != 2):
        print 'Error> syntax error, should 2 like "select field": ', itok
        return False

      sqlcmd = itok[0].strip().upper()
      ## wrong sql, see UserQuery.cfg
      if sqlcmd not in self.userqcfg['sql']:
        print "Error> syntax error, wrong sql: ", itok[0].strip()
        print "valid sql are: ",
        for s in self.userqcfg['sql']:
          print s,
        print
        return False

      ## exame each field in SELECT
      if sqlcmd == 'SELECT' and itok[1].strip() == '*':
	self.nonullsql.append(sqlcmd)
        self.geoquery.append('*')
	self.rdapipquery.append('*')
	self.rdapcquery.append('*')

      elif sqlcmd == 'SELECT' and itok[1].strip() != '*':
	self.nonullsql.append(sqlcmd)
        fieldtok = itok[1].split(',')
        for field in fieldtok:
	  dotftok = field.split('.')

 	  ## wrong field format
          if len(dotftok) != 2:
	    print "Error> syntax error, wrong field format: ", field
	    return False
	  ## invalid reference db
	  if dotftok[0].upper() != 'G' and dotftok[0].upper() != 'RI' and \
	     dotftok[0].upper() != 'RE':
	    print "Error> invlid db, should be 'g or G' or 'ri or RI' or 're or RE': ", dotftok[0]
	    return False
	  ## invalid Geo IP field 
          if dotftok[0].upper() == 'G' and dotftok[1].upper() not in self.geocfg['field']:
	    ## exception
	    if (dotftok[1] == '*') :
	      self.geoquery.append('*')
	    else:  
	      print "Error> invalid GeoIP field name: ", dotftok[1]
              print "valid GeoIP fields are : ", self.geocfg['field']
	      return False
	  ## invalid RDAP IP field
          if dotftok[0].upper() == 'RI' and dotftok[1].upper() not in self.rdapcfg['ipfield']:
	    ## exception
	    if (dotftok[1] == '*') :
	      self.rdapipquery.append('*')
	    else:
	      print "Error> invalid RDAP IP field name: ", dotftok[1]
              print "valid RDAP IP fields are : ", self.rdapcfg['ipfield']
	      return False
	  ## invalid RDAP Contact(entity) field
          if dotftok[0].upper() == 'RE' and dotftok[1].upper() not in self.rdapcfg['entityfield']:
	    ## exception
	    if (dotftok[1] == '*') :
	      self.rdapcquery.append('*')
	    else:
	      print "Error> invalid RDAP Contact field name: ", dotftok[1]
              print "valid RDAP Contact fields are : ", self.rdapcfg['entityfield']
	      return False

	  ## query for fields 
	  if dotftok[0].upper() == 'G' :
	    self.geoquery.append(dotftok[1].strip().upper())
	  elif dotftok[0].upper() == 'RI' :
	    self.rdapipquery.append(dotftok[1].strip().upper())
	  elif dotftok[0].upper() == 'RE' :
	    self.rdapcquery.append(dotftok[1].strip().upper())

      ## exame each field in FROM 
      if sqlcmd == 'FROM' and itok[1] == '*' :
        self.nonullsql.append(sqlcmd)
	self.usripquery.append('*')
      elif itok[0].upper() == 'FROM' and itok[1] != '*' :
        self.nonullsql.append(sqlcmd)
        for ip in itok[1].split(','):
	  if ip not in self.iplist:
	    print "Error> ERROR: ", ip, "is not in input IP list"
	    continue
	  self.usripquery.append(ip)  ## query for IPs

      ## exame field in WHERE
      if sqlcmd == 'WHERE':
        self.outputquery = itok[1].strip()
  
    ## SELECT and FROM must be in query 
    for sql in self.userqcfg['nonull']:
      if sql not in self.nonullsql :
        print "Error> " + sql + " must be in query"
        return False
   
    ## SELECT or FROM can't be more than one
    if len(self.nonullsql) != 2 :
      print "Error> same sql can't be more than one", self.nonullsql
      return False
 
    return True
