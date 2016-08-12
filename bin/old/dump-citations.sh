#!/bin/bash

# script to dump *all* citations from dash database, live or not, stipped of screwy whitespace characters.
# for weeding out bulk ingest duplicates.


# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

export OSCROOT=/home/osc
export PROPS=$OSCROOT/conf/$HOSTNAME.properties;
export DATA=$OSCROOT/data/ingest;

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_citation.text_value, 4000, 1 ) as citation from metadatavalue mdv_citation where mdv_citation.metadata_field_id=18
"  >  $DATA/citations.tsv
