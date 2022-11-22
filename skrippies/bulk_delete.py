#!/usr/bin/python3

# HOW TO USE THIS SCRIPT:
#
# 1) source the environment file with your swift credentials 
#
# 2) generate a list of objects in a container, like so:
# swift list largecontainer > objectlist.txt
# 
# 3) generate a token:
# openstack token issue
#
# 3b) optionally, use environment variables
# export TOKEN=whateveryourgeneratedtokenis
# export ACCOUNT=whateveryouraccountis
#
# 4) run the script with the required or wanted arguments
# (batches are quite small by default)
# account is the project_id shown by "openstack token issue"
# you can use the -d flag to see what it would do
# use the -f flag for it to actually execute the curl call
#
# example:
# bulk_delete.py -a $ACCOUNT -t $TOKEN -c largecontainer -o objectlist.txt -n 10 -s 500 -d -f
 
import sys
import os
import argparse
import string
from itertools import islice
import urllib.parse

#
# Parse user input from command-line
#
parser = argparse.ArgumentParser(description='Reads objects from a file and does a bulk delete')
parser.add_argument("-e", "--endpoint", type=str, default="proxy.swift.surfsara.nl", required=False, help="swift endpoint")
parser.add_argument("-a", "--account", type=str, required=True, help="swift account")
parser.add_argument("-t", "--token", type=str, required=True, help="authtoken")
parser.add_argument("-c", "--container", type=str, required=True, help="name of container")
parser.add_argument("-o", "--objects", type=str, required=True, help="name of file with object listing")
parser.add_argument("-s", "--batchsize", type=int, default=10, help="number of objects per batch")
parser.add_argument("-n", "--numbatches", type=int, default=5, help="number of batches to execute")
parser.add_argument("-f", "--force", action="count", default=0, help="actually run the curl command")
parser.add_argument("-d", "--debug", action="count", default=0, help="debug output")
args = parser.parse_args()

#
# Set input in readable string
#
endpoint   = args.endpoint
account    = args.account
token      = args.token
container  = args.container
objects    = args.objects
batchsize  = args.batchsize
numbatches = args.numbatches
force      = args.force
debug      = args.debug

def prepare(line):
  line = line.strip()
  line = urllib.parse.quote_plus(line)
  return line

# loop the input file and create the batches
batchnum = 0
with open(objects, "r") as fp:
  while batchnum < numbatches:
    batchnum = batchnum + 1
    print("Running batch %i of maximum %i" % (batchnum, numbatches))
    next_n_lines = list(islice(fp, batchsize))
    if not next_n_lines:
      break
    # create the body
    bulk = ""
    for line in next_n_lines:
      container = prepare(container)
      line = prepare(line)
      bulk = bulk + container + "/" + line + "\n"

    cmd = ""
    cmd = cmd + "curl -i https://proxy.swift.surfsara.nl/v1/KEY_%s?bulk-delete=true \\\n" % account
    cmd = cmd + "-X DELETE \\\n"
    cmd = cmd + "-H \"X-Auth-Token: %s\" \\\n" % token
    cmd = cmd + "-H \"Content-Type: text/plain\" \\\n"
    cmd = cmd + "-d \"%s\"" % bulk
    if debug:
      print()
      print("Command to execute:")
      print(cmd)
      print()
    if force:
      os.system(cmd)
      print()
 
