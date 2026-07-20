## Overview

The `memory_model` test category collects tests that check whether shader-visible memory operations preserve the right values
under Vulkan/SPIR-V memory semantics and layout rules.

## Background Knowledge

No common prerequisite concepts need category-level explanation for this test category.

## Category Structure

```text
memory_model
├── message_passing
├── write_after_read
├── transitive
├── padding
└── shared
```

The test category has five registered test families but three Level-3 pages:

- [MessagePassing.md](../testfiles/memory_model/MessagePassing.md) covers `message_passing`, `write_after_read`, and
  `transitive` because they are generated synchronization and visibility families rooted in the same implementation file.
- [Padding.md](../testfiles/memory_model/Padding.md) covers the single `memory_model.padding.test` case.
- [SharedLayout.md](../testfiles/memory_model/SharedLayout.md) covers the generated `shared` layout test family, including
  the intermediate `shared.16bit` and `shared.8bit` nodes.

## How the Families Fit Together

All families in this category test whether shader-visible memory behavior matches the contract expected by Vulkan CTS, but they
approach that contract from different angles:

- `message_passing`, `write_after_read`, and `transitive` focus on **when** a value is allowed or required to become visible after
  synchronization, early reads, or availability/visibility chains.
- `padding` focuses on **which bytes** a shader-side structure assignment is allowed to affect when `std140` padding exists in the
  host-visible destination memory.
- `shared` focuses on **which generated fields** in GLSL workgroup `shared` memory can be written, synchronized, read, and
  compared across many layout shapes and type-width variants.

Together, these test families make `memory_model` a test category about shader-visible memory correctness: visibility timing,
layout-preserving writes, and workgroup shared-memory value preservation.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `message_passing`, `write_after_read`, `transitive` | [MessagePassing.md](../testfiles/memory_model/MessagePassing.md) | Payload/guard synchronization, release/acquire behavior, early-read hazards, transitive visibility chains, and the generated synchronization matrix. |
| `padding` | [Padding.md](../testfiles/memory_model/Padding.md) | The single `memory_model.padding.test` case and how it detects destination padding corruption. |
| `shared`, including intermediate `shared.16bit` and `shared.8bit` nodes | [SharedLayout.md](../testfiles/memory_model/SharedLayout.md) | Randomized GLSL `shared` layout generation, write/barrier/read/compare behavior, and 16-bit/8-bit variants. |
