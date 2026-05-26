# vktSpvAsmTerminateInvocationTests

## Overview

Tests for [`VK_KHR_shader_terminate_invocation`](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L112-L114), verifying that terminated invocations do not perform subsequent output, SSBO, image, or invalid-pointer accesses, and checking subgroup participation cases registered from Amber files.

## Role

Implementation file

## Source

- [vktSpvAsmTerminateInvocationTests.cpp](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L110)

## Registration Hierarchy

```text
spirv_assembly.instruction.terminate_invocation
└── terminate
```

## Test Families

### no_output_write — No write to output after terminate invocation

Verifies the `no_output_write` Amber case registered by this file; the source adds the case name to the `terminate` group before creating Amber test cases from the `spirv_assembly/instruction/terminate_invocation` data directory ([case list](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L132-L135), [Amber creation](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L77-L103)).

### no_output_write_before_terminate — No output write despite occurring before terminate

Verifies the `no_output_write_before_terminate` case described in source as an output write occurring before terminate invocation ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L135-L136)).

### no_ssbo_store — No SSBO store after terminate

Verifies that SSBO stores after terminate invocation are not executed; the case is registered with the `Features.fragmentStoresAndAtomics` requirement ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L117-L119), [case](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L137-L138)).

### no_ssbo_atomic — No SSBO atomic after terminate

Verifies that SSBO atomic operations after terminate invocation are not executed and uses the same store/atomic feature requirement ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L139-L140)).

### ssbo_store_before_terminate — SSBO store commits before terminate

Verifies that SSBO stores occurring before terminate invocation are committed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L141-L142)).

### no_image_store — No image store after terminate

Verifies that image stores after terminate invocation are not executed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L143-L144)).

### no_image_atomic — No image atomic after terminate

Verifies that image atomic operations after terminate invocation are not executed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L145-L146)).

### no_null_pointer_load — No null pointer load in terminated invocation

Verifies that a null pointer load in a terminated invocation is not accessed; this pointer-access group carries `VariablePointerFeatures.variablePointersStorageBuffer` and `Features.fragmentStoresAndAtomics` ([requirements](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L120-L123), [case](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L147-L148)).

### no_null_pointer_store — No null pointer store in terminated invocation

Verifies that a null pointer store in a terminated invocation is not accessed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L149-L150)).

### no_out_of_bounds_load — No out-of-bounds load in terminated invocation

Verifies that out-of-bounds pointer loads in terminated invocations are not accessed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L151-L152)).

### no_out_of_bounds_store — No out-of-bounds store in terminated invocation

Verifies that out-of-bounds pointer stores in terminated invocations are not accessed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L153-L154)).

### no_out_of_bounds_atomic — No out-of-bounds atomic in terminated invocation

Verifies that out-of-bounds atomic operations in terminated invocations are not accessed ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L155-L156)).

### terminate_loop — Infinite loop that calls terminate invocation

Tests an "infinite" loop containing terminate invocation ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L157-L158)).

### subgroup_ballot — Terminated invocations don't participate in ballot

Verifies that terminated invocations do not participate in subgroup ballot operations; the case uses SPIR-V 1.3 build options and requires `SubgroupSupportedOperations.ballot` and `SubgroupSupportedStages.fragment` ([requirements](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L128-L130), [case](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L159-L160), [SPIR-V selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L86-L88)).

### subgroup_vote — Terminated invocations don't participate in vote

Verifies that terminated invocations are not included in subgroup vote operations; the case uses SPIR-V 1.3 build options and requires `SubgroupSupportedOperations.vote` and `SubgroupSupportedStages.fragment` ([requirements](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L124-L126), [case](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L161-L162), [SPIR-V selection](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L86-L88)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Amber case | `no_output_write`, `no_output_write_before_terminate`, `no_ssbo_store`, `no_ssbo_atomic`, `ssbo_store_before_terminate`, `no_image_store`, `no_image_atomic`, `no_null_pointer_load`, `no_null_pointer_store`, `no_out_of_bounds_load`, `no_out_of_bounds_store`, `no_out_of_bounds_atomic`, `terminate_loop`, `subgroup_ballot`, `subgroup_vote` | Direct case list registered into the `terminate` subgroup ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L132-L162)) |
| SPIR-V version | 1.0 for ordinary cases, 1.3 for subgroup cases | `spv1p3` controls the API/SPIR-V build options ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L86-L88)) |
| Requirement bundle | Stores, VarPtr, Vote, Ballot | Requirement vectors attached per case ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L117-L130)) |

## Support Requirements

- `VK_KHR_shader_terminate_invocation` extension is added to every Amber case ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L90-L99)).
- `Features.fragmentStoresAndAtomics` is used by store/image/atomic and pointer-access cases through the `Stores` and `VarPtr` requirement vectors ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L117-L123)).
- `VariablePointerFeatures.variablePointersStorageBuffer` is used by pointer-access cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L120-L123)).
- `SubgroupSupportedOperations.vote` / `SubgroupSupportedStages.fragment` and `SubgroupSupportedOperations.ballot` / `SubgroupSupportedStages.fragment` gate the subgroup cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L124-L130)).

## Verification Methods

All cases are Amber-based: the file constructs `.amber` filenames from each registered basename and calls `cts_amber::createAmberTestCase`, so verification is provided by the Amber data files in `spirv_assembly/instruction/terminate_invocation/` ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L77-L103)).

## Notes

- The `terminate` subgroup wraps all individual test cases ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L163-L165)).
- The group is excluded from Vulkan SC by the surrounding `#ifndef CTS_USES_VULKANSC` guard ([source](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L75-L106), [registration guard](../../../modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp#L163-L165)).
