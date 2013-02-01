#!/usr/bin/perl -w

# first overcomplicated approach. duplicate citations. confused. but nailed low hanging fruit.

use strict;

my %citation2ids;
my %suspect_ids;
my %id2workflow;

open(CITATION2IDS,$ARGV[0]) || die("canna open citations 2 ids file");
open(SUSPECT_IDS,$ARGV[1]) || die("canna open suspect ids file");
open(WORKFLOW,$ARGV[2]) || die("canna open workflow file");

while(<SUSPECT_IDS>){
  chomp;
  $suspect_ids{$_}=1;
}

while(<WORKFLOW>){
  chomp;
  my($id,$workflow)= split("\t");
  $id2workflow{$id}=$workflow;
}

while(<CITATION2IDS>){
  chomp;
  my ($id,$citation)=split("\t");
  $citation2ids{$citation} ||= [];
  push @{$citation2ids{$citation}}, $id;
}

my $dup_citation_count=0;
my $dup_item_count=0;
my @ids2withdraw;

for my $citation ( keys %citation2ids) {
  if ( @{$citation2ids{$citation}} > 1) {
    print("Duplicate items for citation!\n");
    print("Citation: $citation\n");
    $dup_citation_count++;
    for my $id ( @{$citation2ids{$citation}} ) {
      $dup_item_count++;
      print("ID: $id\n");
      if ( $suspect_ids{$id} ) {
	push @ids2withdraw,$id;
      }
    }
  }
}

print("Dup Citation Count: $dup_citation_count\n");
print("Dup Item Count: $dup_item_count\n");

print("Ids 2 withdraw: " . scalar(@ids2withdraw) . "\n");

my $workflow_count=0;


for my $id ( @ids2withdraw ) {
  print "<li>";
  if ( $id2workflow{$id} ) {
    my $workflow = $id2workflow{$id};
    print(qq{<a href="http://dash.harvard.edu/handle/0/0/workflow?workflowID=$workflow">Workflow: $workflow</a> | });
  }
  print(qq{ <a href="http://dash.harvard.edu/admin/item?itemID=$id">Withdraw: $id</a></li>\n});

}

print("Workflow count: $workflow_count\n");
