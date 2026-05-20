# vktNonRobustBufferAccessTests

## Overview

This page documents the Vulkan CTS `robustness.non_robust_buffer_access` group implemented by [`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L1-L61). The group registers two Amber compute tests that verify out-of-bounds buffer accesses in unexecuted shader branches do not affect the result produced by the executed branch.

## Role of file

[`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L58) is a compact implementation and registration file. The category root adds its returned `non_robust_buffer_access` group directly ([`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L90)), and the header declares the factory ([`vktNonRobustBufferAccessTests.hpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.hpp#L31-L37)).

## Source code link

- Source: [`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L1-L61)
- Header: [`vktNonRobustBufferAccessTests.hpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.hpp#L1-L41)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L90) | Category root registration. |
| [`vktNonRobustBufferAccessTests.hpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.hpp#L31-L37) | Factory declaration. |
| [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L1-L105) | Underflow Amber shader, buffers, dispatch, and expected result. |
| [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L1-L105) | Overflow Amber shader, buffers, dispatch, and expected result. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754) | Default mustpass entries for the two leaves. |

## Registration Hierarchy

```text
robustness.non_robust_buffer_access
├── unexecuted_oob_overflow
└── unexecuted_oob_underflow
```

The root group name is stored as `non_robust_buffer_access`, and its direct child names come from the two-element `nonRobustBufferAccessTests` vector ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L54)). The default mustpass file contains both leaves ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754)).

## Test Families

### `unexecuted_oob_overflow`

This Amber compute test initializes input arrays of 512 `int32` values and a 1024-value output. The shader starts with high indices (`index_in0 = 127`, `index_in1 = 383`, `index_out0 = 255`, `index_out1 = 383`) and alternates branches while decrementing indices, so the unexecuted path can reference overflow or overlapping result indices ([`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L26-L35), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L45-L76)).

### `unexecuted_oob_underflow`

This Amber compute test uses the same array sizes and branch-control buffer, but starts alternate-path indices at negative offsets (`index_in1 = -128`, `index_out1 = -128`). The comments describe underflow/overlap access in the unexecuted path while the executed path writes the expected interleaved result ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L26-L35), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L45-L76)).

## Parameter dimensions and observed values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Registered leaves | `unexecuted_oob_underflow`, `unexecuted_oob_overflow` | [`nonRobustBufferAccessTests`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L41-L46) |
| Execution backend | Amber test cases loaded from `non_robust_buffer_access/<leaf>.amber` | [`createAmberTestCase()`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L49-L54) |
| Shader stage | Compute | Amber `SHADER compute` declarations in [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L36-L43) and [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L36-L43) |
| Workgroup configuration | `local_size_x = 4`; dispatch `RUN pipeline 4 1 1` | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L39-L43), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L103-L105) |
| Buffer sizes | `data_in0` and `data_in1`: 512 `int32`; `data_in2`: 8 `int32`; `data_out` and `expected`: 1024 `int32` | [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L79-L93), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L79-L93) |
| Branch-control data | `0, 2, 1, 2, 0, 2, 1, -6` | [`data_in2`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L81-L90) |

## Support / feature requirements

- The C++ file registers Amber tests only when `CTS_USES_VULKANSC` is not defined; in VulkanSC builds it returns an empty group from the inspected loop body ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L48-L55)).
- No explicit Vulkan extension or feature requirement is declared in the C++ registration file beyond the Amber compute pipeline operations it references ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L39-L58)).
- The inspected Amber scripts use GLSL `#version 430`, storage buffers, and compute dispatch ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L36-L43), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L36-L43)).

## Verification methods

- The C++ registration maps each leaf name to an Amber file of the same basename with `.amber` appended ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L49-L54)).
- Each Amber script binds two input buffers, a control buffer, and the output buffer to one compute pipeline, runs `4 1 1` workgroups, and verifies `data_out EQ_BUFFER expected` ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L95-L105), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L95-L105)).
- The expected output is a 1024-value increasing integer series; the comments define the intended result as interleaving the two 512-value input arrays ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L16-L35), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L91-L93)).

## Test principles

- Keep all executed accesses valid while placing out-of-bounds or overlapping accesses in the unexecuted side of alternating branches ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L26-L35), [`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L26-L35)).
- Use a control buffer and `condition_index` increments to avoid optimizing away the branch structure under test ([`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L22-L24), [`unexecuted_oob_underflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_underflow.amber#L53-L75)).
- Reduce the final verdict to full-buffer equality between produced output and an explicit expected series ([`unexecuted_oob_overflow.amber`](../../../data/vulkan/amber/non_robust_buffer_access/unexecuted_oob_overflow.amber#L91-L105)).

## Notes / uncertainties

- The registration tree lists only two direct leaf tests; no nested subgroups were observed in the assigned C++ file.
- The C++ file comment contains the typo `shder`; this page preserves the intended meaning rather than the spelling ([`vktNonRobustBufferAccessTests.cpp`](../../../modules/vulkan/robustness/vktNonRobustBufferAccessTests.cpp#L20-L24)).
- Other mustpass profiles were not inspected; default mustpass confirms the two leaves for `vk-default` ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L13753-L13754)).
