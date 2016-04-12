#!/bin/env python3

# script to build and update a dash nrs link to hollis id mapping file.
# takes no arguments, everything is hard coded below.
# done for proquest etd to drs push but conceivably useful for other stuff so sticking here.
# Read list of dash nrs urls (built from nightly dump).
# Read existing mapping file.
# Use presto api to query for hollis records by dash nrs url for anything we are missing.
# Update mapping file.

# sample hollis api url: 
# http://webservices.lib.harvard.edu/rest/classic/search/dc/ure%3Dhttp%3A%2F%2Fnrs.harvard.edu%2Furn-3%3AHUL.InstRepos%3A9920663

import os
import sys
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as etree  

OSCROOT=os.environ['OSCROOT']
sys.path.append(OSCROOT+'/common/lib/python3')
import tsv

def ask_presto(nrs) :
    presto_base_url = "http://webservices.lib.harvard.edu/rest/classic/search/marc/ure%3D"
    presto_url = presto_base_url + urllib.parse.quote_plus(nrs)
    print("nrs: " + nrs)
    print("presto url: " + presto_url)
    print("...")
    xml_string = urllib.request.urlopen(presto_url).read().decode('utf-8')
    xml = etree.fromstring(xml_string)
    item_node = xml.find('.//item')
    hollis = item_node.attrib['id']
    print("hollis: " + hollis)
    return hollis

def print_nrs2hollis(nrs2hollis,nrs2hollis_tsv_path) :
    f = open(nrs2hollis_tsv_path, 'w')
    f.truncate(0)
    for nrs in nrs2hollis.keys() :
        hollis = nrs2hollis[nrs]
        f.write(nrs+"\t"+hollis+"\n")
    f.close()

def main():
    nrss = tsv.read_map(OSCROOT+"/proj/ingest/data/tsv/external2nrs.tsv").values() # note: incomplete source of nrss. but enough for proquest stuff.
    nrs2hollis_tsv_path=(OSCROOT+"/proj/ingest/data/tsv/nrs2hollis.tsv")
    nrs2hollis = tsv.read_map(nrs2hollis_tsv_path)
    count=0
    for nrs in nrss :
        if nrs not in nrs2hollis :
            count+=1
            try :
                nrs2hollis[nrs] = ask_presto(nrs)
            except :
                print("PRESTO ERROR! No hollis number returned for nrs " + nrs)
                nrs2hollis[nrs] = "NONE"
            if count >= 50 :
                break
    print_nrs2hollis(nrs2hollis,nrs2hollis_tsv_path)

main()
