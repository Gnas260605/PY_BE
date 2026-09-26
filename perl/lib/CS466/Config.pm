package CS466::Config;

use strict;
use warnings;
use JSON::PP qw(decode_json);

sub defaults {
    return {
        brute_force_threshold => 5,
        brute_force_window    => 'same_minute',
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
        $config->{$key} = $loaded->{$key};
    }
    return $config;
}

1;
