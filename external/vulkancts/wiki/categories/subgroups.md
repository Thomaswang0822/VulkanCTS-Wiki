# subgroups

## Overview

The `subgroups` category documents Vulkan subgroup built-ins and subgroup operations across compute, graphics/framebuffer, mesh, and ray-tracing execution paths. The category is rooted in [`vktSubgroupsTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L25-L47), which includes the registering subgroup files and attaches the verified child groups in [`createChildren()`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L55-L82).

## Registration Entry Point

```text
subgroups
├── builtin_var
├── builtin_mask_var
├── basic
├── vote
├── ballot
├── ballot_broadcast
├── ballot_other
├── arithmetic
├── clustered
├── partitioned (non-VulkanSC only)
├── shuffle
├── quad
├── shape
├── ballot_mask
├── multiple_dispatches
├── size_control
├── subgroup_uniform_control_flow (non-VulkanSC only)
├── uniform_descriptor_indexing (non-VulkanSC only)
└── shader_quad_control (non-VulkanSC only)
```

## File Inventory

| File | Role | Notes | Level-3 |
|---|---|---|---|
| [`vktSubgroupsTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L1) | Registration | Top-level dispatcher | [`vktSubgroupsTests.md`](../testfiles/subgroups/vktSubgroupsTests.md) |
| [`vktSubgroupsBuiltinVarTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1) | Implementation | Registers `builtin_var` | [`vktSubgroupsBuiltinVarTests.md`](../testfiles/subgroups/vktSubgroupsBuiltinVarTests.md) |
| [`vktSubgroupsBuiltinMaskVarTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1) | Implementation | Registers `builtin_mask_var` | [`vktSubgroupsBuiltinMaskVarTests.md`](../testfiles/subgroups/vktSubgroupsBuiltinMaskVarTests.md) |
| [`vktSubgroupsBasicTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1) | Implementation | Registers `basic` | [`vktSubgroupsBasicTests.md`](../testfiles/subgroups/vktSubgroupsBasicTests.md) |
| [`vktSubgroupsVoteTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L1) | Implementation | Registers `vote` | [`vktSubgroupsVoteTests.md`](../testfiles/subgroups/vktSubgroupsVoteTests.md) |
| [`vktSubgroupsBallotTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1) | Implementation | Registers `ballot` | [`vktSubgroupsBallotTests.md`](../testfiles/subgroups/vktSubgroupsBallotTests.md) |
| [`vktSubgroupsBallotBroadcastTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L1) | Implementation | Registers `ballot_broadcast` | [`vktSubgroupsBallotBroadcastTests.md`](../testfiles/subgroups/vktSubgroupsBallotBroadcastTests.md) |
| [`vktSubgroupsBallotOtherTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L1) | Implementation | Registers `ballot_other` | [`vktSubgroupsBallotOtherTests.md`](../testfiles/subgroups/vktSubgroupsBallotOtherTests.md) |
| [`vktSubgroupsArithmeticTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L1) | Implementation | Registers `arithmetic` | [`vktSubgroupsArithmeticTests.md`](../testfiles/subgroups/vktSubgroupsArithmeticTests.md) |
| [`vktSubgroupsClusteredTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L1) | Implementation | Registers `clustered` | [`vktSubgroupsClusteredTests.md`](../testfiles/subgroups/vktSubgroupsClusteredTests.md) |
| [`vktSubgroupsPartitionedTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L1) | Implementation | Registers `partitioned` | [`vktSubgroupsPartitionedTests.md`](../testfiles/subgroups/vktSubgroupsPartitionedTests.md) |
| [`vktSubgroupsShuffleTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L1) | Implementation | Registers `shuffle` | [`vktSubgroupsShuffleTests.md`](../testfiles/subgroups/vktSubgroupsShuffleTests.md) |
| [`vktSubgroupsQuadTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L1) | Implementation | Registers `quad` | [`vktSubgroupsQuadTests.md`](../testfiles/subgroups/vktSubgroupsQuadTests.md) |
| [`vktSubgroupsShapeTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsShapeTests.cpp#L1) | Implementation | Registers `shape` | [`vktSubgroupsShapeTests.md`](../testfiles/subgroups/vktSubgroupsShapeTests.md) |
| [`vktSubgroupsBallotMasksTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1) | Implementation | Registers `ballot_mask` | [`vktSubgroupsBallotMasksTests.md`](../testfiles/subgroups/vktSubgroupsBallotMasksTests.md) |
| [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L1) | Implementation | Registers `multiple_dispatches` | [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.md`](../testfiles/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.md) |
| [`vktSubgroupsSizeControlTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1) | Implementation | Registers `size_control` | [`vktSubgroupsSizeControlTests.md`](../testfiles/subgroups/vktSubgroupsSizeControlTests.md) |
| [`vktSubgroupUniformControlFlowTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L1) | Implementation | Registers `subgroup_uniform_control_flow` | [`vktSubgroupUniformControlFlowTests.md`](../testfiles/subgroups/vktSubgroupUniformControlFlowTests.md) |
| [`vktSubgroupsUniformDescriptorIndexingTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L1) | Implementation | Registers `uniform_descriptor_indexing` | [`vktSubgroupsUniformDescriptorIndexingTests.md`](../testfiles/subgroups/vktSubgroupsUniformDescriptorIndexingTests.md) |
| [`vktSubgroupsQuadControlTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1) | Implementation | Registers `shader_quad_control` | [`vktSubgroupsQuadControlTests.md`](../testfiles/subgroups/vktSubgroupsQuadControlTests.md) |
| [`vktSubgroupsTestsUtils.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1) | Helper | Shared execution and verification helpers; no direct test registration page | — |
| [`vktSubgroupsScanHelpers.cpp`](../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L1) | Helper | Shared scan/reference support; no direct test registration page | — |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktSubgroupsTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTests.cpp#L1) | [`vktSubgroupsTests.md`](../testfiles/subgroups/vktSubgroupsTests.md) |
| [`vktSubgroupsBuiltinVarTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1) | [`vktSubgroupsBuiltinVarTests.md`](../testfiles/subgroups/vktSubgroupsBuiltinVarTests.md) |
| [`vktSubgroupsBuiltinMaskVarTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1) | [`vktSubgroupsBuiltinMaskVarTests.md`](../testfiles/subgroups/vktSubgroupsBuiltinMaskVarTests.md) |
| [`vktSubgroupsBasicTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L1) | [`vktSubgroupsBasicTests.md`](../testfiles/subgroups/vktSubgroupsBasicTests.md) |
| [`vktSubgroupsVoteTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L1) | [`vktSubgroupsVoteTests.md`](../testfiles/subgroups/vktSubgroupsVoteTests.md) |
| [`vktSubgroupsBallotTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1) | [`vktSubgroupsBallotTests.md`](../testfiles/subgroups/vktSubgroupsBallotTests.md) |
| [`vktSubgroupsBallotBroadcastTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotBroadcastTests.cpp#L1) | [`vktSubgroupsBallotBroadcastTests.md`](../testfiles/subgroups/vktSubgroupsBallotBroadcastTests.md) |
| [`vktSubgroupsBallotOtherTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotOtherTests.cpp#L1) | [`vktSubgroupsBallotOtherTests.md`](../testfiles/subgroups/vktSubgroupsBallotOtherTests.md) |
| [`vktSubgroupsArithmeticTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L1) | [`vktSubgroupsArithmeticTests.md`](../testfiles/subgroups/vktSubgroupsArithmeticTests.md) |
| [`vktSubgroupsClusteredTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L1) | [`vktSubgroupsClusteredTests.md`](../testfiles/subgroups/vktSubgroupsClusteredTests.md) |
| [`vktSubgroupsPartitionedTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L1) | [`vktSubgroupsPartitionedTests.md`](../testfiles/subgroups/vktSubgroupsPartitionedTests.md) |
| [`vktSubgroupsShuffleTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L1) | [`vktSubgroupsShuffleTests.md`](../testfiles/subgroups/vktSubgroupsShuffleTests.md) |
| [`vktSubgroupsQuadTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L1) | [`vktSubgroupsQuadTests.md`](../testfiles/subgroups/vktSubgroupsQuadTests.md) |
| [`vktSubgroupsShapeTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsShapeTests.cpp#L1) | [`vktSubgroupsShapeTests.md`](../testfiles/subgroups/vktSubgroupsShapeTests.md) |
| [`vktSubgroupsBallotMasksTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1) | [`vktSubgroupsBallotMasksTests.md`](../testfiles/subgroups/vktSubgroupsBallotMasksTests.md) |
| [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.cpp#L1) | [`vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.md`](../testfiles/subgroups/vktSubgroupsMultipleDispatchesUniformSubgroupSizeTests.md) |
| [`vktSubgroupsSizeControlTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1) | [`vktSubgroupsSizeControlTests.md`](../testfiles/subgroups/vktSubgroupsSizeControlTests.md) |
| [`vktSubgroupUniformControlFlowTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L1) | [`vktSubgroupUniformControlFlowTests.md`](../testfiles/subgroups/vktSubgroupUniformControlFlowTests.md) |
| [`vktSubgroupsUniformDescriptorIndexingTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L1) | [`vktSubgroupsUniformDescriptorIndexingTests.md`](../testfiles/subgroups/vktSubgroupsUniformDescriptorIndexingTests.md) |
| [`vktSubgroupsQuadControlTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L1) | [`vktSubgroupsQuadControlTests.md`](../testfiles/subgroups/vktSubgroupsQuadControlTests.md) |

## Subgroup Structure and Major Themes

- Built-in variable coverage is split into [`builtin_var`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinVarTests.cpp#L1948) and [`builtin_mask_var`](../../modules/vulkan/subgroups/vktSubgroupsBuiltinMaskVarTests.cpp#L1337).
- Core operation families include [`basic`](../../modules/vulkan/subgroups/vktSubgroupsBasicTests.cpp#L2198), [`vote`](../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L547), [`ballot`](../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1021), [`arithmetic`](../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L477), [`clustered`](../../modules/vulkan/subgroups/vktSubgroupsClusteredTests.cpp#L386), [`shuffle`](../../modules/vulkan/subgroups/vktSubgroupsShuffleTests.cpp#L663), [`quad`](../../modules/vulkan/subgroups/vktSubgroupsQuadTests.cpp#L414), and [`shape`](../../modules/vulkan/subgroups/vktSubgroupsShapeTests.cpp#L391).
- Extension or specialized branches include [`partitioned`](../../modules/vulkan/subgroups/vktSubgroupsPartitionedTests.cpp#L528), [`ballot_mask`](../../modules/vulkan/subgroups/vktSubgroupsBallotMasksTests.cpp#L1417), [`size_control`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L1015), [`subgroup_uniform_control_flow`](../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L224), [`uniform_descriptor_indexing`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L827), and [`shader_quad_control`](../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L807).

## Recurring Parameter Dimensions

| Dimension | Observed examples |
|---|---|
| Operation family | Operation enums such as vote, ballot, arithmetic, clustered, shuffle, quad, and shape operation types in the individual files |
| Shader stage family | Direct child groups repeatedly divide coverage into `graphics`, `compute`, `framebuffer`, `ray_tracing`, and `mesh`, for example in [`arithmetic`](../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L477-L484) |
| Data format and input layout | Generated test names combine operation names with formats, input SSBO/image data, and helper layouts, with shared input descriptors defined by [`SSBOData`](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L75-L121) |
| Required subgroup size | Many compute/mesh paths iterate min-to-max power-of-two required subgroup sizes; [`size_control`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L44-L86) makes this the central parameter |
| Extension variant | Vote and ballot files add nested legacy extension groups such as [`ext_shader_subgroup_vote`](../../modules/vulkan/subgroups/vktSubgroupsVoteTests.cpp#L558-L565) and [`ext_shader_subgroup_ballot`](../../modules/vulkan/subgroups/vktSubgroupsBallotTests.cpp#L1030-L1033) |
| External data | Uniform-control-flow tests load Amber case groups from large/small/control/discard directories in [`vktSubgroupUniformControlFlowTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupUniformControlFlowTests.cpp#L227-L249) |

## Recurring Support Requirements

The common baseline is subgroup support, checked through local calls to [`isSubgroupSupported()`](../../modules/vulkan/subgroups/vktSubgroupsArithmeticTests.cpp#L279-L285) and related helpers. Operation families then require their feature bits, such as arithmetic, ballot, clustered, shuffle, quad, vote, or partitioned support. Cross-stage branches check shader-stage support and optional ray-tracing or mesh requirements, while size-control paths require `VK_EXT_subgroup_size_control` and validate required-size stage support in [`supportedCheckFeatures()`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L514-L570).

## Recurring Verification Methods

Most operation files generate shaders, execute them through framebuffer or compute-like helpers, read back result storage, and call local callbacks. The shared callback signatures carry `subgroupSize` and dimensions through [`CheckResult` declarations](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.hpp#L58-L63), and common helpers turn callback failures into CTS failures in [`vktSubgroupsTestsUtils.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L2622-L2637). Specialized branches add image/color classification for uniform descriptor indexing in [`iterate()`](../../modules/vulkan/subgroups/vktSubgroupsUniformDescriptorIndexingTests.cpp#L366-L377), output correctness checks for shader quad control in [`iterate()`](../../modules/vulkan/subgroups/vktSubgroupsQuadControlTests.cpp#L331-L336), and subgroup-size property/range checks in [`vktSubgroupsSizeControlTests.cpp`](../../modules/vulkan/subgroups/vktSubgroupsSizeControlTests.cpp#L974-L1005).


## Notes / Uncertainties

- Level-3 pages are created only for files that register tests. Helper files such as [`vktSubgroupsTestsUtils.cpp`](../../modules/vulkan/subgroups/vktSubgroupsTestsUtils.cpp#L1) and [`vktSubgroupsScanHelpers.cpp`](../../modules/vulkan/subgroups/vktSubgroupsScanHelpers.cpp#L1) are documented as support files only.
- Generated leaf matrices are large; the parseable trees list direct children and the prose summarizes deeper generated leaves.
