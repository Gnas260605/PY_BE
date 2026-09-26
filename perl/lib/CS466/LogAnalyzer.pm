package CS466::LogAnalyzer;

use strict;
use warnings;
use CS466::Config;
use CS466::LogParser;
use Time::Local qw(timelocal);

sub new {
    my ($class, %args) = @_;
    my $config = $args{config} || CS466::Config->defaults;
    return bless {
        config                => $config,
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
    my $threshold = int($self->{config}{brute_force_threshold} || 5);
    $threshold = 5 if $threshold < 1;
    my $window_seconds = int($self->{config}{brute_force_window_seconds} || 60);
    $window_seconds = 60 if $window_seconds < 1;
    my $event_epoch = _timestamp_epoch($event->{timestamp});
    return unless defined $event_epoch;
    $event->{_epoch} = $event_epoch;

    push @{ $self->{_failed_attempts}{$username} }, $event;
    my @recent = grep {
        defined $_->{_epoch} && ($event_epoch - $_->{_epoch}) <= $window_seconds
    } @{ $self->{_failed_attempts}{$username} };
    $self->{_failed_attempts}{$username} = \@recent;

    return unless @recent >= $threshold;
    my $window_start = $recent[0]->{_epoch};
    my $window_end = $event_epoch;

    my $already_reported = grep {
        $_->{username} eq $username
          && $_->{window_start_epoch} == $window_start
          && $_->{window_end_epoch} == $window_end
    } @{ $self->{security_events} };
    return if $already_reported;

    push @{ $self->{security_events} }, {
        timestamp          => $event->{timestamp},
        event              => 'POSSIBLE_BRUTE_FORCE',
        username           => $username,
        reason             => $threshold . '_or_more_login_failed_within_' . $window_seconds . '_seconds',
        window_start_epoch => $window_start,
        window_end_epoch   => $window_end,
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

sub _timestamp_epoch {
    my ($timestamp) = @_;
    my ($year, $mon, $day, $hour, $min, $sec) =
      $timestamp =~ /^(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2}),\d{3}$/;
    return unless defined $sec;
    return timelocal($sec, $min, $hour, $day, $mon - 1, $year);
}

1;
