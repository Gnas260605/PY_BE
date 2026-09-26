use strict;
use warnings;
use Test::More;
use FindBin;
use File::Temp qw(tempfile);
use lib "$FindBin::Bin/../lib";
use CS466::Config;
use CS466::LogAnalyzer;

my ($config_fh, $config_file) = tempfile(UNLINK => 1);
print {$config_fh} '{"brute_force_threshold":3,"brute_force_window_seconds":60}';
close $config_fh;

my $config = CS466::Config->load($config_file);
is($config->{brute_force_threshold}, 3, 'loads brute-force threshold from JSON config');
is($config->{brute_force_window_seconds}, 60, 'loads brute-force window from JSON config');

my $analyzer = CS466::LogAnalyzer->new(config => $config);
for my $i (1 .. 3) {
    $analyzer->add_event({
        timestamp => "2026-09-26 08:00:0$i,001",
        level => 'INFO',
        logger => 'app.users.service',
        event => 'LOGIN_FAILED',
        metadata => { username => 'ghost' },
    });
}
$analyzer->add_event({
    timestamp => '2026-09-26 08:01:00,001',
    level => 'INFO',
    logger => 'app.users.service',
    event => 'LOGIN_SUCCESS',
    metadata => { username => 'admin' },
});
$analyzer->add_event({
    timestamp => '2026-09-26 08:02:00,001',
    level => 'INFO',
    logger => 'app.tickets.service',
    event => 'TICKET_CREATED',
    metadata => { ticket_id => 42 },
});
$analyzer->add_event({
    timestamp => '2026-09-26 08:03:00,001',
    level => 'WARNING',
    logger => 'app.tickets.service',
    event => 'TICKET_CLOSED',
    metadata => { ticket_id => 42 },
});

my $summary = $analyzer->summary;
is($summary->{events}{LOGIN_SUCCESS}, 1, 'LOGIN_SUCCESS count');
is($summary->{events}{LOGIN_FAILED}, 3, 'LOGIN_FAILED count');
is($summary->{events}{TICKET_CREATED}, 1, 'ticket event count');
is($summary->{levels}{WARNING}, 1, 'warning level count');
is(scalar @{ $summary->{security_events} }, 1, 'configurable security detection threshold');
is($summary->{security_events}[0]{event}, 'POSSIBLE_BRUTE_FORCE', 'security event type');
is($summary->{security_events}[0]{reason}, '3_or_more_login_failed_within_60_seconds', 'security reason uses configured threshold and window');
is($summary->{top_logger}{logger}, 'app.users.service', 'top logger');

my ($bad_fh, $bad_config_file) = tempfile(UNLINK => 1);
print {$bad_fh} '{"brute_force_threshold":0,"brute_force_window_seconds":60}';
close $bad_fh;
eval { CS466::Config->load($bad_config_file) };
like($@, qr/Invalid config/, 'invalid config is rejected');

my $window_analyzer = CS466::LogAnalyzer->new(config => {
    brute_force_threshold => 5,
    brute_force_window_seconds => 60,
});
for my $ts (
    '2026-09-26 08:00:50,001',
    '2026-09-26 08:00:55,001',
    '2026-09-26 08:00:59,001',
    '2026-09-26 08:01:03,001',
    '2026-09-26 08:01:08,001',
) {
    $window_analyzer->add_event({
        timestamp => $ts,
        level => 'INFO',
        logger => 'app.users.service',
        event => 'LOGIN_FAILED',
        metadata => { username => 'boundary' },
    });
}
my $window_summary = $window_analyzer->summary;
is(scalar @{ $window_summary->{security_events} }, 1, 'brute-force detection works across minute boundary');

done_testing;
