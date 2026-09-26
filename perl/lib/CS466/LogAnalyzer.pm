package CS466::LogAnalyzer;

use strict;
use warnings;
use CS466::LogParser;

sub new {
    my ($class) = @_;
    return bless {
        total_logs            => 0,
        events                => {},
        levels                => { map { $_ => 0 } qw(DEBUG INFO WARNING ERROR CRITICAL) },
        loggers               => {},
        failed_login_users    => {},
        failed_login_timeline => {},
        security_events       => [],
        _failed_attempts      => {},
    }, $class;
}

sub analyze_file {
    my ($self, $path) = @_;
    my $parser = CS466::LogParser->new;
    $parser->parse_file($path, sub { $self->add_event($_[0]) });
    $self->{parser_stats} = $parser->stats;
    return $self->summary;
}

sub add_event {
    my ($self, $event) = @_;
    return unless $event;

    $self->{total_logs}++;
    $self->{events}{ $event->{event} }++;
    $self->{levels}{ $event->{level} }++;
    $self->{loggers}{ $event->{logger} }++;

    if ($event->{event} eq 'LOGIN_FAILED') {
        my $username = $event->{metadata}{username} || 'unknown';
        $self->{failed_login_users}{$username}++;
        my $minute = substr($event->{timestamp}, 0, 16);
        $self->{failed_login_timeline}{$minute}++;
        $self->_record_failed_login($event, $username);
    }
}

sub summary {
    my ($self) = @_;
    return {
        total_logs            => $self->{total_logs},
        events                => { %{ $self->{events} } },
        levels                => { %{ $self->{levels} } },
        loggers               => { %{ $self->{loggers} } },
        failed_login_users    => { %{ $self->{failed_login_users} } },
        failed_login_timeline => { %{ $self->{failed_login_timeline} } },
        security_events       => [ @{ $self->{security_events} } ],
        parser_stats          => $self->{parser_stats} || {},
        top_logger            => $self->_top_logger,
    };
}

sub _record_failed_login {
    my ($self, $event, $username) = @_;
    push @{ $self->{_failed_attempts}{$username} }, $event;
    my @recent = @{ $self->{_failed_attempts}{$username} };
    @recent = @recent > 5 ? @recent[-5 .. -1] : @recent;
    $self->{_failed_attempts}{$username} = \@recent;

    return unless @recent >= 5;
    my $bucket = substr($event->{timestamp}, 0, 16);
    my $same_bucket = grep { substr($_->{timestamp}, 0, 16) eq $bucket } @recent;
    return unless $same_bucket >= 5;

    my $already_reported = grep {
        $_->{username} eq $username && substr($_->{timestamp}, 0, 16) eq $bucket
    } @{ $self->{security_events} };
    return if $already_reported;

    push @{ $self->{security_events} }, {
        timestamp => $event->{timestamp},
        event     => 'POSSIBLE_BRUTE_FORCE',
        username  => $username,
        reason    => '5_or_more_login_failed_in_same_minute',
    };
}

sub _top_logger {
    my ($self) = @_;
    my ($top, $count) = ('', 0);
    for my $logger (keys %{ $self->{loggers} }) {
        if ($self->{loggers}{$logger} > $count) {
            ($top, $count) = ($logger, $self->{loggers}{$logger});
        }
    }
    return { logger => $top, count => $count };
}

1;
