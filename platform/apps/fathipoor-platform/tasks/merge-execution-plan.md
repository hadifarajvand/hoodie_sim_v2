# Fathipoor Platform Merge Execution Plan

Status: planned-not-executed
Scope: execution planning only

## Purpose

This plan defines the future registry/documentation steps needed to merge `fathipoor-website` and `fathipoor-streamer` into the composite logical platform capsule `fathipoor-platform`.

This plan does not execute the merge.

## Approved Route Clarification

`appsm.fathipoor.abisanraya.com` is assigned to the `web` component for the proposed future merge.

## Source Contract

This execution plan follows:

```text
platform/apps/fathipoor-platform/tasks/merge-contract.md
```

## Future Files To Edit During Merge Execution

The future merge execution may edit only after separate approval:

```text
platform/control-plane/apps-registry.yml
platform/control-plane/domains-registry.yml
app-records/fathipoor-website/README.md
app-records/fathipoor-streamer/README.md
platform/apps/fathipoor-platform/README.md
platform/apps/fathipoor-platform/app-capsule.yml
docs/planning/manual-validation-pass-001.md
docs/planning/repo-validation-plan.md
```

No file outside this list should be changed during the merge execution unless separately approved.

## Proposed Step 1 — Add Parent Platform Registry Record

Add `fathipoor-platform` to `platform/control-plane/apps-registry.yml` as the parent composite record.

Proposed record shape:

```yaml
fathipoor-platform:
  workload_type: composite_web_and_streaming_platform
  status: adopted-production-composite
  readiness: registry-planning-only
  current_stamp: abisan-ir-01
  target_stamp: abisan-ir-01
  management_authority: abisan-ir-01
  future_management_authority: mgmt-ir-01
  legacy_aliases:
    - fathipoor-website
    - fathipoor-streamer
  components:
    - web
    - helpers
    - streamer
  domains:
    - fathipoor.abisanraya.com
    - appsm.fathipoor.abisanraya.com
```

Parent-level Taxonomy v3 should remain conservative and must not downgrade component risk:

```yaml
sensitivity_label: confidential
data_domain: mixed_or_unclassified
impact_rating:
  confidentiality: high
  integrity: high
  availability: high
access_scope: mixed_component_access
network_exposure: public_internet_direct
current_origin: iran_origin
distribution_policy: component_policy_required
hosting_model: self_hosted
routing_posture: iran_primary_public
cloudflare_mode: dns_only
```

## Proposed Step 2 — Convert Existing App Records To Legacy Aliases

Do not delete existing records.

Update `fathipoor-website` as a legacy alias/component reference:

```yaml
fathipoor-website:
  status: legacy-alias
  parent_app: fathipoor-platform
  component_refs:
    - web
    - helpers
```

Update `fathipoor-streamer` as a legacy alias/component reference:

```yaml
fathipoor-streamer:
  status: legacy-alias
  parent_app: fathipoor-platform
  component_refs:
    - streamer
```

Old records should keep enough information to make rollback easy.

## Proposed Step 3 — Preserve Component-Level Taxonomy v3

Component-level taxonomy remains authoritative where risks differ.

### web

```yaml
component: web
sensitivity_label: general
data_domain: operational_metadata
impact_rating:
  confidentiality: moderate
  integrity: high
  availability: high
access_scope: public_anonymous
network_exposure: public_internet_direct
current_origin: iran_origin
distribution_policy: metadata_only_replica_candidate
hosting_model: self_hosted
routing_posture: iran_primary_public
cloudflare_mode: dns_only
```

### helpers

```yaml
component: helpers
sensitivity_label: general
data_domain: operational_metadata
impact_rating:
  confidentiality: moderate
  integrity: high
  availability: high
access_scope: public_anonymous
network_exposure: public_internet_direct
current_origin: iran_origin
distribution_policy: metadata_only_replica_candidate
hosting_model: self_hosted
routing_posture: iran_primary_public
cloudflare_mode: dns_only
```

### streamer

```yaml
component: streamer
sensitivity_label: confidential
data_domain: client_runtime_data
impact_rating:
  confidentiality: high
  integrity: high
  availability: high
access_scope: client_tenant_scoped
network_exposure: public_internet_direct
current_origin: iran_origin
distribution_policy: no_replica_current
hosting_model: self_hosted
routing_posture: region_locked
cloudflare_mode: dns_only
```

## Proposed Step 4 — Update Domain Registry Mapping

Update Fathipoor domains in `platform/control-plane/domains-registry.yml` after separate execution approval.

Proposed future mapping:

```yaml
fathipoor.abisanraya.com:
  app: fathipoor-platform
  component: web

appsm.fathipoor.abisanraya.com:
  app: fathipoor-platform
  component: web
```

The approved decision is that `appsm.fathipoor.abisanraya.com` belongs to the `web` component.

No DNS, Cloudflare, Traefik, or live routing changes are approved by this mapping update. This is only a control-plane documentation registry change.

## Proposed Step 5 — Update App Record READMEs

Update old app-record files only after registry merge approval:

```text
app-records/fathipoor-website/README.md
app-records/fathipoor-streamer/README.md
```

Required README behavior:

- Mark each old record as a legacy alias/component reference.
- Point to `platform/apps/fathipoor-platform/`.
- Preserve old context for rollback.
- Do not delete old documentation.

## Proposed Step 6 — Update Fathipoor Platform Planning Shell

Update these after registry merge approval:

```text
platform/apps/fathipoor-platform/README.md
platform/apps/fathipoor-platform/app-capsule.yml
```

Required behavior:

- Mark the shell as the active composite planning record.
- Keep production non-change warnings.
- Keep component-level taxonomy controls.
- Keep merge-execution status recorded.

## Proposed Step 7 — Update Validation Documents

Update these after registry merge approval:

```text
docs/planning/manual-validation-pass-001.md
docs/planning/repo-validation-plan.md
```

Required behavior:

- Record merge execution status.
- Record changed files.
- Record validation result.
- Record remaining pending issues.

## Validation Checks After Merge Execution

After execution, validate:

- `fathipoor-platform` exists as parent app record.
- `fathipoor-website` is not deleted.
- `fathipoor-streamer` is not deleted.
- Old records point to `fathipoor-platform`.
- Parent record lists `web`, `helpers`, and `streamer`.
- `fathipoor.abisanraya.com` maps to `fathipoor-platform` component `web`.
- `appsm.fathipoor.abisanraya.com` maps to `fathipoor-platform` component `web`.
- Component-level taxonomy remains visible.
- Streamer remains `confidential / client_runtime_data`.
- No production/live-system fields were changed.
- No DNS/Cloudflare/Traefik behavior was changed.

## Rollback / Undo Plan

If the merge creates confusion or bad references, rollback is documentation-only:

1. Remove or mark `fathipoor-platform` parent registry record as planning-only.
2. Restore `fathipoor-website` as the active app record for its domains.
3. Restore `fathipoor-streamer` as the active app record for streamer-specific service tracking.
4. Restore domain mappings to the previous app references.
5. Keep `platform/apps/fathipoor-platform/` files unless deletion is explicitly approved.
6. Record rollback in `manual-validation-pass-001.md`.

## Explicitly Forbidden During Execution

The future merge execution must not perform:

- production access
- deployment
- server commands
- container renaming
- live routing changes
- DNS changes
- Cloudflare changes
- Traefik changes
- app deletion
- old-record deletion
- tool installation
- backup execution
- restore execution

## Required Approval Before Execution

Before the merge execution is performed, the user must separately approve:

- exact files to edit
- exact status labels
- exact parent record content
- exact old-record alias behavior
- exact domain registry changes
- exact rollback rule
- final report requirement

## Current Status

This execution plan is created and ready for review.

The merge is not executed.
