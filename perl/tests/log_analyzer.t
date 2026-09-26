use strict;
use warnings;
use Test::More;
use FindBin;
use lib "$FindBin::Bin/../lib";
use CS466::LogAnalyzer;

my $analyzer = CS466::LogAnalyzer->new;
for my $i (1 .. 5) {
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
is($summary->{events}{LOGIN_FAILED}, 5, 'LOGIN_FAILED count');
is($summary->{events}{TICKET_CREATED}, 1, 'ticket event count');
is($summary->{levels}{WARNING}, 1, 'warning level count');
is(scalar @{ $summary->{security_events} }, 1, 'security detection');
is($summary->{security_events}[0]{event}, 'POSSIBLE_BRUTE_FORCE', 'security event type');
is($summary->{top_logger}{logger}, 'app.users.service', 'top logger');

done_testing;
