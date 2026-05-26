# reconvergence

The `reconvergence` category covers generated shader reconvergence tests and terminate-invocation behavior. The category root is registered by the Vulkan test package as `reconvergence` [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1387-L1391). The experimental package also registers a `reconvergence` root through `Reconvergence::createTestsExperimental` [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1403-L1407); that factory selects the experimental fifth of generated cases while still appending the delegated `terminate_invocation` branch [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7929-L7947). The category implementation lives under [reconvergence](../../modules/vulkan/reconvergence/) and its build file lists two registering implementation sources plus their headers [CMakeLists.txt](../../modules/vulkan/reconvergence/CMakeLists.txt#L7-L12).

## Registration Entry Point

| Item | Evidence |
|------|----------|
| Main package root | [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1387-L1391) |
| Experimental package root | [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1403-L1407) |
| Category implementation factory | [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7786-L7948) |
| Public declarations | [vktReconvergenceTests.hpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.hpp#L30-L36) |
| Build inventory | [CMakeLists.txt](../../modules/vulkan/reconvergence/CMakeLists.txt#L7-L12) |

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

### subgroup_uniform_control_flow_elect — Subgroup-uniform control flow using elect

The branch is one of the five `ttCases` names registered by the main factory [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It is compute-only in the inspected configuration because non-compute shader stages are skipped for non-maximal test types [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825). See [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md).

### subgroup_uniform_control_flow_ballot — Subgroup-uniform control flow using ballot

The branch is registered from `TT_SUCF_BALLOT` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It shares the generated compute/nesting/seed structure with other non-maximal branches and uses ballot operation support instead of the elect/basic gate [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4404-L4408). See [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md).

### workgroup_uniform_control_flow_elect — Workgroup-uniform control flow using elect

The branch is registered from `TT_WUCF_ELECT` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). Both subgroup-uniform and workgroup-uniform generated branches are gated by `shaderSubgroupUniformControlFlow` when classified by `CaseDef::isUCF()` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L109-L124), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4428-L4430). See [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md).

### workgroup_uniform_control_flow_ballot — Workgroup-uniform control flow using ballot

The branch is registered from `TT_WUCF_BALLOT` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It combines uniform-control-flow feature gating with ballot operation support [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4404-L4408), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4428-L4430). See [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md).

### maximal — Maximal reconvergence

The branch is registered from `TT_MAXIMAL` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803). It registers compute and fragment children in the current build configuration [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7825). Maximal generated shaders emit `GL_EXT_maximal_reconvergence` and require `shaderMaximalReconvergence` support [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4553-L4561), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4432-L4433). See [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md).

### terminate_invocation — Terminated invocation behavior

The main factory appends the `terminate_invocation` branch by calling `createTerminateInvocationTests(testCtx)` [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7943-L7947). That file registers `bit_count`, `terminate_helpers`, `oob_read`, and `quad_any` [vktReconvergenceTerminateInvocationTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675). See [vktReconvergenceTerminateInvocationTests](../testfiles/reconvergence/vktReconvergenceTerminateInvocationTests.md).

## File Inventory

| Wiki page | Source role | Registered path roots |
|-----------|-------------|-----------------------|
| [vktReconvergenceTests](../testfiles/reconvergence/vktReconvergenceTests.md) | Category root and generated reconvergence implementation | `reconvergence` |
| [vktReconvergenceTerminateInvocationTests](../testfiles/reconvergence/vktReconvergenceTerminateInvocationTests.md) | Delegated terminate-invocation implementation | `reconvergence.terminate_invocation` |

## Recurring Parameter Dimensions

| Theme | Observed dimensions | Evidence |
|-------|---------------------|----------|
| Test type | Five generated reconvergence branches: two subgroup-uniform, two workgroup-uniform, and one maximal | [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7797-L7803) |
| Shader stages | Compute for generated branches; fragment also appears for maximal; additional graphics stages are behind disabled `INCLUDE_GRAPHICS_TESTS` | [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L69-L69), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7805-L7814) |
| Nesting and seeds | Generated cases use nesting groups and eight seed groups; non-maximal branches skip nesting 5 and 6 | [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7837-L7872), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7842-L7848) |
| Main vs experimental split | Main and experimental packages split generated cases by index, with indexes below one fifth of each generated set assigned to the main tree and the remaining four fifths assigned to the experimental tree | [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L7929-L7933), [vktTestPackage.cpp](../../modules/vulkan/vktTestPackage.cpp#L1403-L1407) |
| Terminate-invocation subcases | `bit_count`, `terminate_helpers`, `oob_read`, and `quad_any` | [vktReconvergenceTerminateInvocationTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L653-L675) |

## Recurring Support Requirements

Generated reconvergence cases require Vulkan 1.1, selected-stage subgroup support, elect or ballot subgroup operation support, and the corresponding reconvergence feature gate (`shaderSubgroupUniformControlFlow` or `shaderMaximalReconvergence`) [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L4395-L4433). Terminate-invocation cases require fragment-stage subgroup support, basic subgroup operations, `VK_KHR_shader_quad_control`, subcase-specific ballot or vote operations, and in selected subcases `VK_KHR_shader_maximal_reconvergence` [vktReconvergenceTerminateInvocationTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L196-L226).

## Recurring Verification Methods

Generated reconvergence tests execute shader-generated random programs, simulate expected behavior on the CPU, and compare GPU output buffers with CPU references [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L5278-L5314), [vktReconvergenceTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTests.cpp#L6341-L6367). Terminate-invocation tests render to a color attachment, copy it back, construct reference images per subcase, and compare with `tcu::floatThresholdCompare` [vktReconvergenceTerminateInvocationTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L560-L571), [vktReconvergenceTerminateInvocationTests.cpp](../../modules/vulkan/reconvergence/vktReconvergenceTerminateInvocationTests.cpp#L574-L648).

## Scope Notes

The Level-3 scope contains only the two source files that register tests in this category; no helper-only reconvergence source file was found in the category build inventory [CMakeLists.txt](../../modules/vulkan/reconvergence/CMakeLists.txt#L7-L12).
