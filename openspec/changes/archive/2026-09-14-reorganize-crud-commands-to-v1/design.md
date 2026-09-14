## Context

`airembr_api/endpoint/gui/v1/routes/{meta,data}/<domain>/crud_endpoint.py` files each import a small number of CRUD functions from `airembr/system/command/<domain>/<file>.py`. Most of those source files also contain non-CRUD functions (list/meta/histogram helpers) used only by the still-active legacy (pre-v1) endpoints under `airembr_api/endpoint/gui/routes/...`. 15 of the 24 command files being moved are imported by both a `gui/v1` crud_endpoint and a legacy endpoint; the rest (`task`, `timer`, and most of `user`'s per-function files) are already CRUD-only files used solely by the v1 endpoint. See proposal.md for the full per-file move list and the "Why".

Router registration is explicit and manual in `airembr_api/endpoint/gui/main.py` (no auto-discovery), so this change does not touch route registration — only the `from ...` import lines that resolve to the moved files.

## Goals / Non-Goals

**Goals:**
- Relocate the 29 listed files verbatim (byte-for-byte function bodies) into `airembr/system/command/v1/{meta,data}/<domain>/` and `airembr/system/command/v1/errors/`.
- Update every import statement that resolves to a moved file — in both `gui/v1` crud endpoints and legacy `gui/routes` endpoints — so nothing breaks at import time.
- Establish the `meta`/`data` + per-domain folder convention under `command/v1/` as the pattern later work (organizing non-CRUD "operations" commands) will extend.

**Non-Goals:**
- Splitting mixed CRUD/non-CRUD files. Files containing non-CRUD functions move in full; those non-CRUD functions are not relocated to an `operations.py` in this change.
- Renaming or refactoring any function, class, or variable inside a moved file.
- Changing route paths, request/response schemas, or endpoint behavior.
- Removing or consolidating the legacy (pre-v1) endpoints.

## Decisions

**Whole-file moves, not function-level splits.** The user explicitly requires file contents to stay unchanged. Files that mix CRUD and non-CRUD functions (e.g. `bridge/bridge.py`, `destination/destination.py`) move as complete units to their new `v1` domain folder; splitting is deferred to the future "operations" reorganization.

**Command folder names mirror the endpoint's domain names, not the old command names.** Four domains are renamed on the move to match `gui/v1/routes/meta/<domain>/`: `event_mapping` → `payload_mapping`, `event_reshaping` → `reshaping_schema`, `event_source` → `source`. The `user` command folder splits across two target folders (`user/` and `user_account/`) to match the two separate endpoint domains, based on which crud_endpoint each source file is actually imported by.

**Shared `command/v1/errors/` folder for all 5 domain error modules**, not just the one (`user/errors.py`) that is genuinely shared across two moving domains. Chosen for consistency — one place to look for command-layer exceptions — over keeping the 4 single-domain error files next to their crud file. Each file is renamed `<domain>_errors.py` to stay unambiguous in a flat folder (plain `errors.py` would collide across domains).

**New `v1` subpackages get an `__init__.py`** (empty, matching the existing convention seen in `command/v1/`, `endpoint/gui/v1/routes/*/__init__.py`, etc.) so each new folder is an importable Python package.

**Old files are deleted after the move, not left as re-export shims.** A shim (`from ..v1.meta.bridge.bridge import *`) would satisfy any importer missed by this change, but it hides the mistake instead of surfacing an ImportError at startup/import time, and it contradicts "content should not be changed" by adding new content to the old location. A clean move-and-fix-imports is preferred; the importer inventory below is built from an exhaustive grep specifically to make missed-importer risk low.

## Migration Plan

1. Create the new directory tree under `airembr/system/command/v1/` (`meta/<domain>/`, `data/<domain>/`, `errors/`) with `__init__.py` in every new package directory.
2. Move each of the 29 files (`git mv`) to its target path per the proposal's move list.
3. For each moved file, update its internal relative imports if any reference sibling files that also moved (e.g. a domain's `configuration.py` importing its own `errors.py` — the relative import target moves too, so the import path changes even though the code is otherwise untouched).
4. Update the one import line in each affected `gui/v1/.../crud_endpoint.py`.
5. Update the one import line in each affected legacy `gui/routes/...` endpoint file.
6. Grep the repo for any remaining reference to the old module paths to catch importers outside the two endpoint trees (tests, scripts, other command files).
7. Boot the GUI API app (or run its import-time test/lint) to confirm no `ImportError`/`ModuleNotFoundError` remains.

No feature flag or staged rollout is needed — this is a file move plus import fixes with identical runtime behavior; rollback is `git revert` of the commit.

## Risks / Trade-offs

- **[Risk]** A caller of a moved file outside the two endpoint trees (e.g. a test, a script, another command module) is missed → import breaks at runtime instead of at review time.
  **Mitigation**: step 6's exhaustive grep across the whole repo (not just `airembr_api/`) before considering the move done.
- **[Risk]** A moved file has an internal relative import to a sibling in the same old folder that is *not* moving (e.g. a CRUD file importing a list-only helper still left behind) → after the move the relative import breaks.
  **Mitigation**: inspect each moved file's own imports during the move, not just its external importers; fix any reference to a non-moving sibling to use the old, still-valid absolute path.
- **[Trade-off]** Files with non-CRUD functions still bundled in (e.g. `bridge.py`) land in the `v1` "CRUD" tree containing functions the v1 layer doesn't use. Accepted per the proposal's explicit scope (whole-file move now, split later) rather than expanding this change into a content edit.
