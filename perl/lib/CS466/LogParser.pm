package CS466::LogParser;

use strict;
use warnings;
use Encode qw(decode);
use CS466::Security;

my %KNOWN_EVENTS = map { $_ => 1 } qw(
  LOGIN_SUCCESS
  LOGIN_FAILED
  USER_CREATED
  USER_UPDATED
  USER_STATUS_CHANGED
  DEVICE_CREATED
  DEVICE_UPDATED
  TICKET_CREATED
  TICKET_UPDATED
  TICKET_CLASSIFIED
  TICKET_ASSIGNED
  TICKET_STATUS_CHANGED
  TICKET_CLOSED
  PASSWORD_CHANGED
  TICKET_BATCH_ASSIGNED
  TICKET_BATCH_STATUS_CHANGED
  TICKET_COMMENT_CREATED
  WEBSOCKET_CONNECTED
  WEBSOCKET_DISCONNECTED
  WEBSOCKET_SEND_FAILED
  WEBSOCKET_BROADCAST_FAILED
  TELEGRAM_CONFIG_MISSING
  TELEGRAM_NOTIFICATION_SENT
  TELEGRAM_NOTIFICATION_FAILED
  SMTP_CONFIG_MISSING
  EMAIL_NOTIFICATION_SENT
  EMAIL_NOTIFICATION_FAILED
  UNHANDLED_DB_EXCEPTION
  UNHANDLED_EXCEPTION
  HEALTH_CHECK
);

sub new {
    my ($class) = @_;
    return bless {
        last_event => undef,
        stats => {
            parsed             => 0,
            malformed          => 0,
            continuation_lines => 0,
            unknown_event      => 0,
            total_lines        => 0,
        },
    }, $class;
}

sub stats {
    my ($self) = @_;
    return { %{ $self->{stats} } };
}

sub parse_file {
    my ($self, $path, $callback) = @_;
    open my $fh, '<:encoding(UTF-8)', $path or die "Cannot open input file '$path': $!";

    my @events;
    while (my $line = <$fh>) {
        my $event = $self->parse_line($line);
        next unless $event;
        if ($callback) {
            $callback->($event);
        }
        else {
            push @events, $event;
        }
    }
    close $fh;
    return \@events;
}

sub parse_line {
    my ($self, $line) = @_;
    $self->{stats}{total_lines}++;

    return if !defined $line || $line =~ /^\s*$/;
    chomp $line;
    $line =~ s/\r$//;
    $line = decode('UTF-8', $line, 1) unless Encode::is_utf8($line);

    my ($timestamp, $level, $logger, $message) =
      $line =~ /^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+([A-Z]+)\s+(\S+)\s+(.+)$/;

    if (!defined $message) {
        if (_is_continuation_line($line, $self->{last_event})) {
            $self->{stats}{continuation_lines}++;
            return;
        }
        $self->{stats}{malformed}++;
        return;
    }

    my ($event, $rest) = split /\s+/, $message, 2;
    if (!defined $event || $event !~ /^[A-Z][A-Z0-9_]*$/) {
        $self->{stats}{malformed}++;
        return;
    }

    my $metadata = _parse_metadata($rest || q{});
    $metadata = CS466::Security::redact_metadata($metadata);
    my $safe_message = CS466::Security::redact_text($rest || q{});

    my $event_type = exists $KNOWN_EVENTS{$event} ? $event : 'UNKNOWN';
    $self->{stats}{unknown_event}++ if $event_type eq 'UNKNOWN';
    $self->{stats}{parsed}++;

    my $parsed_event = {
        timestamp  => $timestamp,
        level      => $level,
        logger     => $logger,
        event      => $event,
        event_type => $event_type,
        metadata   => $metadata,
        message    => $safe_message,
    };
    $self->{last_event} = $parsed_event;
    return $parsed_event;
}

sub _parse_metadata {
    my ($text) = @_;
    my %metadata;

    while ($text =~ /(\w+)=("([^"]*)"|'([^']*)'|(\S+))/g) {
        my $key = $1;
        my $raw = defined $3 ? $3 : defined $4 ? $4 : $5;
        $metadata{$key} = _coerce_value($raw);
    }

    return \%metadata;
}

sub _coerce_value {
    my ($value) = @_;
    return $value unless defined $value;
    return int($value) if $value =~ /^-?\d+$/;
    return $value;
}

sub _is_continuation_line {
    my ($line, $last_event) = @_;
    return 0 unless defined $line && defined $last_event;
    return 0 unless ($last_event->{event} || q{}) =~ /(?:EXCEPTION|FAILED)$/ || ($last_event->{level} || q{}) =~ /^(ERROR|CRITICAL)$/;

    return 1 if $line =~ /^\s+/;
    return 1 if $line =~ /^Traceback \(most recent call last\):/;
    return 1 if $line =~ /^During handling of the above exception/;
    return 1 if $line =~ /^[A-Za-z_][A-Za-z0-9_.]*(Error|Exception|Warning):/;
    return 0;
}

1;
