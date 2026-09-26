package CS466::Config;

use strict;
use warnings;
use JSON::PP qw(decode_json);

sub defaults {
    return {
        brute_force_threshold => 5,
        brute_force_window_seconds => 60,
        output_dir            => 'perl/output',
        reports_dir           => 'perl/reports',
    };
}

sub load {
    my ($class, $path) = @_;
    my $config = defaults();
    return $config unless $path && -f $path;

    open my $fh, '<:encoding(UTF-8)', $path or die "Cannot open config file '$path': $!";
    my $json = do { local $/; <$fh> };
    close $fh;

    my $loaded = decode_json($json || '{}');
    for my $key (keys %$loaded) {
        next if $key eq 'brute_force_window';
        $config->{$key} = $loaded->{$key};
    }
    _validate($config);
    return $config;
}

sub _validate {
    my ($config) = @_;
    for my $key (qw(brute_force_threshold brute_force_window_seconds)) {
        die "Invalid config '$key': must be a positive integer"
          unless defined $config->{$key} && $config->{$key} =~ /^\d+$/ && int($config->{$key}) > 0;
        $config->{$key} = int($config->{$key});
    }
}

1;
