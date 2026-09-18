# Shared Types and Backend Contracts

This directory is intentionally kept free of domain definitions (such as `SystemState`, `EV`, `Station`, `Grid`) until the authoritative backend contract is finalized.

The frontend is strictly forbidden from inventing these types or maintaining a parallel domain logic engine. Once the backend schema is established, it will be integrated here and consumed globally by the generic state boundary and UI features.

Presently, this directory only houses generic transport-level interfaces required by the REST and WebSocket integration boundaries.
