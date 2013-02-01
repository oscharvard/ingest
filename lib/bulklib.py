import difflib
import os
import re
from time import strftime
import sys
#from xml.dom.minidom import parse, parseString
import xml.sax.saxutils

OSCROOT=os.environ['OSCROOT']

sys.path.append(OSCROOT+'/common/lib/python3')
import tsv

# python 3 methods that can be shared by bulk ingest processes.
# among others: pubmed, arxiv, HLS Peter Hut ingest.

# methods for reading tsv and simple flat files
# note: use tsv.py for this stuff instead.

#def read_set(file) :
#    inp = open (file,"r")
#    myset = []
#    for line in inp.readlines():
#        line = line.rstrip()
#        myset.append(line)
#    return set(myset)

def load_fas_departments() :
    return tsv.read_map(OSCROOT+"/data/ingest/tsv/dashdept.tsv")

def load_dash_dois() :
    return tsv.read_set(OSCROOT+"/data/ingest/tsv/dois.tsv")

def load_dash_titles() :
    return tsv.read_set(OSCROOT+"/data/ingest/tsv/titles.tsv")

def load_dash_pmcids():
    return tsv.read_set(OSCROOT+"/data/ingest/tsv/pmcids.tsv")

# Methods for munging data

def orval(dictionary,key,value) :
    ''' orval = or value '''
    if key in dictionary and dictionary[key] != None :
        return dictionary[key]
    return value

def esc(string) :
    if string :
        return xml.sax.saxutils.escape(string)
    else :
        return ""

# Methods for matching and filtering 

def serial_search(patterns,string,notfound) :
    for pattern in patterns :
        m = re.search(pattern,string)
        if m :
            return m.group(1)
    return notfound

def prepfirst(name) :
    # this is a nasty and dangerous method. rethink.

    # get rid of middle initials
    name = re.sub("\W+"," ",name)
    parts = name.split(" ")

    if len(parts) == 2 and len(parts[1]) > 1 :
        ## example: Fan, Baojian	Fan, Bao Jian
        name = parts[0] +  parts[1]
    else :
        name = parts[0]

    # get rid of non word characters
    name = re.sub("\W+","",name)

    # deal with umlauts etc.
    name = re.sub("ö","oe",name);

    # expand shortnames. a little dangerous...
    if  name == 'Bob' :
        name = 'Robert'
    elif name == 'Chris' :
        name = 'Christopher'
    elif name == 'Connie' :
        name = 'Constance'
    elif name == 'Tim' :
        name = 'Timothy'
    elif name == 'Fred' :
        name = 'Frederick'
    elif name == 'Vlad' :
        name = 'Vladimir'
    elif re.match("[A-Z]{2}",name) :
        ## middle inital glues onto first initial
        name = name[0]
    return name


def match_authors(ldap_author,pubmed_author):
    ratio = 0.0
    if ldap_author['last'] == pubmed_author['last'] :
        # last names must match exactly
        ratio = .5
        if ldap_author['first'] == pubmed_author['first'] :
            # cheap test to see if first names match exactly
            ratio = 1.0
        elif len(prepfirst(pubmed_author['first'])) == 1 :
            # if all we have is an initial, and it matches, we give it a barely making the cutoff score.
            if ldap_author['first'][0] == pubmed_author['first'][0] :
                ratio = .85
        else :
            # do the fancy fuzzy match against first names
            ratio = ratio + (difflib.SequenceMatcher(None, prepfirst(ldap_author['first']), prepfirst(pubmed_author['first'])).ratio())/2 
    return ratio


# Methods for creating dspace files from article objects

def write_contents_file(article,article_dir) :
    path = article_dir + "/contents"
    print("Writing contents file " + path)
    f = open(path, "w")
    # todo: pmc specific crap here.
    #f.write(article['pmcid'] + ".pdf" + "\tbundle:ORIGINAL\n")
    for file in article['files'] :
        f.write(file['name'] + "\tbundle:ORIGINAL")
        if 'description' in file :
            f.write("\tdescription:" + file['description'])
        f.write("\n")
    if article['license'] is not 'META_ONLY' :
        # meta only has no license file.
        f.write('license.txt	bundle:LICENSE'+"\n")
    f.close()

def write_thesis_meta(article,article_dir) :
    path = article_dir + "/metadata_thesis.xml"
    #if not os.path.exists(path) :
    print("Writing thesis meta file " + path)
    f = open(path, "w")
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>'+"\n")
    f.write('<dublin_core schema="thesis">'+"\n")
    f.write('<dcvalue element="degree" qualifier="date" language="en_US">'+ article['thesis.degree.date']+ '</dcvalue>'+ "\n")
    f.write('<dcvalue element="degree" qualifier="discipline" language="en_US">'+ article['thesis.degree.discipline']+ '</dcvalue>'+ "\n")
    f.write('<dcvalue element="degree" qualifier="grantor" language="en_US">'+ article['thesis.degree.grantor']+ '</dcvalue>'+ "\n")
    f.write('<dcvalue element="degree" qualifier="level" language="en_US">'+ article['thesis.degree.level']+ '</dcvalue>'+ "\n")
    f.write('<dcvalue element="degree" qualifier="name" language="en_US">'+ article['thesis.degree.name']+ '</dcvalue>'+ "\n")
    f.write('</dublin_core>'+ "\n")
    f.close()

def write_dash_meta(article,article_dir) :
    path = article_dir + "/metadata_dash.xml"
    #if not os.path.exists(path) :
    print("Writing dash meta file " + path)
    f = open(path, "w")
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>'+"\n")
    f.write('<dublin_core schema="dash">'+"\n")
    f.write('<dcvalue element="license" qualifier="none">' + article['license'] + '</dcvalue>'+ "\n")
    if 'harvard_authors' in article and len(article['harvard_authors']):
        for author in article['harvard_authors'] :
            last = esc(author['last'])
            first = esc(author['first'])
            break
        f.write('<dcvalue element="depositing" qualifier="author">' + last + ', ' + first + '</dcvalue>' + "\n")
    if 'dash.affiliation.other' in article:
        for other in article['dash.affiliation.other'] :
            f.write('<dcvalue element="affiliation" qualifier="other" language="en_US">' + other + '</dcvalue>' + "\n")
    if 'embargo_until' in article :
        # why redundancy? why does a date go into "terms?" 
        f.write('<dcvalue element="embargo" qualifier="terms">' + article['embargo_until'] + '</dcvalue>\n')
        f.write('<dcvalue element="embargo" qualifier="until">' + article['embargo_until'] + '</dcvalue>\n')
    f.write('</dublin_core>'+ "\n")
    f.close()


def author_string(author) :
    return esc(author['last']) + ', ' + esc(advisor['first'])

def dc_value(element,qualifier,value,language) :
    sb = '<dcvalue element="' + element + '" qualifier="' + qualifier + '"'
    if language :
        sb += ' language="en"'
    sb += ('>' + value + '</dcvalue>'+"\n")
    return sb

def write_dc_authors(f,article,key,element,qualifier) :
    # key is what we call the multi-valued field in the author object. Example: 'authors' for dc.contributor.author
    if key in article :
        authors = article[key]
        for author in authors :
            f.write(dc_value(element,qualifier, esc(author['last']) + ', ' + esc(author['first']),None))

def write_dublin_core_meta(article,article_dir,batch) :
    path = article_dir + "/dublin_core.xml"
    print("Writing dublin core meta file " + path)
    f = open(path, "w")
    #f = open(path, encoding='utf-8', mode='w')
    f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>' + "\n")
    f.write('<dublin_core schema="dc">' + "\n")
    
    write_dc_authors(f,article,'authors','contributor','author')
    write_dc_authors(f,article,'advisors','contributor','advisor')
    write_dc_authors(f,article,'committeeMembers','contributor','committeeMember')

    if 'date' in article :
        f.write('<dcvalue element="date" qualifier="issued">'+ article['date'] + '</dcvalue>'+"\n")
    if 'submitted' in article :
        f.write('<dcvalue element="date" qualifier="submitted">'+ article['submitted'] + '</dcvalue>'+"\n")
    if 'citation' in article :
        f.write('<dcvalue element="identifier" qualifier="citation" language="en">'+ esc(article['citation']) + '</dcvalue>'+"\n")
    if 'issn' in article:
          f.write('<dcvalue element="identifier" qualifier="issn" language="en">' + article['issn'] + '</dcvalue>\n')
    if 'identifier.other' in article :
          f.write('<dcvalue element="identifier" qualifier="other" language="en">' + article['identifier.other'] + '</dcvalue>\n')
    if 'abstract' in article :
        f.write('<dcvalue element="description" qualifier="abstract" language="en">' + esc(article['abstract']) +'</dcvalue>' +"\n")
    f.write('<dcvalue element="language" qualifier="iso" language="en">en_US</dcvalue>' + "\n")
    if 'departments' in article:
        for department in article['departments'] :
            f.write('<dcvalue element="description" qualifier="sponsorship" language="en_US">' + department + '</dcvalue>' + "\n")
    if 'publisher' in article :
        f.write('<dcvalue element="publisher" qualifier="none" language="en">' + esc(article['publisher']) + '</dcvalue>' + "\n")
    if 'doi' in article :
        f.write('<dcvalue element="relation" qualifier="isversionof" language="en">doi:' + esc(article['doi']) + '</dcvalue>'+"\n")
    if 'hasversion' in article :
        f.write('<dcvalue element="relation" qualifier="hasversion" language="en">' + esc(article['hasversion']) +'</dcvalue>' + "\n")
    if 'pdf_url' in article :
        f.write('<dcvalue element="relation" qualifier="hasversion" language="en">' + esc(article['pdf_url']) +'</dcvalue>' + "\n")
    if 'subjects' in article :
        for subject in article['subjects'] :
            f.write('<dcvalue element="subject" qualifier="none" language="en">'+ esc(subject) + '</dcvalue>' + "\n")
    f.write('<dcvalue element="title" qualifier="none" language="en">' + esc(article['title']) + '</dcvalue>' + "\n")
    if 'journal' in article :
        f.write('<dcvalue element="relation" qualifier="journal" language="en">' + esc(article['journal']) + '</dcvalue>' + "\n")
        if not 'type' in article :
            article['type'] = 'Journal Article'
    f.write('<dcvalue element="type" qualifier="none" language="en_US">' + article['type'] +'</dcvalue>' + "\n")

    timestamp = strftime("%Y-%m-%dT%H:%M:%SZ")
    #'pubmed_3'

    f.write('<dcvalue element="description" qualifier="provenance" language="en">Batch uploaded (batch: ' + batch + ') by Reinhard Engels (reinhard_engels@harvard.edu) on ' + timestamp + '</dcvalue>' +"\n")
    f.write('</dublin_core>'+"\n")
    f.close()

# methods for extracting additional article metadate from crossref

def get_crossref_meta(doi) :
    meta = {}
    return meta
