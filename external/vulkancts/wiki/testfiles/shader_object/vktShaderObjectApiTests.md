# [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L1)

## Overview

[`vktShaderObjectApiTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L1) implements the `shader_object/api` branch. The branch checks shader-object-related API exposure, required dynamic-state command lookup through a custom device, selected extension-version expectations, dynamic-rendering availability, and nonzero `shaderBinaryUUID` property behavior.

## Role of File

Implementation-heavy test file for the root-level `api` branch.

## Source Code

- Primary source: [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L51)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- api
    +-- get_device_proc_addr
    +-- discard_rectangles
    +-- scissor_exclusive
    +-- dynamic_rendering
    +-- shader_binary_uuid
```

Explicit registration path prefixes for verifier extraction:

```text
`shader_object.api`
`shader_object.api.get_device_proc_addr`
`shader_object.api.discard_rectangles`
`shader_object.api.scissor_exclusive`
`shader_object.api.dynamic_rendering`
`shader_object.api.shader_binary_uuid`
```

Evidence: `createShaderObjectApiTests()` constructs the group named `api`, adds `get_device_proc_addr`, and iterates `apiTests[]` to add four named extension/property cases at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L354-L374).

## Test Hierarchy

```text
api
+-- get_device_proc_addr
+-- discard_rectangles
+-- scissor_exclusive
+-- dynamic_rendering
+-- shader_binary_uuid
```

## Test Families

### Device function lookup

`get_device_proc_addr` creates a custom device with `VK_EXT_shader_object` in the enabled extension list and then checks a list of shader-object-relevant dynamic-state function names with the device driver; the extension list and custom device setup are visible at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L83-L106).

### Extension-version and property checks

The `ShaderObjectApiTest` enum defines four extension/property checks at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L42-L48). `ShaderObjectExtensionVersionInstance::iterate()` checks `shaderBinaryUUID`, `VK_KHR_dynamic_rendering` availability for Vulkan versions below 1.3, and minimum reported versions for `VK_EXT_discard_rectangles` and `VK_NV_scissor_exclusive` when those extensions are present at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L215-L315).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| API extension/property selector | `EXT_DISCARD_RECTANGLES`, `NV_SCISSOR_EXCLUSIVE`, `KHR_DYNAMIC_RENDERING`, `SHADER_BINARY_UUID` at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L42-L48) |
| Registered extension/property case names | `discard_rectangles`, `scissor_exclusive`, `dynamic_rendering`, `shader_binary_uuid` at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L363-L368) |
| Base device function case | `get_device_proc_addr` at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L357) |

## Support / Feature Requirements

- All cases require `VK_EXT_shader_object` through `checkSupport()` at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L192-L195) and [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L340-L342).
- `discard_rectangles` additionally requires `VK_EXT_discard_rectangles`; `scissor_exclusive` additionally requires `VK_NV_scissor_exclusive` at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L343-L350).

## Verification Methods

- Fail if `shaderBinaryUUID` is all zero bytes at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L239-L254).
- Fail if Vulkan version is below 1.3 and `VK_KHR_dynamic_rendering` is absent while shader object is supported at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L256-L276).
- Fail if supported discard-rectangle or exclusive-scissor extensions report a spec version below 2 at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L281-L313).

## Test Principles Observed

- Validate API and property consistency around `VK_EXT_shader_object` before deeper rendering tests.
- Separate mandatory shader-object support from optional extension-specific checks.

## Notes / Uncertainties

- The full list of dynamic-state function names checked by `get_device_proc_addr` extends beyond the inspected excerpt; this document describes the observed setup and purpose without enumerating every function.
