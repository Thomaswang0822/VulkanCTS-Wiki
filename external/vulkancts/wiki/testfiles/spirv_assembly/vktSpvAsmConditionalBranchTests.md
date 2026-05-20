# vktSpvAsmConditionalBranchTests

## Overview

Tests for the SPIR-V OpBranchConditional instruction, specifically verifying behavior when both branch targets are the same label (same-label branching). Tests both true and false condition values.

## Role

Implementation file

## Source

- [vktSpvAsmConditionalBranchTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmConditionalBranchTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.compute.conditional_branch
├── same_labels_true
└── same_labels_false

spirv_assembly.instruction.graphics.conditional_branch
├── same_labels_true_frag
├── same_labels_true_geom
├── same_labels_true_tessc
├── same_labels_true_tesse
├── same_labels_true_vert
├── same_labels_false_frag
├── same_labels_false_geom
├── same_labels_false_tessc
├── same_labels_false_tesse
└── same_labels_false_vert
```

## Test Families

### same_labels_true — Same-label branch with true condition

Tests OpBranchConditional where both the true and false labels point to the same block (`%live`), with the condition set to `%true` (OpConstantTrue). The dead code block (`%dead`) stores a sentinel value (2863311530) and should never execute.

Observed in `addComputeSameLabelsTest()` at vktSpvAsmConditionalBranchTests.cpp#L49-L126 and `addGraphicsSameLabelsTest()` at vktSpvAsmConditionalBranchTests.cpp#L128-L218.

### same_labels_false — Same-label branch with false condition

Tests OpBranchConditional where both the true and false labels point to the same block (`%live`), with the condition set to `%false` (OpConstantFalse). Despite the false condition, the branch should still go to the same target label.

Observed in `addComputeSameLabelsTest()` at vktSpvAsmConditionalBranchTests.cpp#L49-L126 and `addGraphicsSameLabelsTest()` at vktSpvAsmConditionalBranchTests.cpp#L128-L218.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| condition | `true`, `false` | Boolean condition for OpBranchConditional |
| ShaderStage | All stages (graphics only) | Graphics pipeline stages via `createTestsForAllStages` |

## Support Requirements

- **vertexPipelineStoresAndAtomics** — required for graphics tests — vktSpvAsmConditionalBranchTests.cpp#L143
- **fragmentStoresAndAtomics** — required for graphics tests — vktSpvAsmConditionalBranchTests.cpp#L144
- **tessellationShader** — implicitly required for tessellation stages (graphics)
- **geometryShader** — implicitly required for geometry stage (graphics)

## Verification Methods

- **Compute**: Output buffer is compared against expected sequential values (0, 1, 2, ..., numItems-1). Each invocation stores its index via the live branch; if the dead branch executed, the sentinel value 2863311530 would appear instead — vktSpvAsmConditionalBranchTests.cpp#L56-L57 and #L122
- **Graphics**: Uses `GraphicsResources` with output buffer verification via `createTestsForAllStages`. The same expected sequential values are used — vktSpvAsmConditionalBranchTests.cpp#L137-L141

## Notes

- This is a focused test file with only two test cases per pipeline type (compute and graphics)
- The test specifically targets the edge case where OpBranchConditional has identical true/false labels, which is valid SPIR-V but may expose driver bugs in dead code elimination or control flow handling
- The sentinel value 2863311530 (0xAAAAAAAA) is used in the dead code block to detect incorrect execution — vktSpvAsmConditionalBranchTests.cpp#L96
