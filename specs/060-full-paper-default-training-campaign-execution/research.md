# Research: Feature 060

## Decision: execute only the approved controlled run

Feature 060 is the first execution feature after the gate. It must follow the scope, seeds, output directory, and resource limits defined by Feature 059.

## Decision: report actual counts

The report must record actual executed counts. It must not inflate episode, step, replay, checkpoint, or metric counts.

## Decision: separate results from claims

This feature records campaign artifacts and metrics. Interpretation and comparison readiness belong to Feature 061.
