#!/usr/bin/perl -w
use strict;
use warnings;
chomp(my @from=<DATA>);

require POSIX;
my %seen_dev_inode=();

# Fix path separators
(my $path_sep=POSIX::getcwd())=~s#^(?:\w+:)?(.).*#$1#;

sub du_r {
  my ($f) = @_;
  my @s=lstat($f); 
  unless(@s) {
    warn "lstat() failed for $f: $!";
  }
  if($s[1] and $seen_dev_inode{$s[0]}{$s[1]}) {
    return 0; # Already seen.
  }
  $seen_dev_inode{$s[0]}{$s[1]}=1;
  my $size = $s[12] ? 512*$s[12] : $s[7];
  $size||=0;
  if(not(-l $f) and -d $f) {
    my $owd = POSIX::getcwd();
    my @dents;
    if(opendir(DIR, "$f")) {
      @dents = grep {!m/^(\.\.?)$/} readdir DIR;
      closedir DIR;
    }
    $size+=du_r(join($path_sep, $f, $_)) for @dents;
  }
  return $size;
}
if($^X=~/[.]dll$/) {
  print "HTTP/1.1 200 OK\r\n";
}
print "Content-Type: text/plain\r\n\r\n";
@from = map {s#/#$path_sep#g; $_} @from;
#
printf("%.0fM\n", du_r($_)/(1024*1024)) for @from;
close(DATA) and unlink($0);
__DATA__
../