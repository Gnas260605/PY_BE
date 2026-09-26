package CS466::Security;

use strict;
use warnings;

our @SENSITIVE_FIELDS = qw(
  password
  password_hash
  authorization
  access_token
  refresh_token
  jwt
  jwt_secret
  secret
);

sub is_sensitive_key {
    my ($key) = @_;
    return 0 unless defined $key;
    my $normalized = lc $key;
    for my $field (@SENSITIVE_FIELDS) {
        return 1 if $normalized eq $field;
    }
    return 0;
}

sub redact_value {
    my ($key, $value) = @_;
    return '[REDACTED]' if is_sensitive_key($key);
    return '[REDACTED]' if defined $value && $value =~ /\bBearer\s+[A-Za-z0-9._~+\/=-]+/i;
    return $value;
}

sub redact_metadata {
    my ($metadata) = @_;
    my %redacted;
    for my $key (keys %{ $metadata || {} }) {
        $redacted{$key} = redact_value($key, $metadata->{$key});
    }
    return \%redacted;
}

sub redact_text {
    my ($text) = @_;
    return $text unless defined $text;

    my $result = $text;
    $result =~ s/\b(Bearer)\s+[A-Za-z0-9._~+\/=-]+/$1 [REDACTED]/gi;
    for my $field (@SENSITIVE_FIELDS) {
        $result =~ s/\b($field)=("[^"]*"|'[^']*'|\S+)/$1=[REDACTED]/gi;
    }
    return $result;
}

1;
