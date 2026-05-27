# Fathipoor Platform Merge Contract

Status: defined-not-executed
Scope: planning contract only

## Purpose

This contract defines how the current Fathipoor records should be merged later into one composite logical platform capsule named `fathipoor-platform`.

This contract does not execute the merge. It only defines the model that a future approved registry update must follow.

## Parent Platform

The future parent platform record is:

```text
fathipoor-platform
```

Role:

- Composite logical app/platform capsule.
- Operational parent for the Fathipoor website, helper endpoints, and streamer.
- Planning and management boundary for future monitoring, backup, logging, release, and rollback plans.

## Existing Records

Current records remain valid until a future registry merge is separately approved:

```text
fathipoor-website
fathipoor-streamer
```

They must not be deleted during the planning-shell phase.

## Future Alias / Component Behavior

When the merge is approved later:

- `fathipoor-website` should become a legacy alias or component reference under `fathipoor-platform`.
- `fathipoor-streamer` should become a legacy alias or component reference under `fathipoor-platform`.
- Old records should not be deleted immediately.
- Old records should point to the parent platform until the team approves archival or cleanup.

Recommended behavior:

```yaml
legacy_aliases:
  - fathipoor-website
  - fathipoor-streamer
```

## Components

The parent platform must contain these components:

```text
web
helpers
streamer
```

### web

Purpose:

- Public-facing Fathipoor website/web app component.

Former record:

```text
fathipoor-website
```

### helpers

Purpose:

- Runtime/helper endpoints currently associated with the Fathipoor website.

Known services:

```text
stream-status
site-metrics
```

Former record:

```text
fathipoor-website
```

### streamer

Purpose:

- Streaming/runtime service component.

Former record:

```text
fathipoor-streamer
```

## Domain Ownership

Future domain ownership should be assigned to the parent platform, with component-level routing notes.

Current domains:

```text
fathipoor.abisanraya.com
appsm.fathipoor.abisanraya.com
```

Recommended future mapping:

```yaml
fathipoor.abisanraya.com:
  app: fathipoor-platform
  component: web

appsm.fathipoor.abisanraya.com:
  app: fathipoor-platform
  component: web_or_helpers
```

The exact `appsm` component split remains pending final route confirmation.

## Taxonomy v3 Parent Rule

The parent platform may summarize the platform risk, but it must not downgrade sensitive child components.

Recommended parent posture:

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

## Taxonomy v3 Component Rule

Component-level Taxonomy v3 remains authoritative where risks differ.

### web

```yaml
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

## Future Registry Changes To Propose Later

A future approved merge execution may update:

- `platform/control-plane/apps-registry.yml`
- `platform/control-plane/domains-registry.yml`
- `app-records/fathipoor-website/README.md`
- `app-records/fathipoor-streamer/README.md`
- `platform/apps/fathipoor-platform/README.md`
- `platform/apps/fathipoor-platform/app-capsule.yml`

No registry changes are approved by this contract alone.

## Production Non-Changes

The merge contract must not change production behavior.

The future merge execution must not:

- rename containers
- change live routes
- change DNS
- change Cloudflare settings
- change Traefik rules
- move files
- change server paths
- deploy anything
- install tools
- delete old records

## Rollback / Undo Rule

If the future registry merge creates confusion or incorrect references, the rollback is documentation-only:

1. Restore `fathipoor-website` as the active app reference.
2. Restore `fathipoor-streamer` as the active app reference.
3. Mark `fathipoor-platform` as planning-only again.
4. Revert domain registry mappings to the previous app references.
5. Keep component files for future review unless deletion is explicitly approved.

## Execution Approval Required

Before merge execution, the user must approve:

- exact files to edit
- exact old-record behavior
- exact domain mapping behavior
- exact component mapping behavior
- rollback/undo rule
- final validation report requirement

## Not Authorized By This Contract

This contract does not authorize:

- production access
- deployment
- server commands
- container renaming
- live routing changes
- apps-registry update
- domains-registry update
- deletion of old app records
- Cloudflare changes
- Traefik changes
- tool installation
