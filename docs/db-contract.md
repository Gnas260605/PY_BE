# DB Contract

Status: CURRENT BACKEND SCHEMA

Source of truth: `database/schema.sql`

## Tables

- `USERS`: accounts, bcrypt password hashes, role, status, notification preference.
- `DEVICES`: managed IT assets and current device status.
- `TICKETS`: helpdesk requests, lifecycle state, priority, category, creator, device, technician.
- `TICKET_HISTORY`: immutable ticket audit trail. Ticket delete is restricted to preserve history.
- `TICKET_COMMENTS`: ticket discussion messages.
- `TICKET_ATTACHMENTS`: uploaded attachment metadata; files live under the backend upload directory.

## Enum Alignment

Backend schemas must stay aligned with these database enum values:

- User roles: `USER`, `TECHNICIAN`, `ADMIN`
- User status: `ACTIVE`, `INACTIVE`
- Device status: `ACTIVE`, `MAINTENANCE`, `BROKEN`, `INACTIVE`
- Ticket category: `INCIDENT`, `SERVICE_REQUEST`, `MAINTENANCE`
- Ticket priority: `LOW`, `MEDIUM`, `HIGH`, `URGENT`
- Ticket status: `OPEN`, `ASSIGNED`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`
- Ticket history action: `CREATED`, `UPDATED`, `CLASSIFIED`, `ASSIGNED`, `STATUS_CHANGED`, `CLOSED`

## Integrity Rules

- Usernames are unique.
- Emails are unique when present.
- Device codes are unique.
- Ticket creator is required and uses `ON DELETE RESTRICT`.
- Ticket device can be deleted with `ON DELETE SET NULL`.
- Ticket technician can be deleted with `ON DELETE SET NULL`.
- Ticket history uses `ON DELETE RESTRICT` for tickets to preserve audit history.
- Comments and attachments cascade when the parent ticket is deleted.

## Notes

Do not change schema for backend-only work unless the database owner approves it. Keep `database/seed.sql` compatible with `database/schema.sql`.
