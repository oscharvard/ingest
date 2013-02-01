#!/bin/bash

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

echo "You are on $HOSTNAME" 

export AUTO=/home/osc/prod/auto;
export PROPS=$AUTO/conf/$HOSTNAME.properties;
export INC=/home/osc/prod/inc/workflow
export JAVA_HOME=/usr/lib/jvm/jre-1.6.0-openjdk
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=$AUTO/common/lib/ojdbc14-10.2.0.2.0.jar:$AUTO/common/bin;

java JSD $PROPS "
select item_id,dbms_lob.substr( metadatavalue.text_value, 4000, 1 ) as citation  from metadatavalue where metadata_field_id = 18 order by citation
" > $AUTO/ingest/data/dup-report.tsv;


java JSD $PROPS "
select item_id from metadatavalue where 
metadata_field_id = 28
and
text_value like '%2011-01-29%'
" > $AUTO/ingest/data/suspect-ids.tsv

java JSD $PROPS "
select item_id, workflow_id from workflowitem
" > $AUTO/ingest/data/workflow.tsv


java JSD $PROPS "
select mdv.item_id,dbms_lob.substr( mdv.text_value, 4000, 1 ) as title
from  metadatavalue mdv, item i
where 
i.item_id = mdv.item_id
and
mdv.metadata_field_id = 64
and
i.withdrawn=0
order by title
" > $AUTO/ingest/data/titles.tsv