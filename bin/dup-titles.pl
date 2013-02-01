#!/usr/bin/perl -w

use strict;

open(TITLE,$ARGV[0] ) || die("canna open title file!");
open(WORKFLOW,$ARGV[1]) || die("canna open workflow file");

my %id2workflow=();
my %id2title=();
my %title2ids=();

while(<WORKFLOW>){
  chomp;
  my($id,$workflow)= split("\t");
  $id2workflow{$id}=$workflow;
}

while(<TITLE>){
  chomp;
  my($id,$title)= split("\t");
  $id2title{$id}= lc $title;
}


for my $id ( keys %id2title ) {
  my $title = $id2title{$id};
  $title2ids{$title} ||= [];
  push @{$title2ids{$title}}, $id;
}

my @sqls = ();

print("<html><head><title>Duplicate Titles in DASH</title></head><body>\n\n");

print("<ol>\n");

for my $title ( sort keys %title2ids ) {
  if ( @{$title2ids{$title}} > 1 ) {
    my $itemsql="";
    my $workflowsql="";
    print("  <li>Duplicated Title: $title\n");
    print("    <ul>");
    for my $id (  sort @{$title2ids{$title}} ) {
      print "      <li>";
      print "item id: <a href=\"http://dash.harvard.edu/admin/item?itemID=$id\">$id</a> | ";
      if ( $id2workflow{$id} ) {
	my $workflow = $id2workflow{$id};
	print("workflow id: <a href=\"http://dash.harvard.edu/handle/0/0/workflow?workflowID=$workflow\">$workflow</a>");
	$itemsql = "update item set withdrawn = 1 where item_id=$id";
	$workflowsql="delete from workspaceitem where item_id=$id";
      }
      print "</li>\n";
    }
    if ($itemsql){
      push @sqls, $itemsql;
      push @sqls, $workflowsql;
    }
    print("    </ul></li>\n");
  }
}


print "<pre>";

#for my $sql ( @sqls ) {
#  print "$sql;\n";
#}

print "</pre>";

print("</ol>");
print("</body>");
print("</html>");
