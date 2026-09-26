#!/usr/bin/env perl
use strict;
use warnings;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Getopt::Long qw(GetOptions);
use CS466::LogAnalyzer;
use CS466::ReportGenerator;

my ($input, $help);
GetOptions(
    'input=s' => \$input,
    'help'    => \$help,
) or usage(2);

usage(0) if $help;
usage(2) unless $input;
die "Input file does not exist: $input\n" unless -f $input;

my $analyzer = CS466::LogAnalyzer->new;
my $summary = $analyzer->analyze_file($input);
print CS466::ReportGenerator->format_console_summary($summary);
exit 0;

sub usage {
    my ($code) = @_;
    print "Usage: perl perl/bin/analyze_logs.pl --input backend.log\n";
    exit $code;
}
