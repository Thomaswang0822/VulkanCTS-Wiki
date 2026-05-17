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

## Registration Hierarchy

```text
shader_object.api
├── get_device_proc_addr
├── discard_rectangles
├── scissor_exclusive
├── dynamic_rendering
└── shader_binary_uuid
```

Evidence: `createShaderObjectApiTests()` constructs the group named `api`, adds `get_device_proc_addr`, and iterates `apiTests[]` to add four named extension/property cases at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L354-L374).

## Test Families

### get_device_proc_addr — Device function lookup

Creates a custom device with `VK_EXT_shader_object` in the enabled extension list and then checks a list of shader-object-relevant dynamic-state function names with the device driver; the extension list and custom device setup are visible at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L83-L106).

### discard_rectangles — EXT_discard_rectangles extension-version check

Checks the minimum reported spec version for `VK_EXT_discard_rectangles` when the extension is present at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L281-L313). Requires `VK_EXT_discard_rectangles` in addition to `VK_EXT_shader_object`.

### scissor_exclusive — NV_scissor_exclusive extension-version check

Checks the minimum reported spec version for `VK_NV_scissor_exclusive` when the extension is present at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L281-L313). Requires `VK_NV_scissor_exclusive` in addition to `VK_EXT_shader_object`.

### dynamic_rendering — KHR_dynamic_rendering availability check

Checks `VK_KHR_dynamic_rendering` availability for Vulkan versions below 1.3 at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L256-L276). Fails if Vulkan version is below 1.3 and `VK_KHR_dynamic_rendering` is absent while shader object is supported.

### shader_binary_uuid — Nonzero shaderBinaryUUID property check

Checks that `shaderBinaryUUID` is not all zero bytes at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L239-L254). The `ShaderObjectApiTest` enum defines this and the other extension/property checks at [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L42-L48).

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
