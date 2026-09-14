## Purpose

Gives every GUI API meta-domain (destination, user, segment, etc.) a predictable, versioned single-record CRUD surface at `/v1/<domain-object>`, so clients can rely on one consistent URL and method shape per domain instead of the mixed `/v2/...`/unversioned paths in use today.

## ADDED Requirements

### Requirement: Canonical v1 CRUD routes per domain
For each of the 17 meta domains under `airembr_api/endpoint/gui/v1/routes/meta/` (bridge, canonical_entity, configuration, destination, embedding_setting, entity_object, ontology, payload_mapping, reshaping_schema, resource, segment, source, task, timer, user, user_account, validator), the system SHALL expose, in addition to any existing legacy route(s), a canonical route at `/v1/<domain-object>` using the domain's kebab-case folder name, where:
- `GET /v1/<domain-object>/{id}` returns the record or a 404-equivalent absence result, identical to the existing legacy GET behavior for that domain.
- `POST /v1/<domain-object>` creates or upserts a record, identical to the existing legacy POST/create behavior for that domain.
- `DELETE /v1/<domain-object>/{id}` deletes the record, identical to the existing legacy DELETE behavior for that domain.
A domain SHALL only expose the verbs it already exposes today (e.g. `task` and `timer` do not gain a verb they don't already have).

#### Scenario: Canonical GET matches legacy GET
- **WHEN** a client calls `GET /v1/destination/{destination_id}` for an existing destination
- **THEN** the response body and status code are identical to calling the existing legacy `GET /destination/{destination_id}`

#### Scenario: Canonical POST matches legacy POST
- **WHEN** a client calls `POST /v1/destination` with a valid destination payload
- **THEN** the record is created/updated exactly as it would be via the existing legacy `POST /v2/destination`

#### Scenario: Canonical DELETE matches legacy DELETE
- **WHEN** a client calls `DELETE /v1/segment/{segment_id}` for an existing segment
- **THEN** the segment is deleted exactly as it would be via the existing legacy `DELETE /segment/{segment_id}`

### Requirement: Create and update stay distinct where they already are
Where a domain already implements create and edit-by-id as two separate operations (currently only `user`: create has no id in the path, edit takes `{id}`), the canonical v1 surface SHALL preserve that same two-operation shape as `POST /v1/user` (create) and `POST /v1/user/{id}` (edit-by-id). No PATCH method is introduced by this change; POST remains the only write verb for both creation and update-by-id, matching current behavior.

#### Scenario: User create and edit remain separate v1 operations
- **WHEN** a client calls `POST /v1/user` without an id to create a user, and separately calls `POST /v1/user/{id}` to edit an existing user
- **THEN** each behaves identically to the existing legacy `POST /user` and `POST /user/{id}` respectively, and no `PATCH /v1/user` or `PATCH /v1/user/{id}` route exists

### Requirement: Self-scoped sub-resources get their own flat v1 path
Sub-resources whose handlers resolve their parent from authentication context or from a self-sufficient id rather than a parent-id path parameter (currently: user preference, canonical entity property GET/DELETE) SHALL be exposed as their own flat `/v1/<sub-resource>` path rather than nested under a parent id, since nesting would require a path parameter the handler does not accept.

#### Scenario: User preference is a flat v1 path
- **WHEN** a client calls `GET /v1/user-preference/{key}` for the authenticated user
- **THEN** the response is identical to calling the existing legacy `GET /user/preference/{key}`

#### Scenario: Canonical entity property nests only where the handler accepts the parent id
- **WHEN** a client calls `POST /v1/canonical-entity/{entity_id}/property` (whose legacy handler already accepts `entity_id`)
- **THEN** the property is saved identically to the existing legacy `POST /v2/canonical/entity/{entity_id}/property`
- **WHEN** a client calls `GET /v1/canonical-entity-property/{id}` or `DELETE /v1/canonical-entity-property/{id}` (whose legacy handlers take only the property id)
- **THEN** the response is identical to the existing legacy `GET`/`DELETE /v2/canonical/entity/property/{id}`

### Requirement: Legacy routes remain fully functional
All existing routes on every affected domain (whether versioned `/v2/...` or unversioned) SHALL continue to exist, accept requests, and behave exactly as before this change. No legacy route is removed, renamed, or altered in request/response shape as part of adding the canonical v1 routes.

#### Scenario: Legacy destination routes still work after v1 is added
- **WHEN** a client calls the existing legacy `GET /destination/{destination_id}`, `POST /v2/destination`, or `DELETE /destination/{destination_id}`
- **THEN** each responds exactly as it did before the canonical `/v1/destination` routes were added
