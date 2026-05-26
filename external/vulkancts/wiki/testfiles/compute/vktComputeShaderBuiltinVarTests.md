# vktComputeShaderBuiltinVarTests.cpp

## Overview

[`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L635-L679) registers the `builtin_var` group. It verifies compute shader built-ins by comparing shader-written results against host-side reference values for different workgroup and local invocation coordinates.

## Role

Implementation file.

## Source Code

- Primary source: [`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L1)
- Factory declaration: [`vktComputeShaderBuiltinVarTests.hpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.hpp#L36-L37)

## Registration Hierarchy

```text
compute.pipeline.builtin_var
├── num_work_groups
├── work_group_size
├── work_group_id
├── local_invocation_id
├── global_invocation_id
├── num_work_groups_component
├── work_group_size_component
├── work_group_id_component
├── local_invocation_id_component
├── global_invocation_id_component
└── local_invocation_index
```

## Test Families

### num_work_groups — `gl_NumWorkGroups`

`NumWorkGroupsCase` is added for whole-vector and component-wise reads in the initialization loop ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L664)).

### work_group_size — `gl_WorkGroupSize`

`WorkGroupSizeCase` is also added for both vector and component reads ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L665)).

### work_group_id — `gl_WorkGroupID`

`WorkGroupIDCase` verifies the workgroup coordinates observed by the shader ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L663-L666)).

### local_invocation_id — `gl_LocalInvocationID`

`LocalInvocationIDCase` verifies local invocation coordinates for both read modes ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L663-L667)).

### global_invocation_id — `gl_GlobalInvocationID`

`GlobalInvocationIDCase` is added in both vector and component modes ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L667-L668)).

### local_invocation_index — `gl_LocalInvocationIndex`

The scalar local-invocation-index case is added once because the source comments that it is already scalar ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L670-L671)).

## Parameter Dimensions

The main dimension is read mode: vector-valued built-ins are read as whole vectors and by component via a two-iteration loop ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L668)). Scalar `local_invocation_index` is not duplicated ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L670-L671)).

## Support / Feature Requirements

Each built-in case checks shader-object requirements according to the selected compute pipeline construction type ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L169-L173)). No additional feature gate was observed in this file.

## Verification Methods

The test instance computes host-side reference values for each workgroup/local-invocation combination, reads shader results from the result buffer, compares the active scalar components, logs mismatches, and fails if any comparison differs ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L600-L632)).

## Test Principles Observed

- The file is a direct implementation of the test-plan goal that workgroup counts and invocation IDs are passed correctly to compute shader invocations ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L679)).
- Vector built-ins are tested through both aggregate and per-component reads to catch access-form issues ([`vktComputeShaderBuiltinVarTests.cpp`](../../../modules/vulkan/compute/vktComputeShaderBuiltinVarTests.cpp#L657-L660)).

## Notes / Uncertainties

- The direct case names are inferred from the case classes and current CTS naming convention; validation confirms the listed registration prefixes in mustpass data.
