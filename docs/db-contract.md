# DB Contract

Status: DRAFT

Source of truth: `database/schema.sql`

## Locked now

- Entity baseline only:
  - `USERS`
  - `DEVICES`
  - `TICKETS`
  - `TICKET_HISTORY`

## Not locked yet

- Table columns
- Primary/foreign keys
- Auth-related fields
- Device status values
- Ticket writable fields

## Blocking notes

- Backend auth implementation is blocked until auth fields exist in schema.
- Ticket/device persistence must not be implemented before concrete columns are approved.

