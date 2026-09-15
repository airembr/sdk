## MODIFIED Requirements

### Requirement: Legacy routes remain fully functional
Legacy routes remain fully functional except where explicitly retired below. For the 13 domains where the console (the only known caller) has been migrated to the canonical `/v1/<domain-object>` path — `bridge`, `configuration`, `destination`, `embedding_setting`, `entity_object`, `segment`, `source`, `timer`, `user` (create/get/edit/delete), `user_account`, `validator`, `payload_mapping`, `reshaping_schema`, `resource` — the legacy route(s) for that domain SHALL be removed once the migration is verified, and only the canonical `/v1/...` route SHALL remain. For every other domain or sub-resource not in that list — `canonical_entity` (including its property sub-resource), `ontology`, the `user` preference sub-resource, and `task` — all existing legacy routes SHALL continue to exist, accept requests, and behave exactly as before, unchanged by this requirement.

#### Scenario: Retired legacy destination routes no longer respond
- **WHEN** a client calls the former legacy `GET /destination/{destination_id}`, `POST /v2/destination`, or `DELETE /destination/{destination_id}` after this change ships
- **THEN** the server returns a 404-equivalent not-found response, since only `/v1/destination` remains

#### Scenario: Canonical v1 destination routes remain the sole way to reach the domain
- **WHEN** a client calls `GET /v1/destination/{destination_id}`, `POST /v1/destination`, or `DELETE /v1/destination/{destination_id}` after this change ships
- **THEN** each behaves exactly as the retired legacy route did before removal

#### Scenario: Untouched domains keep both routes
- **WHEN** a client calls the existing legacy `GET /v2/ontology/{id}`, `POST /v2/ontology`, or `DELETE /v2/ontology/{id}` after this change ships
- **THEN** each responds exactly as it did before this change, since `ontology` is not one of the 13 migrated domains

#### Scenario: Legacy destination routes still work after v1 is added
- **WHEN** a client calls the existing legacy `GET /destination/{destination_id}`, `POST /v2/destination`, or `DELETE /destination/{destination_id}` before the destination-domain legacy removal step of this change has been applied
- **THEN** each responds exactly as it did before the canonical `/v1/destination` routes were added — this scenario stops holding once `destination`'s legacy decorators are removed, per the "Retired legacy destination routes no longer respond" scenario above
