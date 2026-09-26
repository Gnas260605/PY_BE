#!/usr/bin/env perl
use strict;
use warnings;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Getopt::Long qw(GetOptions);
use CS466::Config;
use CS466::LogAnalyzer;
use CS466::ReportGenerator;

my ($input, $config_path, $help);
GetOptions(
    'input=s'  => \$input,
    'config=s' => \$config_path,
    'help'     => \$help,
) or usage(2);

usage(0) if $help;
usage(2) unless $input;
die "Input file does not exist: $input\n" unless -f $input;

$config_path ||= "$FindBin::Bin/../config/perl.json";
my $config = CS466::Config->load($config_path);
my $analyzer = CS466::LogAnalyzer->new(config => $config);
my $summary = $analyzer->analyze_file($input);
print CS466::ReportGenerator->format_console_summary($summary);
exit 0;

sub usage {
    my ($code) = @_;
    print "Usage: perl perl/bin/analyze_logs.pl --input backend.log [--config perl/config/perl.json]\n";
    exit $code;
}
