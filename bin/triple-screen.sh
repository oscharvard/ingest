#!/bin/bash

# redundant check of dash dspace import files to screen out duplicates.

# first, re-download all dash data dumps so we're current.

$OSCROOT/proj/ingest/bin/dump-dois.sh;
$OSCROOT/proj/ingest/bin/dump-titles.sh;
$OSCROOT/proj/ingest/bin/dump-pmcids.sh;

# now, find dublin_core xml files to check and 
# fee them to python triple-screen.py to handle xml field extraction and checking against dash dumps.

#find . -name "dublin_core.xml"  | $OSCROOT/proj/ingest/bin/triple-screen.py