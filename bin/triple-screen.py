#!/bin/env python3

# Script to double check dash for duplicates in dash imports.
# also checks that xml is valid.
# point it at import batch directory.

# usage:
# ./triple-screen.py 

# ~/proj/ingest/bin/triple-screen.py ~/proj/proquest/data/20120621/out/dash

# todo: this should take a top level directory, then crawl ALL dash xml files (etd, dash, dublin core)

import difflib
import os
import re
import sys
sys.path.append('/home/osc/proj/ingest/lib')
import bulklib
import xml.etree.ElementTree as etree  


def prep_record(record) :
    return record.strip().lower()

def extract_title(dc_tree) :
    #print("FINDALL")
    for node in dc_tree.findall('.//dcvalue') :
        #print("ELEMENT", node.get("element"))
        if node.get("element") == 'title' :
            return node.text
    return None

def extract_doi(node) :
    return None

def extract_pmcid(node) :
    return None

def needle_in_haystack(needle,haystack) :
    best_ratio = 0
    best_hay  = ""
    needle = prep_record(needle)
    for hay in haystack :
        hay = prep_record(hay) 
        ratio = difflib.SequenceMatcher(None, needle, hay).ratio()
        if ratio > best_ratio :
            best_ratio = ratio
            best_hay  = hay
    in_haystack = 0
    if best_ratio >= .70 :
        print("Best match: " + str(best_ratio) + " : " + best_hay)
        return True
    return False

dash_titles = bulklib.load_dash_titles()

path = sys.argv[1]
batch_dir = os.listdir(path)
for item_dir in batch_dir :
    for item_file in os.listdir(path + "/" + item_dir) : 
        item_path =  path + "/" + item_dir + "/" + item_file
        if item_file == 'dublin_core.xml' :
            print("Checking file: " + item_path)
            dc_tree = etree.parse(item_path)
            print("XML is well formed.")
            root = dc_tree.getroot()
            title = extract_title(dc_tree)
            print("Title is: '" + str(title) + "'")
            if needle_in_haystack(title,dash_titles) :
                print("ALERT: SIMILAR TITLE ALREADY IN DASH!")
                #exit()
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



