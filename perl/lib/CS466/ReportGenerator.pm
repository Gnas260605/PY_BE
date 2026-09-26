package CS466::ReportGenerator;

use strict;
use warnings;
use File::Path qw(make_path);
use File::Spec;
use CS466::Config;
use CS466::LogAnalyzer;
use CS466::LogParser;

my @LOG_COLUMNS = qw(timestamp level logger event user_id ticket_id device_id username role status message);

sub csv_escape {
    my ($value) = @_;
    $value = '' unless defined $value;
    $value =~ s/"/""/g;
    return qq{"$value"} if $value =~ /[",\r\n]/;
    return $value;
}

sub write_csv_row {
    my ($fh, $row) = @_;
    print {$fh} join(',', map { csv_escape($_) } @$row), "\n";
}

sub export_logs_csv {
    my ($class, %args) = @_;
    my $input  = $args{input}  or die "input is required";
    my $output = $args{output} or die "output is required";

    _ensure_parent_dir($output);
    open my $out, '>:encoding(UTF-8)', $output or die "Cannot write output file '$output': $!";
    write_csv_row($out, \@LOG_COLUMNS);

    my $parser = CS466::LogParser->new;
    $parser->parse_file($input, sub {
        my ($event) = @_;
        my $meta = $event->{metadata} || {};
        write_csv_row($out, [
            $event->{timestamp},
            $event->{level},
            $event->{logger},
            $event->{event},
            $meta->{user_id},
            $meta->{ticket_id},
            $meta->{device_id},
            $meta->{username},
            $meta->{role},
            $meta->{status} || $meta->{new},
            $event->{message},
        ]);
    });
    close $out;
    return $parser->stats;
}

sub generate_reports {
    my ($class, %args) = @_;
    my $input      = $args{input} or die "input is required";
    my $output_dir = $args{output} || 'perl/reports';
    my $config     = $args{config} || CS466::Config->defaults;

    make_path($output_dir) unless -d $output_dir;
    my $analyzer = CS466::LogAnalyzer->new(config => $config);
    my $summary = $analyzer->analyze_file($input);

    my $summary_path = File::Spec->catfile($output_dir, 'summary.csv');
    open my $summary_fh, '>:encoding(UTF-8)', $summary_path or die "Cannot write '$summary_path': $!";
    write_csv_row($summary_fh, [qw(metric value)]);
    for my $pair (
        ['total_logs',     $summary->{total_logs}],
        ['login_success',  $summary->{events}{LOGIN_SUCCESS} || 0],
        ['login_failed',   $summary->{events}{LOGIN_FAILED} || 0],
        ['ticket_created', $summary->{events}{TICKET_CREATED} || 0],
        ['ticket_closed',  $summary->{events}{TICKET_CLOSED} || 0],
        ['warning',        $summary->{levels}{WARNING} || 0],
        ['error',          $summary->{levels}{ERROR} || 0],
      )
    {
        write_csv_row($summary_fh, $pair);
    }
    close $summary_fh;

    my $security_path = File::Spec->catfile($output_dir, 'security_events.csv');
    open my $security_fh, '>:encoding(UTF-8)', $security_path or die "Cannot write '$security_path': $!";
    write_csv_row($security_fh, [qw(timestamp event username reason)]);
    for my $event (@{ $summary->{security_events} }) {
        write_csv_row($security_fh, [
            $event->{timestamp},
            $event->{event},
            $event->{username},
            $event->{reason},
        ]);
    }
    close $security_fh;

    my $text_path = File::Spec->catfile($output_dir, 'report.txt');
    open my $text_fh, '>:encoding(UTF-8)', $text_path or die "Cannot write '$text_path': $!";
    print {$text_fh} _format_console_summary($summary);
    close $text_fh;

    return {
        summary         => $summary,
        summary_csv     => $summary_path,
        security_csv    => $security_path,
        report_txt      => $text_path,
    };
}

sub format_console_summary {
    my ($class, $summary) = @_;
    return _format_console_summary($summary);
}

sub _format_console_summary {
    my ($summary) = @_;
    my $events = $summary->{events} || {};
    my $levels = $summary->{levels} || {};
    my $security_count = scalar @{ $summary->{security_events} || [] };

    return join('', (
        "=== CS466 HELP DESK LOG ANALYSIS ===\n\n",
        "Total logs: " . ($summary->{total_logs} || 0) . "\n\n",
        "LOGIN\n",
        "Success: " . ($events->{LOGIN_SUCCESS} || 0) . "\n",
        "Failed: " . ($events->{LOGIN_FAILED} || 0) . "\n\n",
        "TICKETS\n",
        "Created: " . ($events->{TICKET_CREATED} || 0) . "\n",
        "Assigned: " . ($events->{TICKET_ASSIGNED} || 0) . "\n",
        "Closed: " . ($events->{TICKET_CLOSED} || 0) . "\n\n",
        "ERRORS\n",
        "WARNING: " . ($levels->{WARNING} || 0) . "\n",
        "ERROR: " . ($levels->{ERROR} || 0) . "\n",
        "CRITICAL: " . ($levels->{CRITICAL} || 0) . "\n\n",
        "SECURITY\n",
        "Possible brute-force: $security_count\n",
    ));
}

sub _ensure_parent_dir {
    my ($path) = @_;
    my (undef, $dir) = File::Spec->splitpath($path);
    make_path($dir) if $dir && !-d $dir;
}

1;
