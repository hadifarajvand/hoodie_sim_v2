# ECHO State Schema

- schema_version: `echo_v1`
- source: live `HoodieGymEnvironment.observe_flat(task)` / `legal_action_mask(task)`
- feature_order: `arrival_indicator`, `task_size`, `processing_density`, `timeout_length`, `queue_load`, `local_queue_depth`, `outbound_queue_depth`, `local_ert`, `min_outbound_ert`, `mask_local`, `mask_horizontal`, `mask_vertical`
- dimension: `12`
- normalization: `task_size` / `10.0`, `processing_density` raw, `timeout_length` raw, `queue_load` raw, `local_queue_depth` raw, `outbound_queue_depth` raw, `ERT` raw slots, masks in `{0,1}`
- clipping: ERT candidates clipped by policy path before action selection; no-arrival uses zero vector
- candidate ordering: local, horizontal_* , cloud
- mask ordering: local, horizontal, vertical
- LSTM ordering: not used in live smoke path; learner smoke uses same tensor schema as trainer input
