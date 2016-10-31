#!/usr/bin/python

from Parse             import *
from LookUp            import *
from UserQueryTestCase import *
import os,sys,string

####################################
## Main function for test cases
####################################

def usage():
  print "-------- USAGE ------"
  print "-- PLEASE USE full Path --"
  print ("Usage: python FindIPInfo.py -g GeoIP.cfg -r RDAP.cfg -u UserQuery.cfg -i IPList.dat -h <help>")

def main():
  rdapConfig      = ""
  geoipConfig     = ""
  userqueryConfig = ""
  iplist          = ""

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'g:r:i:u:h', ['geoip=', 'rdap=', 'ip=', 'usr=', 'help'])
  except getopt.GetoptError:
    usage()
    sys.exit(1)
    
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
      sys.exit(1)
    elif opt in ('-g', '--geoip'):
      geoipConfig = arg
    elif opt in ('-r', '--rdap'):
      rdapConfig = arg
    elif opt in ('-i', '--ip'):
      iplist = arg
    elif opt in ('-u', '--usr'):
      userqueryConfig = arg
    else:
      assert False, "illegal option"

  if (rdapConfig == "" or geoipConfig == "" or userqueryConfig == "" or iplist == ""):
    usage()
    sys.exit(1)

  ## Extract IP addresses from input file
  ipextractor = IPExtractor(iplist)
  ipList      = ipextractor.getIPs()

  ## Perform GeoIP with ipList  
  objGeoIP = LookUpFactory("GeoIP")
  geoip = objGeoIP.initLookUp(geoipConfig, ipList)
  geoip.queryGeoIPInfo()
 
  ## Perform RDAP with ipList 
  objRDAP  = LookUpFactory("RDAP")
  rdap  = objRDAP.initLookUp(rdapConfig, ipList)
  rdap.queryRDAPInfo()

## get Geo IP info
  geoipdb = geoip.getGeoIPDB()
#  for ip in geoipdb.keys():
#    print "---- ", ip, "-----"
#    for content in geoipdb[ip].keys():
#      print content, "=>", geoipdb[ip][content]


## get RDAP IP info
  rdapipdb = rdap.getRDAPIPDB()
#  for ip in rdapipdb.keys():
#    print '----', ip, '------'
#    for content in rdapipdb[ip].keys():
#        print content, "=>", rdapipdb[ip][content]


## get RDAP Contact Info
  rdapcontactdb = rdap.getRDAPContactsDB()
#  for ip in rdapcontactdb.keys():
#    print "----", ip, "-------"
#    for contacts in rdapcontactdb[ip]:
#      for c in contacts.keys():
#        print c, "=>", contacts[c]
#      print "++++++"

  ## run user query
  userquery = UserQueryTestCase(geoipdb,rdapipdb,rdapcontactdb,
	                        geoipConfig,rdapConfig,userqueryConfig,ipList)
  userquery.testCases()

if __name__ == '__main__':
  main()
