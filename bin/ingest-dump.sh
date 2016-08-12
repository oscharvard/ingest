#!/bin/bash

# script to dump dash data for batch ingest scripts.
# maybe move to dashdump.sh?

export BASE=/home/osc
export OSC_COMMON=$BASE/common;
export PROPS=$BASE/conf/$HOSTNAME.properties;
export PROJECT=$BASE/proj/ingest;
export DATA=$PROJECT/data;
export TSV=$DATA/tsv;
#export CLASSPATH=$OSC_COMMON/lib/ojdbc14-10.2.0.2.0.jar:$OSC_COMMON/bin;
export CLASSPATH=$OSC_COMMON/lib/ojdbc6-12.1.0.1.jar:$OSC_COMMON/bin;

## dump citations

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_citation.text_value, 3940, 1 ) as citation from metadatavalue mdv_citation where mdv_citation.metadata_field_id=18
"  >  $TSV/citations.tsv

## dump dois

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_doi.text_value, 4000, 1 ) as doi from metadatavalue mdv_doi where mdv_doi.metadata_field_id=45
"  > $TSV/dois-dirty.tsv

$PROJECT/bin/clean-dois.pl $TSV/dois-dirty.tsv > $TSV/dois.tsv

## dump pmc ids (pubmed central)

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_hasversion.text_value, 4000, 1 ) as hasversion from metadatavalue mdv_hasversion where mdv_hasversion.metadata_field_id=46
and mdv_hasversion.text_value like '%PMC%' "  > $TSV/pmcids.tsv

perl -p -i -e "s#^.*PMC##"  $TSV/pmcids.tsv;
perl -p -i -e "s#.pdf.+##"  $TSV/pmcids.tsv;
perl -p -i -e "s#\/##"  $TSV/pmcids.tsv;

sort -n $TSV/pmcids.tsv > $TSV/temp.tsv;
uniq    $TSV/temp.tsv   > $TSV/pmcids.tsv;

rm      $TSV/temp.tsv;


## dump pmc ids (pubmed central) REINOS

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select mdv_hasversion.text_value as hasversion,mdv_hasversion.item_id  from metadatavalue mdv_hasversion where mdv_hasversion.metadata_field_id=46 and mdv_hasversion.text_value like '%PMC%'"  > $TSV/pmcid2dashid.tsv;

perl -p -i -e "s#^.*PMC##"  $TSV/pmcid2dashid.tsv;
perl -p -i -e "s#.pdf.+\t#\t#"  $TSV/pmcid2dashid.tsv;
perl -p -i -e "s#\/\t#\t#"  $TSV/pmcid2dashid.tsv;

sort -n $TSV/pmcid2dashid.tsv > $TSV/temp2.tsv;
uniq    $TSV/temp2.tsv   > $TSV/pmcid2dashid.tsv;

rm      $TSV/temp2.tsv;


## dump external urls ("hasversion")

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_hasversion.text_value, 4000, 1 ) as hasversion from metadatavalue mdv_hasversion where mdv_hasversion.metadata_field_id=46"  > $TSV/hasversions.tsv

sort -n $TSV/hasversions.tsv > $TSV/temp.tsv;
uniq    $TSV/temp.tsv   > $TSV/hasversions.tsv;
rm      $TSV/temp.tsv;


## dump external ids 

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_id_other.text_value, 4000, 1 ) as id_other from metadatavalue mdv_id_other where mdv_id_other.metadata_field_id=24"  > $TSV/id-others.tsv

sort -n $TSV/id-others.tsv > $TSV/temp.tsv;
uniq    $TSV/temp.tsv   > $TSV/id-others.tsv;
rm      $TSV/temp.tsv;


## dump titles

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select dbms_lob.substr( mdv_title.text_value, 4000, 1 ) as title from metadatavalue mdv_title where mdv_title.metadata_field_id=64
"  > $TSV/titles.tsv

## external id to nrs uri (done from proquest etds)
## aka dump dc.identifier.other -> dc.identifier.uri

java -Djava.security.egd=file:/dev/../dev/urandom JSD $PROPS "
select mdv_external.text_value ,mdv_nrs.text_value
from metadatavalue mdv_external, metadatavalue mdv_nrs 
where 
mdv_external.metadata_field_id = 24 
and
mdv_nrs.metadata_field_id = 25
and
mdv_external.item_id = mdv_nrs.item_id
"  > $TSV/external2nrs.tsv
