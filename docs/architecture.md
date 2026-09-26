# Architecture

```text
Frontend -> HTTP/JSON -> Backend Python REST API -> MySQL
Log/Data -> Perl -> CSV/Reports
```

## Sprint 1 decisions

- Backend framework: FastAPI
- Contract state: current backend implements auth, users, devices, tickets, reports, health, and notification support.
- Ownership split follows `Promt/00_MASTER_PROMPT.md`
