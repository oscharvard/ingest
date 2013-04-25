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
    if best_ratio >= .80 :
        print("CLOSE MATCH!")
        return True
    print("Best match: " + str(best_real_quick_ratio) + "|" + str(best_quick_ratio) + "|" + str(best_ratio) + " : " + best_hay)
    return False

def main() :
    dash_titles = bulklib.load_dash_titles()
    path = sys.argv[1]
    process_batch_dir(path,dash_titles)

def process_item_file(item_path,item_file,dash_titles) :
    if item_file == 'dublin_core.xml' :
        print("Checking file: " + item_path)
        dc_tree = etree.parse(item_path)
        print("XML is well formed.")
        root = dc_tree.getroot()
        title = extract_title(dc_tree)
        print("Title is: '" + str(title) + "'")
        if needle_in_haystack(title,dash_titles) :
            print("!!!!!!!!!!!!!!!!! ALERT: SIMILAR TITLE ALREADY IN DASH!!!!!!!!!!!!!!!!")
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


def process_batch_dir(path,dash_titles) :
    batch_dir = os.listdir(path)
    for item_dir in batch_dir :
        if os.path.isdir(path + "/" + item_dir) :
            if re.match("^\d+$",item_dir ) :
                # Looks like an item dir (numeric)
                for item_file in os.listdir(path + "/" + item_dir) : 
                    item_path =  path + "/" + item_dir + "/" + item_file
                    process_item_file(item_path,item_file,dash_titles)
            else :
                # Looks like batch dir (HMS, FAS_HMS, etc)
                process_batch_dir(item_dir,dash_titles)
        else :
            """ ignore non-directory files """
            print("ignoring: " + str(item_dir))
        
main()
