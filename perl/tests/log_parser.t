use strict;
use warnings;
use utf8;
use Test::More;
use FindBin;
use File::Temp qw(tempfile);
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

my $utf8 = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service USER_CREATED user_id=2 username="Nguyễn Văn Á" role=USER');
is($utf8->{metadata}{username}, 'Nguyễn Văn Á', 'quoted UTF-8 value with Vietnamese accents');

my $secret = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service LOGIN_FAILED username=admin password=123456 authorization="Bearer abc.def"');
is($secret->{metadata}{password}, '[REDACTED]', 'password redaction');
is($secret->{metadata}{authorization}, '[REDACTED]', 'token redaction');

my $token_fields = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service LOGIN_FAILED username=admin token=abc api_key="xyz"');
is($token_fields->{metadata}{token}, '[REDACTED]', 'generic token redaction');
is($token_fields->{metadata}{api_key}, '[REDACTED]', 'api_key redaction');

my $bearer_text = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.users.service LOGIN_FAILED username=admin message="Authorization: Bearer abc.def.ghi"');
is($bearer_text->{metadata}{message}, '[REDACTED]', 'Bearer token redaction inside non-sensitive field');
like($bearer_text->{message}, qr/Bearer \[REDACTED\]/, 'Bearer token redaction in raw message text');

my $new_event = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.auth.service PASSWORD_CHANGED user_id=1');
is($new_event->{event_type}, 'PASSWORD_CHANGED', 'backend new event is known');

my $unknown = $parser->parse_line('2026-09-26 08:10:12,421 INFO app.demo.service CUSTOM_EVENT foo=bar');
is($unknown->{event}, 'CUSTOM_EVENT', 'unknown event name preserved');
is($unknown->{event_type}, 'UNKNOWN', 'unknown event marked');

my $stats = $parser->stats;
ok($stats->{malformed} >= 1, 'malformed counter increments');
ok($stats->{unknown_event} >= 1, 'unknown event counter increments');

my ($fh, $filename) = tempfile(UNLINK => 1);
print {$fh} "2026-09-26 08:10:12,421 INFO app.core.websocket WEBSOCKET_CONNECTED user_id=1\n";
print {$fh} "bad mixed malformed line\n";
print {$fh} "2026-09-26 08:10:13,421 ERROR app.core.errors UNHANDLED_EXCEPTION path=/api/tickets\n";
print {$fh} "Traceback (most recent call last):\n";
print {$fh} "  File \"app/main.py\", line 1, in demo\n";
print {$fh} "ValueError: sample failure password=secret\n";
close $fh;

my $file_parser = CS466::LogParser->new;
my $events = $file_parser->parse_file($filename);
is(scalar @$events, 2, 'mixed malformed file keeps valid events');
is($file_parser->stats->{malformed}, 1, 'mixed malformed file counts bad line');
is($file_parser->stats->{continuation_lines}, 3, 'traceback continuation is not malformed');

done_testing;
