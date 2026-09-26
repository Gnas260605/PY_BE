use strict;
use warnings;
use Test::More;
use FindBin;
use File::Temp qw(tempdir);
use File::Spec;
use lib "$FindBin::Bin/../lib";
use CS466::ReportGenerator;

my $tmp = tempdir(CLEANUP => 1);
my $log = File::Spec->catfile($tmp, 'backend.log');
open my $fh, '>:encoding(UTF-8)', $log or die $!;
print {$fh} "2026-09-26 08:00:00,001 INFO app.users.service LOGIN_SUCCESS user_id=1 username=admin role=ADMIN\n";
print {$fh} "2026-09-26 08:00:01,001 INFO app.users.service USER_CREATED user_id=2 username=\"nguyen, van a\" role=USER\n";
print {$fh} "2026-09-26 08:00:02,001 INFO app.tickets.service TICKET_CREATED ticket_id=42 user_id=2\n";
print {$fh} "2026-09-26 08:00:03,001 ERROR app.core.errors UNHANDLED_EXCEPTION path=/api/tickets\n";
print {$fh} "Traceback (most recent call last):\n";
print {$fh} "  File \"demo.py\", line 1, in <module>\n";
close $fh;

my $csv = File::Spec->catfile($tmp, 'logs.csv');
my $stats = CS466::ReportGenerator->export_logs_csv(input => $log, output => $csv);
ok(-f $csv, 'CSV generation');
is($stats->{parsed}, 4, 'CSV parsed count');
is($stats->{continuation_lines}, 2, 'CSV export tracks traceback continuation');

open my $csv_fh, '<:encoding(UTF-8)', $csv or die $!;
my $content = do { local $/; <$csv_fh> };
close $csv_fh;
like($content, qr/timestamp,level,logger,event/, 'CSV header');
like($content, qr/"nguyen, van a"/, 'CSV escaping');

my $empty = File::Spec->catfile($tmp, 'empty.log');
open my $empty_fh, '>:encoding(UTF-8)', $empty or die $!;
close $empty_fh;
my $empty_stats = CS466::ReportGenerator->export_logs_csv(input => $empty, output => File::Spec->catfile($tmp, 'empty.csv'));
is($empty_stats->{parsed}, 0, 'empty file');

my $report_dir = File::Spec->catdir($tmp, 'reports');
my $result = CS466::ReportGenerator->generate_reports(input => $log, output => $report_dir);
ok(-f $result->{summary_csv}, 'summary report exists');
ok(-f $result->{security_csv}, 'security report exists');
ok(-f $result->{report_txt}, 'text report exists');

done_testing;
