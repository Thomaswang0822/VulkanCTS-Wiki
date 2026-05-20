# vktSpvAsmTerminateInvocationTests

## Overview

Tests for VK_KHR_shader_terminate_invocation, verifying that terminated invocations do not perform subsequent writes to outputs, SSBOs, images, or access invalid pointers, and that they correctly participate (or not) in subgroup operations.

## Role

Implementation file

## Source

- [vktSpvAsmTerminateInvocationTests.cpp](https://github.com/KhronosGroup/VK-GL-CTS/blob/main/external/vulkancts/modules/vulkan/spirv_assembly/vktSpvAsmTerminateInvocationTests.cpp)

## Registration Hierarchy

```text
spirv_assembly.instruction.terminate_invocation
└── terminate
```

## Test Families

### no_output_write — No write to output after terminate invocation

Verifies that an output write occurring after `OpTerminateInvocation` is not executed. Source: `vktSpvAsmSpirvVersion1p4Tests.cpp` pattern, Amber-based.

### no_output_write_before_terminate — No output write despite occurring before terminate

Verifies that an output write before `OpTerminateInvocation` that would be conditionally reached is correctly handled.

### no_ssbo_store — No SSBO store after terminate

Verifies that SSBO stores after `OpTerminateInvocation` are not executed. Requires `fragmentStoresAndAtomics`.

### no_ssbo_atomic — No SSBO atomic after terminate

Verifies that SSBO atomic operations after `OpTerminateInvocation` are not executed.

### ssbo_store_before_terminate — SSBO store commits before terminate

Verifies that SSBO stores occurring before `OpTerminateInvocation` are correctly committed.

### no_image_store — No image store after terminate

Verifies that image stores after `OpTerminateInvocation` are not executed.

### no_image_atomic — No image atomic after terminate

Verifies that image atomic operations after `OpTerminateInvocation` are not executed.

### no_null_pointer_load — No null pointer load in terminated invocation

Verifies that a null pointer load in a terminated invocation is not accessed. Requires variable pointers and fragmentStoresAndAtomics.

### no_null_pointer_store — No null pointer store in terminated invocation

Verifies that a null pointer store in a terminated invocation is not accessed.

### no_out_of_bounds_load — No out-of-bounds load in terminated invocation

Verifies that out-of-bounds pointer loads in terminated invocations are not accessed.

### no_out_of_bounds_store — No out-of-bounds store in terminated invocation

Verifies that out-of-bounds pointer stores in terminated invocations are not accessed.

### no_out_of_bounds_atomic — No out-of-bounds atomic in terminated invocation

Verifies that out-of-bounds atomic operations in terminated invocations are not accessed.

### terminate_loop — Infinite loop that calls terminate invocation

Tests that an "infinite" loop containing `OpTerminateInvocation` correctly terminates the invocation.

### subgroup_ballot — Terminated invocations don't participate in ballot

Verifies that terminated invocations do not participate in subgroup ballot operations. Requires SPIR-V 1.3, subgroup ballot and fragment stage support.

### subgroup_vote — Terminated invocations don't participate in vote

Verifies that terminated invocations are not included in subgroup all/any vote operations. Requires SPIR-V 1.3, subgroup vote and fragment stage support.

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| Write type | output, SSBO store, SSBO atomic, image store, image atomic | The type of write operation being tested |
| Pointer access | null load, null store, OOB load, OOB store, OOB atomic | The type of pointer access being tested |
| Subgroup op | ballot, vote | The subgroup operation being tested |
| SPIR-V version | 1.0 (most tests), 1.3 (subgroup tests) | Required SPIR-V version |

## Support Requirements

- `VK_KHR_shader_terminate_invocation` extension (added to all tests at `vktSpvAsmTerminateInvocationTests.cpp#L94`)
- `Features.fragmentStoresAndAtomics` for SSBO/image tests
- `VariablePointerFeatures.variablePointersStorageBuffer` for pointer access tests
- `SubgroupSupportedOperations.vote` / `SubgroupSupportedStages.fragment` for subgroup vote tests
- `SubgroupSupportedOperations.ballot` / `SubgroupSupportedStages.fragment` for subgroup ballot tests

## Verification Methods

All tests are Amber-based. Verification is handled by the Amber test framework using `.amber` test files located in the `spirv_assembly/instruction/terminate_invocation/` data subdirectory. Source: `vktSpvAsmTerminateInvocationTests.cpp#L77-L104`.

## Notes

- All tests use Amber test framework
- The `terminate` sub-group wraps all individual test cases
- Non-VulkanSC only (guarded by `#ifndef CTS_USES_VULKANSC`)
