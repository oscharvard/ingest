#!/bin/env python3

import argparse
from http.client import HTTPConnection
import http.cookiejar
from time import sleep
import urllib.request
from urllib.parse import urlparse, parse_qsl

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

# written for pubmed,
# but should be provider agnostic -- work with any OAI-PMH provider.
# just download the files, following resumptionTokens for further analysis.
#

# usage:
# export OSCROOT=/home/osc;
# mkdir $OSCROOT/proj/pubmed/data/batch/pmc2012_04.2012_10_10;
# mkdir $OSCROOT/proj/pubmed/data/batch/pmc2012_04.2012_10_10/oai;
# $OSCROOT/proj/ingest/bin/oai-harvest.py -u "http://www.pubmedcentral.nih.gov/oai/oai.cgi?verb=ListRecords&metadataPrefix=pmc_fm&from=2012-04-01&until=2012-04-30&set=pmc-open" -d "$OSCROOT/proj/pubmed/data/batch/pmc2012_04.2012_10_10/oai"
# todo: directory creation stuff should be part of script
# todo: should automatically figure out last day of month for "until" parameter.
# maybe another script that calls this one could handle those bits to keep this one generic and flexible.

def createOpener():
    HTTPConnection.debuglevel = 10
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return opener

def extractBaseResumptionUrl(initialUrl):
    urlObject =urlparse(initialUrl)
    queryStringKeyValues = parse_qsl(urlObject.query)
    url = urlObject.scheme + '://' + urlObject.netloc + urlObject.path + '?'
    for keyvalue in queryStringKeyValues :
        key = keyvalue[0]
        value = keyvalue[1]
        if key.lower() == 'verb' :
            url += key + "=" + value
    return url

def extractResumptionToken(responseData):
    tree = etree.fromstring(responseData)
    resumptionToken = tree.findall('.//{http://www.openarchives.org/OAI/2.0/}resumptionToken')
    if len(resumptionToken) > 0 :
        print("Got resumptionToken: " + resumptionToken[0].text + "\n")
        return resumptionToken[0].text
    else :
       print("No resumptionToken. We're done.\n")

def savePage(responseData,outputDir,pageCount):
    out_file = open(outputDir+"/page"+str(pageCount) + ".xml", "wb")
    out_file.write(responseData)
    out_file.close()

def getArgs():
    parser = argparse.ArgumentParser(description='Script to fetch OAI-PMH url and all resumptionToken pages and save to specified directory for futher processing.')
    parser.add_argument('-d','--dir', help='Download directory for this run', required=True)
    parser.add_argument('-u','--url', help='OAI PMH url.', required=True)
    parser.add_argument('-r','--resumptiontoken', help='Resumption token - in case of failure, break glass', required=False, default="Initial Request")
    return vars(parser.parse_args())

def main():

    opener = createOpener()
    args = getArgs()
    outputDir = args['dir']
    initialUrl = args['url']
    baseResumptionUrl = extractBaseResumptionUrl(initialUrl)
    url = initialUrl
    pageCount=1
    print("url: " + url + "\nbaseResumptionUrl: " + baseResumptionUrl)
    resumptionToken = args['resumptiontoken']

    while resumptionToken:
        print("Opening url: " + url)

        retries = 5
        for tries in range(1, retries + 1):
            try:
                response = opener.open(url)
                break
            except urllib.error.HTTPError as e:
                print("Encountered exception: {}".format(e))
                if tries == retries:
                    raise e
                sleep(tries * 3)

        if response.status == 200:
            responseData = response.read()
            resumptionToken = extractResumptionToken(responseData)
            savePage(responseData,outputDir,pageCount)
            pageCount+=1
            if resumptionToken:
                url = baseResumptionUrl + "&resumptionToken=" + resumptionToken
                print("Found Resumption Token. Waiting 1 second before next request...")
                sleep(1)
        else:
            exit("HTTP Error! Exiting")

main()
