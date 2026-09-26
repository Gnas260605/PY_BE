#!/usr/bin/env perl
use strict;
use warnings;
use FindBin;
use lib "$FindBin::Bin/../lib";
use Getopt::Long qw(GetOptions);
use CS466::Config;
use CS466::ReportGenerator;

my ($input, $output, $config_path, $help);
GetOptions(
    'input=s'  => \$input,
    'output=s' => \$output,
    'config=s' => \$config_path,
    'help'     => \$help,
) or usage(2);

usage(0) if $help;
usage(2) unless $input;
$output ||= 'perl/reports';
die "Input file does not exist: $input\n" unless -f $input;

$config_path ||= "$FindBin::Bin/../config/perl.json";
my $config = CS466::Config->load($config_path);
my $result = CS466::ReportGenerator->generate_reports(input => $input, output => $output, config => $config);
print "Wrote report files:\n";
print "  $result->{summary_csv}\n";
print "  $result->{security_csv}\n";
print "  $result->{report_txt}\n";
exit 0;

sub usage {
    my ($code) = @_;
    print "Usage: perl perl/bin/generate_report.pl --input backend.log --output perl/reports [--config perl/config/perl.json]\n";
    exit $code;
}
