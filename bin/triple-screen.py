#!/bin/env python3

# Script to double check dash for duplicates in dash imports.
# also checks that xml is valid.
# point it at import batch directory.

# usage:
# ./triple-screen.py 

# ~/proj/ingest/bin/triple-screen.py ~/proj/proquest/data/20120621/out/dash

# TODO:
# 1. check external id field. 
# 2. move suspicious items to
# quarrantine, along with report of suspicions for item, so we can
# load the rest quickly, then remove funny stuff at leisure.

import difflib
import os
import re
#import shutil
import sys
sys.path.append('/home/osc/proj/ingest/lib')
import bulklib
import xml.etree.ElementTree as etree  

quarantine_events = []

def prep_record(record) :
    return record.strip().lower()

def extract_title(dc_tree) :
    #print("FINDALL")
    for node in dc_tree.findall('.//dcvalue') :
        #print("ELEMENT", node.get("element"))
        if node.get("element") == 'title' :
            return node.text
    return None

def extract_id_other(dc_tree) :
    for node in dc_tree.findall('.//dcvalue') :
        #print("ELEMENT", node.get("element"))
        if node.get("element") == 'identifier' and node.get("qualifier") == 'other' :
            return node.text
    return None

def extract_hasversion(dc_tree) :
    for node in dc_tree.findall('.//dcvalue') :
        #print("ELEMENT", node.get("element"))
        if node.get("element") == 'relation' and node.get('qualifier' == 'hasversion' ) :
            return node.text
    return None


def extract_doi(node) :
    return None

def extract_pmcid(node) :
    return None

def needle_in_haystack(needle,haystack) :
    best_ratio = 0.0
    best_real_quick_ratio = 0.0
    best_quick_ratio = 0.0
    best_hay  = ""
    needle = prep_record(needle)
    for hay in haystack :
        hay = prep_record(hay) 
        sm = difflib.SequenceMatcher(None,needle,hay)
        ratio = 0.00
        quick_ratio = 0.00
        real_quick_ratio = sm.real_quick_ratio()
        if real_quick_ratio >= .80 :
            quick_ratio = sm.quick_ratio()
            if quick_ratio >= .80 :
                ratio       = sm.ratio()
        if ratio > best_ratio :
            best_real_quick_ratio = round(real_quick_ratio,3)
            best_quick_ratio      = round(quick_ratio,3)
            best_ratio            = round(ratio,3)
            best_hay  = hay
    in_haystack = 0
    print("Best match: " + str(best_real_quick_ratio) + "|" + str(best_quick_ratio) + "|" + str(best_ratio) + " : " + best_hay)
    if best_ratio >= .80 :
        print("CLOSE MATCH!")
        return True
    return False

def quarantine(item_path,item_file,screen_name,screened_value) :
    event = {}
    event['path'] = re.sub("\/[^\/]+\.xml$","",item_path)
    event['item_path'] = item_path
    event['item_file'] = item_file
    event['screen_name'] = screen_name
    event['screened_value'] = screened_value
    global quarantine_events
    quarantine_events.append(event)
    print("**********************************************")
    print("ITEM FAILED TO PASS SCREEN!")
    print("Top level Path: " + str(event['path']))
    print("Item Path: " + str(item_path))
    print("File: " + str(item_file))
    print("Screen name: " + str(screen_name))
    print("Screened value: " + str(screened_value))
    print("Adding to quarantine")
    print("**********************************************")

def main() :
    dash_titles = bulklib.load_dash_titles()
    dash_id_others = bulklib.load_dash_id_others()
    dash_hasversions = bulklib.load_dash_hasversions()
    path = sys.argv[1]
    process_batch_dir(path,dash_titles,dash_id_others,dash_hasversions)
    for event in quarantine_events :
        #quarantine_path = "quarantine/" + event['path']
        # add data, so mv is on the same device
        quarantine_path = "data/quarantine/" + event['path']
        os.system("mkdir -p " + quarantine_path)
        os.system("mv " + event['path'] + " " + quarantine_path + '/../')


def process_item_file(item_path,item_file,dash_titles,dash_id_others,dash_hasversions) :
    if item_file == 'dublin_core.xml' :
        print("Checking file: " + item_path)
        dc_tree = etree.parse(item_path)
        print("XML is well formed.")
        root = dc_tree.getroot()
        title = extract_title(dc_tree)
        id_other = extract_id_other(dc_tree)
        hasversion = extract_hasversion(dc_tree)
        print("ID other is: " + str(id_other))
        if id_other and id_other in dash_id_others :
            quarantine(item_path,item_file,'id_other',id_other)
            return
        print("hasversion is: " + str(hasversion))
        if hasversion and hasversion in dash_hasversions :
            quarantine(item_path,item_file,'hasversion',hasversion)
            return
        print("Title is: '" + str(title) + "'")
        if needle_in_haystack(title,dash_titles) :
            quarantine(item_path,item_file,'title',title)
            return
        else :
            print ("New title...")
    elif item_file == 'metadata_dash.xml' :
        ''' sanity check dash metadata file '''
        print("Checking file: " + item_path)
        dc_tree = etree.parse(item_path)
        print("XML is well formed.")
    elif item_file == 'metadata_thesis.xml' :
        ''' sanity check ETD metadata file '''
        print("Checking file: " + item_path)
        dc_tree = etree.parse(item_path)
        print("XML is well formed.")
        

def process_batch_dir(path,dash_titles,dash_id_others,dash_hasversions) :
    batch_dir = os.listdir(path)
    for item_dir in batch_dir :
        if os.path.isdir(path + "/" + item_dir) :
            if re.match("^\d+$",item_dir ) :
                # Looks like an item dir (numeric)
                for item_file in os.listdir(path + "/" + item_dir) : 
                    item_path =  path + "/" + item_dir + "/" + item_file
                    process_item_file(item_path,item_file,dash_titles,dash_id_others,dash_hasversions)
            else :
                # Looks like batch dir (HMS, FAS_HMS, etc)
                process_batch_dir(item_dir,dash_titles,dash_id_others,dash_hasversions)
        else :
            """ ignore non-directory files """
            print("ignoring: " + str(item_dir))
        
main()
