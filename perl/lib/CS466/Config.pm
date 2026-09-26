package CS466::Config;

use strict;
use warnings;

sub defaults {
    return {
        brute_force_threshold => 5,
        brute_force_window    => 'same_minute',
        output_dir            => 'perl/output',
        reports_dir           => 'perl/reports',
    };
}

1;
