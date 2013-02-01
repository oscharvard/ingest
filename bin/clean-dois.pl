#!/usr/bin/perl -w

use strict;

while (<>){
  s/http\:\/\/dx\.doi\.org\///;
  s/http\:\/\/doi\.acm\.org\///;
  s/http\:\/\/dx\.doi\.org\.ezp-prod1\.hul\.harvard\.edu\///;
  s/doi\:\/\///;
  s/doi\://;
  
  s/^[^1]+10\./10./;
  print;
}
