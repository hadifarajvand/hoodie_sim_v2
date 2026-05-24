# Feature 055: Paper-Default Training Smoke Run

## Purpose

Run the first controlled paper-default smoke step after the Feature 054 readiness contract.

## Scope

This feature checks that the live environment can feed replay, optimizer, loss, legal-action, delayed-reward, and metadata reporting paths for one paper-default episode.

## Required outcome

The report must end with `paper_default_training_smoke_passed` only if replay is populated, at least one optimizer step runs, loss is finite, selected actions are legal, and Feature 054 readiness is true.

## Forbidden

No full campaign, no baseline comparison, no paper reproduction claim, no policy drift, no dependency drift, and no prior artifact rewrites.
