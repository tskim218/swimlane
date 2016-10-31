#!/usr/bin/python

from Parse import *
import os,sys,string

#################################################
## Test Cases for query
## No input from user
#################################################
class UserQueryTestCase(object):
  def __init__ (self, gdb, ripdb, rcontactdb, geocfg, rdapcfg, usrqcfg, iplist):
    self.geoipdb        = gdb
    self.rdapipdb       = ripdb
    self.rdapcontactdb  = rcontactdb
    self.geocfg         = ConfigParse(geocfg).getConfigList()
    self.rdapcfg        = ConfigParse(rdapcfg).getConfigList()
    self.usrqcfg        = ConfigParse(usrqcfg).getConfigList()
    self.iplist         = iplist

  def usage (self):
    print "\n\n++++++++++++++++++++++++++++ USAGE +++++++++++++++++++++++++++\n"
    usage_str = "select <source.fields in comma-delimited>; "
    print usage_str
    usage_str = "from <ips in comma-delimited>; "
    print usage_str
    usage_str = "[where] <full path output file>; END"
    print usage_str
    print "where is option "
    print "(e.q : select g.country_name,ri.name,re.name; from 1.1.1.1,2.2.2.2;END)"
    print "e.x: g is geoip, ri is rdapip, re is rdapentity"
    print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
   

  def testCases (self):
    ## test case 1: success
    query1 = "select * ; from * ; where test1.out ; end"
    print "\n+++++++ TEST CASE1 ++++++++"
    print "Query statement is ", query1
    print "output to File: test1.out"
    self.parseInput(query1)

    ## test case 2: fail
    query2 = "select hello ; from * ; end"
    print "\n+++++++ TEST CASE2 ++++++++"
    print "Query statement is ", query2
    self.parseInput(query2)

    ## test case 3: fail
    query3 = "query g.*,ri.*,re.* ; from * ; end"
    print "\n+++++++ TEST CASE3 ++++++++"
    print "Query statement is ", query3
    self.parseInput(query3)

    ## test case 4: success
    query4 = "select g.country_name,g.city,ri.name,re.name ; from * ; end"
    print "\n+++++++ TEST CASE4 ++++++++"
    print "Query statement is ", query4
    self.parseInput(query4)

  def parseInput(self, finalanswer):
    queryparse  = userQueryParse(finalanswer,self.usrqcfg,self.geocfg,self.rdapcfg,self.iplist)
    ugeoip, urdapip, urdapentity, uusrips, outputfile = queryparse.userAns()

    if (ugeoip == None and urdapip == None and urdapentity == None and uusrips == None):
      print "==== Error in Syntax, Try Again! ===="
    else:
      self.runQuery(ugeoip, urdapip, urdapentity, uusrips, outputfile) 

  def runQuery(self, ugeoip, urdapip, urdapentity, uusrips, output):
    ## output to Fiel or screen ?
    outPtr = None
    if output != "" :
      outf   = Parse(output)
      outPtr = outf.getOutFilePtr()

    queryforIPs = []
    if len(uusrips) == 1 and uusrips[0] == '*' :
      queryforIPs = self.iplist
    else:
      queryforIPs = uusrips
 
    for ip in queryforIPs:
      if (outPtr != None):
        outPtr.write("\n@@@@@@@@@@@@@@@@@@ ["+ip+"] @@@@@@@@@@@@@@@@@@\n")
      else:
        print "\n@@@@@@@@@@@@@@@@@@ ["+ip+"] @@@@@@@@@@@@@@@@@@\n"

      ## run GeoIP info
      if (outPtr != None):
        outPtr.write("[ GEO IP ]\n")
      else:
        print "[ GEO IP ]"
      if len(ugeoip) == 1 and ugeoip[0] == '*' :
	for item in self.geocfg['field']:
	  if (self.geoipdb[ip].has_key(item)):
            if (outPtr != None):
              outstr = "%s%s%s" % ('{0:30} => '.format(item), self.geoipdb[ip][item], "\n")
	      outstr = outstr.encode('ascii','ignore')
	      outPtr.write(outstr)
	    else:
              print '{0:30} => '.format(item), self.geoipdb[ip][item]
      else: 
        for item in ugeoip:
	  if (self.geoipdb[ip].has_key(item)):
	    if (outPtr != None):
	      outstr = "%s%s%s" % ('{0:30} => '.format(item), self.geoipdb[ip][item], "\n")
	      outstr = outstr.encode('ascii','ignore')
              outPtr.write(outstr)
	    else:
              print '{0:30} => '.format(item), self.geoipdb[ip][item]

      ## run RDAP IP info
      if (outPtr != None):
	outPtr.write("[ RDAP IP ]\n")
      else:
        print "[ RDAP IP ]"
      if len(urdapip) == 1 and urdapip[0] == '*' :
	for item in self.rdapcfg['ipfield']:
	  if (self.rdapipdb[ip].has_key(item)):
	    if (outPtr != None):
              outstr = "%s%s%s" % ('{0:30} => '.format(item), self.rdapipdb[ip][item], "\n")
	      outstr = outstr.encode('ascii','ignore')
	      outPtr.write(outstr)
	    else:
              print '{0:30} => '.format(item),  self.rdapipdb[ip][item]
      else:
        for item in urdapip:
	  if (self.rdapipdb[ip].has_key(item)):
	    if (outPtr != None):
              outstr = "%s%s%s" % ('{0:30} => '.format(item), self.rdapipdb[ip][item], "\n")
	      outstr = outstr.encode('ascii','ignore')
	      outPtr.write(outstr)
	    else:
              print '{0:30} => '.format(item), self.rdapipdb[ip][item]

      ## run RDAP Contact (entities) info
      if (outPtr != None):
        outPtr.write("[ RDAP Contact ]\n")
      else:
        print "[ RDAP Contact ]"
      for contact in self.rdapcontactdb[ip]:
	try:
	  if (outPtr != None):
	    outPtr.write("[- "+contact['ROLES']+" -]\n")
	  else:
	    print "[- "+contact['ROLES']+" -]"
	except:
	  if (outPtr != None):
	    outPtr.write("[- NULL -]\n")
	  else:
	    print "[- NULL -]"
	if len(urdapentity) == 1 and urdapentity[0] == '*' :
	  for item in self.rdapcfg['entityfield']:
	    if (contact.has_key(item)):
	      if(outPtr != None):
                outstr = "%s%s%s" % ('{0:30} => '.format(item), contact[item], "\n")
		outstr = outstr.encode('ascii','ignore')
		outPtr.write(outstr)
	      else:
                print '{0:30} => '.format(item), contact[item]
        else:
          for item in urdapentity:
	    if (contact.has_key(item)):
    	      if (outPtr != None):
                outstr = "%s%s%s" % ('{0:30} => '.format(item), contact[item], "\n")
		outstr = outstr.encode('ascii','ignore')
		outPtr.write(outstr)
	      else:
                print '{0:30} => '.format(item), contact[item]

    if (outPtr != None):
      outPtr.close()
