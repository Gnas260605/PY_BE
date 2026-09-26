use strict;
use warnings;
use Test::More;
use FindBin;
use lib "$FindBin::Bin/../lib";
use CS466::LogParser;

my $parser = CS466::LogParser->new;
my $event = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.auth.service LOGIN_SUCCESS user_id=1 username=admin role=ADMIN');

ok($event, 'parse valid line');
is($event->{event}, 'LOGIN_SUCCESS', 'event extraction');
is($event->{metadata}{user_id}, 1, 'numeric metadata extraction');
is($event->{metadata}{username}, 'admin', 'string metadata extraction');

my $bad = $parser->parse_line('this is not a valid backend log line');
ok(!defined $bad, 'parse invalid line returns undef');

my $utf8 = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service USER_CREATED user_id=2 username="nguyen van a" role=USER');
is($utf8->{metadata}{username}, 'nguyen van a', 'quoted UTF-8-safe value with spaces');

my $secret = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service LOGIN_FAILED username=admin password=123456 authorization="Bearer abc.def"');
is($secret->{metadata}{password}, '[REDACTED]', 'password redaction');
is($secret->{metadata}{authorization}, '[REDACTED]', 'token redaction');

my $unknown = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.demo.service CUSTOM_EVENT foo=bar');
is($unknown->{event}, 'CUSTOM_EVENT', 'unknown event name preserved');
is($unknown->{event_type}, 'UNKNOWN', 'unknown event marked');

my $stats = $parser->stats;
ok($stats->{malformed} >= 1, 'malformed counter increments');
ok($stats->{unknown_event} >= 1, 'unknown event counter increments');

done_testing;
