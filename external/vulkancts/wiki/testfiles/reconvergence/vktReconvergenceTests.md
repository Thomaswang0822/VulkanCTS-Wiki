# vktReconvergenceTests

This file is the `reconvergence` category dispatcher and the main implementation for generated reconvergence tests. The Vulkan test package registers the root as `reconvergence` through `Reconvergence::createTests` [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1387-L1391), while the experimental package registers the same root name through `Reconvergence::createTestsExperimental` [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1403-L1407). The implementation builds five direct reconvergence branches plus the delegated `terminate_invocation` branch [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7786-L7947).

## Source Files

| Role | Link |
|------|------|
| Category root and generated reconvergence implementation | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp) |
| Root declaration | [vktReconvergenceTests.hpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.hpp#L30-L36) |
| Terminate-invocation delegated branch | [vktReconvergenceTerminateInvocationTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675) |
| Build inventory | [CMakeLists.txt](../../../modules/vulkan/reconvergence/CMakeLists.txt#L7-L12) |

## Registration Hierarchy

```text
reconvergence
├── subgroup_uniform_control_flow_elect
├── subgroup_uniform_control_flow_ballot
├── workgroup_uniform_control_flow_elect
├── workgroup_uniform_control_flow_ballot
├── maximal
└── terminate_invocation
```

## Test Families

### subgroup_uniform_control_flow_elect — Subgroup-uniform control flow with elect

The branch name comes from the `ttCases` registration table and uses `TT_SUCF_ELECT` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). In the non-maximal branches, only the compute shader stage is registered because non-compute stages are skipped unless the test type is `TT_MAXIMAL` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825). Its deeper generated children are `compute.nesting2`, `compute.nesting3`, and `compute.nesting4`, because non-maximal branches skip nesting levels 5 and 6 [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7837-L7872).

### subgroup_uniform_control_flow_ballot — Subgroup-uniform control flow with ballot

This branch is registered from `TT_SUCF_BALLOT` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). As a ballot-based non-elect case, support requires `VK_SUBGROUP_FEATURE_BALLOT_BIT` rather than the elect/basic gate [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4404-L4408). The visible generated path shape is compute-only with nesting levels 2 through 4, following the common stage and nesting filters [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7837-L7872).

### workgroup_uniform_control_flow_elect — Workgroup-uniform control flow with elect

This branch is registered from `TT_WUCF_ELECT` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). The `CaseDef` helpers classify workgroup-uniform and subgroup-uniform modes together as uniform-control-flow tests [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L109-L124), and the support check requires `shaderSubgroupUniformControlFlow` for both categories [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4428-L4430).

### workgroup_uniform_control_flow_ballot — Workgroup-uniform control flow with ballot

This branch is registered from `TT_WUCF_BALLOT` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It combines the uniform-control-flow feature gate with the ballot operation gate because non-elect cases require `VK_SUBGROUP_FEATURE_BALLOT_BIT` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4404-L4408), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4428-L4430).

### maximal — Maximal reconvergence

The maximal branch is registered from `TT_MAXIMAL` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It registers compute and fragment direct children in the current source configuration; additional graphics stages are present only under the disabled `INCLUDE_GRAPHICS_TESTS` block [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7814). The compute path generates `nesting2` through `nesting6`, while the fragment path sets `nNdx = 7`, adds Amber fragment cases, and then skips the nesting loop because the loop condition starts beyond 6 [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7827-L7837). Maximal shaders require `GL_EXT_maximal_reconvergence` during source generation [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4553-L4561) and require the `shaderMaximalReconvergence` feature in support checks [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4432-L4433).

### terminate_invocation — Delegated terminate-invocation cases

The root implementation appends this child by calling `createTerminateInvocationTests(testCtx)` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7943-L7947). The registered child names are documented in [vktReconvergenceTerminateInvocationTests](vktReconvergenceTerminateInvocationTests.md).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Test type | `subgroup_uniform_control_flow_elect`, `subgroup_uniform_control_flow_ballot`, `workgroup_uniform_control_flow_elect`, `workgroup_uniform_control_flow_ballot`, `maximal` | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803) |
| Shader stages | `compute` for all five branches; `fragment` only for `maximal` in the inspected build configuration | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825) |
| Nesting levels | Non-maximal generated tests use `nesting2` to `nesting4`; maximal compute uses `nesting2` to `nesting6` | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7837-L7872) |
| Seeds | Eight seed groups named `0` through `7` are created under each generated nesting group | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7842-L7848) |
| Generated tests per seed before experimental split | 250 for nesting 2 to 4, 100 for nesting 5, and 50 for nesting 6 | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7849-L7866) |
| Compute dimensions | Generated compute cases use `sizeX = 7` and `sizeY = 13` | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7880-L7887) |
| Fragment dimensions | Generated maximal fragment cases use a 32 by 32 framebuffer extent | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7888-L7891) |
| Main vs experimental split | Cases with index below one fifth of `numTests` go to the main tree; the remaining four fifths go to the experimental tree | [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7929-L7933), [vktTestPackage.cpp](../../../modules/vulkan/vktTestPackage.cpp#L1403-L1407) |

## Support Requirements

Generated reconvergence cases require Vulkan 1.1, subgroup operation support for the selected shader stage, and compute workgroup sizes within device limits when the selected stage is compute [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4395-L4426). Elect cases require `VK_SUBGROUP_FEATURE_BASIC_BIT`, ballot cases require `VK_SUBGROUP_FEATURE_BALLOT_BIT`, uniform-control-flow cases require `shaderSubgroupUniformControlFlow`, and maximal cases require `shaderMaximalReconvergence` [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4404-L4408), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4428-L4433).

## Verification Methods

The generated tests produce shader output into buffers, simulate the random program on the CPU, and compare GPU output with the CPU reference [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5278-L5314). Maximal compute result checking expects exact ballot equality against the reference and logs mismatches [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5317-L5350). Graphics-style paths use the same CPU-reference principle, with fragment code checking subgroup count consistency before executing and comparing reference ballots [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L6064-L6088), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L6341-L6367). Vertex and geometry helper implementations also compare emitted ballots against simulated references when those disabled-stage paths are compiled [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L6703-L6745), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7739-L7781).

## Notes

The source contains additional graphics-stage code behind a disabled `INCLUDE_GRAPHICS_TESTS` macro, so this page documents the registered paths visible in the current source and mustpass coverage rather than the disabled branches [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L69-L69), [vktReconvergenceTests.cpp](../../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7814).
