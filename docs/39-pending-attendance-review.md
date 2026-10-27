# Pending attendance review workflow

1. Open **Pending Attendance Review**, separate from Verified Attendance. Inspect the exact source alias, native sheet, row/column, raw sanitized mark/header, date warning and candidate UUIDs.
2. Treat PROVISIONAL_MATCH as a suggestion, AMBIGUOUS as multiple candidates and UNMATCHED as no supported match. Repeated names or a single name candidate are never enough to approve identity. DATE_PENDING and CODE_PENDING can coexist with any identity state.
3. Record review notes and the reference to authoritative evidence. Resolve identities only using verified identifiers or an independently approved exact crosswalk; resolve dates only after fidelity/calendar evidence; approve attendance-code meanings separately. Do not require these decisions merely to preserve pending evidence.
4. Keep the import-time source evidence unchanged. A separately approved review/backend API can record decisions and produce an operational projection with its original source-record/cell provenance. Import flags are historical evidence, not permission to rewrite source values. Current staging only permits privileged review notes/status changes; it does not activate a general-user resolution API.
5. Show operational attendance in **Verified Attendance** only when its identity/date/code evidence passes and `review_state='accepted'`. Verified identity alone does not make a pending source observation approved attendance. Reject/exclude notes do not delete original evidence.

The frontend scaffold uses **synthetic fixtures only** until the staging migration/import, Google OAuth and role/private-data permissions are separately approved. Its review actions change demo memory only. It cannot promote a name-only candidate or write to the live database. Public/Member access to private staging remains denied.

Metrics must distinguish roster rows, nonempty source cells, formula/summary values and source contexts. Do not show the 43,160 planned staging records as 43,160 sessions or use unverified dates in chronological attendance reporting. No actual remote attendance deployment has been performed by this preparation task.
