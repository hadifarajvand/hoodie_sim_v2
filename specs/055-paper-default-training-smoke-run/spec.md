# Feature 055: Paper-Default Training Smoke Run

## Purpose

Run the first controlled paper-default training smoke step after the Feature 054 readiness contract.

## Scope

This feature uses the live approved trainer path for one paper-default smoke episode and proves that replay, optimizer, loss, legal-action, delayed-reward, checkpoint-metadata, and train/eval reporting paths all execute without starting a full campaign.

## Required outcome

The report must end with `paper_default_training_smoke_passed` only if Feature 054 readiness is true, live environment training is used, fixture-only training is not used, replay is populated, at least one optimizer step runs, loss is finite, selected actions are legal, delayed reward behavior is preserved, checkpoint metadata is valid, and the smoke scope does not claim full training, baseline comparison, or paper reproduction.

## Forbidden

No full campaign, no baseline comparison, no paper reproduction claim, no policy drift, no dependency drift, no environment semantic drift, no reward timing drift, and no prior artifact rewrites.
