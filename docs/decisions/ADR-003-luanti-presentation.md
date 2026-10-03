# ADR-003: native Luanti presentation and selected content

Status: ACCEPTED (original specification §6–7, §19–20, §40–46; amendments §1, §20–22).

Luanti may contain its local client/server runtime to register content and
render the derived world. IPC ingestion and mesh updates run through the C++
bridge. Use the native ClientMap/mesh queue; defer new meshing/LOD systems until
measurements justify them. Mineclonia contributes selected assets and visual
definitions, without gameplay AI, survival, crafting or world generation.

Coordinate scales and camera height belong to presentation configuration.
All projections must use the same origin transformation. Disconnection leaves
the client without authority. A Luanti world is disposable cache data.

An entity count in a packet or an empty scene node is not evidence of visible
animated entities/vehicles. Rendering acceptance uses the actual client.
