# Architecture

```text
NiceGUI Frontend
        |
        | HTTP / WebSocket
        v
FastAPI Backend
        |
        v
MySQL

FastAPI Backend
        |
        v
Structured Logs
        |
        v
Perl Log Analytics
        |
        v
CSV / Summary / Security Reports
```

## Current Modules

- Backend: auth, users, devices, tickets, reports, health, notifications, WebSocket, core config/security/errors/logging, DB access.
- Frontend: NiceGUI app with role-specific USER, TECHNICIAN, and ADMIN views.
- Database: MySQL schema and seed data.
- Perl: backend log parser, analyzer, redaction, CSV export, security report.
- Tests: pytest API/integration tests, role-based smoke runner, Perl `Test::More` tests.

## Design Constraints

- Keep FastAPI, MySQL, NiceGUI, and Perl in their current roles.
- Backend remains the source of truth for RBAC, IDOR protection, ticket lifecycle, and attachment permissions.
- Frontend role guards are UX helpers only.
- Python reports are business reports; Perl reports are log analytics reports.
