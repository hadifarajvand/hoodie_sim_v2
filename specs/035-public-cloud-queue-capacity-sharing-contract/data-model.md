# Data Model: Public/Cloud Queue Capacity Sharing Contract

## Entities

### Public Queue Host

A destination EA host that can receive one or more public queues.

Relevant attributes:
- `host_node_id`
- configured public CPU capacity per slot
- active queue heads targeting the host

Validation rules:
- Capacity is fixed per host per slot.
- Capacity is shared only among active heads targeting the same host.

### Cloud Queue Host

The shared cloud execution host that can receive one or more cloud queues.

Relevant attributes:
- `host_node_id == "cloud"`
- configured cloud CPU capacity per slot
- active queue heads targeting cloud

Validation rules:
- Capacity is global across all cloud queues.
- Capacity is shared only among active cloud heads.

### Active Queue Head

The first task in a queue that is ready for execution at the beginning of a slot.

Relevant attributes:
- queue identity
- source agent identity
- task identity
- readiness at slot start

Validation rules:
- Only the queue head is active.
- Tasks behind the head are not active until they reach the front in a later slot.

### Capacity Share

The equal portion of a host's slot capacity assigned to an active queue head.

Relevant attributes:
- host capacity
- number of active heads for the host
- assigned per-head share

Validation rules:
- `per_head_capacity = host_capacity / k` where `k` is the number of active heads.
- No same-slot redistribution of leftover capacity.

## Relationships

- A public host may have zero or more active public queue heads in a slot.
- The cloud host may have zero or more active cloud queue heads in a slot.
- Different hosts are independent capacity pools.

## State Transitions

- A queue head becomes active when it is first at the front of the queue at slot start.
- A queue head stops being active once it is completed or dropped and removed from the front.
- Remaining queued tasks become active only when they reach the front in a later slot.
