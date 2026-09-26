# CS466 Perl Log Analytics

This directory contains the Perl log analytics and reporting layer for the CS466 Helpdesk project.

## Role in the Architecture

Current system flow:

```text
Frontend -> HTTP/JSON -> Backend Python REST API -> MySQL
Log/Data -> Perl -> CSV/Reports
```

The backend keeps the existing Python logging format. Perl reads those backend logs, redacts sensitive data, exports normalized CSV rows, analyzes operational events, and generates summary/security reports.

## Requirements

- Perl 5
- Core Perl modules used by this implementation: `strict`, `warnings`, `Getopt::Long`, `FindBin`, `File::Path`, `File::Spec`, `File::Temp`, `Test::More`
- JSON config uses core module `JSON::PP`.
- No external CPAN dependency is required.

Check Perl version:

```powershell
perl -v
```

## Directory Layout

```text
perl/
  bin/
    parse_logs.pl
    analyze_logs.pl
    generate_report.pl
  lib/CS466/
    Config.pm
    LogAnalyzer.pm
    LogParser.pm
    ReportGenerator.pm
    Security.pm
  config/perl.json
  samples/backend_sample.log
  output/
  reports/
  tests/
```

## Backend Log Format

The parser expects the current backend format:

```text
TIMESTAMP LEVEL LOGGER EVENT key=value key=value ...
```

Example:

```text
2026-09-26 08:00:00,123 INFO app.tickets.service TICKET_CREATED ticket_id=42 user_id=8 priority=HIGH
```

Supported contract events:

- `LOGIN_SUCCESS`
- `LOGIN_FAILED`
- `PASSWORD_CHANGED`
- `USER_CREATED`
- `USER_UPDATED`
- `USER_STATUS_CHANGED`
- `DEVICE_CREATED`
- `DEVICE_UPDATED`
- `TICKET_CREATED`
- `TICKET_UPDATED`
- `TICKET_CLASSIFIED`
- `TICKET_ASSIGNED`
- `TICKET_STATUS_CHANGED`
- `TICKET_CLOSED`
- `TICKET_BATCH_ASSIGNED`
- `TICKET_BATCH_STATUS_CHANGED`
- `TICKET_COMMENT_CREATED`
- `WEBSOCKET_CONNECTED`
- `WEBSOCKET_DISCONNECTED`
- `WEBSOCKET_SEND_FAILED`
- `WEBSOCKET_BROADCAST_FAILED`
- `TELEGRAM_CONFIG_MISSING`
- `TELEGRAM_NOTIFICATION_SENT`
- `TELEGRAM_NOTIFICATION_FAILED`
- `SMTP_CONFIG_MISSING`
- `EMAIL_NOTIFICATION_SENT`
- `EMAIL_NOTIFICATION_FAILED`
- `UNHANDLED_DB_EXCEPTION`
- `UNHANDLED_EXCEPTION`

Unknown events are preserved and marked as `UNKNOWN` internally. Malformed lines are counted but do not crash the parser.

## Security Rules

These fields are redacted before CSV or reports are written:

- `password`
- `password_hash`
- `authorization`
- `access_token`
- `refresh_token`
- `jwt`
- `jwt_secret`
- `secret`

Bearer tokens are also redacted.

## Parse Logs to CSV

```powershell
perl perl/bin/parse_logs.pl `
  --input perl/samples/backend_sample.log `
  --output perl/output/logs.csv
```

CSV columns:

```text
timestamp,level,logger,event,user_id,ticket_id,device_id,username,role,status,message
```

## Analyze Logs

```powershell
perl perl/bin/analyze_logs.pl `
  --input perl/samples/backend_sample.log `
  --config perl/config/perl.json
```

Console output includes login counts, ticket counts, warning/error counts, and possible brute-force warnings.

`perl/config/perl.json` controls brute-force detection:

```json
{
  "brute_force_threshold": 5,
  "brute_force_window_seconds": 60,
  "output_dir": "perl/output",
  "reports_dir": "perl/reports"
}
```

Detection uses a rolling time window based on parsed timestamps, so attempts crossing a calendar minute boundary still count when they occur inside the configured number of seconds.

## Generate Reports

```powershell
perl perl/bin/generate_report.pl `
  --input perl/samples/backend_sample.log `
  --output perl/reports `
  --config perl/config/perl.json
```

Generated files:

- `summary.csv`
- `security_events.csv`
- `report.txt`

## Run Tests

```powershell
prove -Iperl/lib perl/tests
```

## Optional Backend File Logging

Backend console logging remains the default. To also write logs to a rotating file:

```powershell
$env:LOG_LEVEL = "INFO"
$env:LOG_TO_FILE = "true"
$env:LOG_FILE = "logs/backend.log"
```

Then run the FastAPI app as usual. File logs use a 10 MB rotation size and 5 backups.

## Troubleshooting

- If `perl` is not recognized, install Perl and ensure it is available in `PATH`.
- If an input file is missing, the CLI exits with a non-zero status.
- If CSV fields contain commas or quotes, the report generator escapes them.
- If logs contain malformed lines, check parser stats printed by `parse_logs.pl`, especially `malformed` and `continuation_lines`.
- If no security warnings appear, confirm the configured `brute_force_threshold` number of `LOGIN_FAILED` events for the same username occur inside `brute_force_window_seconds`.
