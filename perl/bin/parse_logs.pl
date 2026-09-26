#!/usr/bin/env perl
use strict;
use warnings;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Getopt::Long qw(GetOptions);
use CS466::ReportGenerator;

my ($input, $output, $help);
GetOptions(
    'input=s'  => \$input,
    'output=s' => \$output,
    'help'     => \$help,
) or usage(2);

usage(0) if $help;
usage(2) unless $input && $output;
die "Input file does not exist: $input\n" unless -f $input;

my $stats = CS466::ReportGenerator->export_logs_csv(input => $input, output => $output);
print "Wrote CSV: $output\n";
print "Parsed: $stats->{parsed}, malformed: $stats->{malformed}, unknown_event: $stats->{unknown_event}\n";
exit 0;

sub usage {
    my ($code) = @_;
    print "Usage: perl perl/bin/parse_logs.pl --input backend.log --output perl/output/logs.csv\n";
    exit $code;
}
