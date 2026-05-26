# [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L1)

## Overview

[`vktShaderObjectTests.cpp`](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L1) is the root registration file for the Vulkan CTS `shader_object` category. Its [`createTests()`](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) creates the category group from the caller-provided category name and directly registers ten root-level branches.

## Role of File

Registration/dispatcher file for the `shader_object` category.

## Source Code

- Primary source: [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L1)
- Root header: [vktShaderObjectTests.hpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.hpp#L1)
- Source inventory: [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Related Inspected Files

- [vktShaderObjectApiTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L354-L375)
- [vktShaderObjectCreateTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L879)
- [vktShaderObjectLinkTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650)
- [vktShaderObjectTessellationTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L929-L975)
- [vktShaderObjectBinaryTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L838-L947)
- [vktShaderObjectPipelineInteractionTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1552)
- [vktShaderObjectBindingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2200)
- [vktShaderObjectPerformanceTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1262-L1310)
- [vktShaderObjectRenderingTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1201-L1395)
- [vktShaderObjectMiscTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3498-L4080)

## Registration Hierarchy

```text
shader_object
├── api
├── create
├── link
├── tessellation
├── binary
├── pipeline_interaction
├── binding
├── performance (excluded from mustpass)
├── rendering
└── misc
```

Evidence: the root function directly calls `addChild()` for the ten branch factory functions at [vktShaderObjectTests.cpp](../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L51-L60). Each displayed branch name was verified from the corresponding implementation file's `TestCaseGroup` construction, not from the factory symbol alone. The inspected mustpass directory [`shader-object/`](../../../mustpass/main/vk-default/shader-object/) contains branch TXT files for `api`, `binary`, `binding`, `create`, `link`, `misc`, `pipeline-interaction`, `rendering`, and `tessellation`, but no `performance.txt`. The performance branch is source-registered in the root file but explicitly excluded from mustpass by [`excluded-tests.txt`](../../../mustpass/main/src/excluded-tests.txt) (glob `dEQP-VK.shader_object.performance.*`); it therefore has no mustpass TXT and is intentionally omitted from the mustpass directory.

## Test Families

### api — API and extension/property checks

Checks shader-object-related API exposure, required dynamic-state command lookup through a custom device, selected extension-version expectations, dynamic-rendering availability, and nonzero `shaderBinaryUUID` property behavior.

### create — Shader creation and stage creation behavior

Covers creating multiple shader objects together and per-stage shader creation cases that are expected either to succeed or fail.

### link — Linked/unlinked stage combinations and next-stage chains

Builds linked and unlinked shader-stage combinations, next-stage chain tests, separate-link tests, and mesh/task/fragment link combinations.

### tessellation — GLSL/HLSL tessellation shader-object rendering variants

Registers GLSL and HLSL tessellation shader-object tests for orientation, spacing, patch vertex count, primitive mode, and point mode, each with and without a rebind suffix.

### binary — Shader binary query/recreation/incompatibility/device-feature behavior

Covers shader binary queries, recreating shaders from binaries, incompatible or corrupted binary data, and device-feature bit variation when using shader binaries.

### pipeline_interaction — Switching between shader objects and pipelines

Tests switching between shader objects and pipelines.

### binding — Binding, swapping, disabling, and unbinding shader stages

Tests binding, swapping, disabling, and unbinding shader stages.

### performance — Timed draw/dispatch/binary operations

Timed draw/dispatch/binary operations.

### rendering — Dynamic rendering output/attachment format variants

Dynamic rendering output/attachment format variants.

### misc — State, unused variables, tessellation modes, push constants, and other cases

State, unused variables, tessellation modes, push constants, and other cases.

## Parameter Dimensions

No test parameters are defined in this dispatcher file. Parameters are defined by the branch implementation files listed above.

## Support / Feature Requirements

No root-level support gate is present around the ten branch registrations. Support requirements are implemented inside branch test cases, for example `VK_EXT_shader_object` in branch `checkSupport()` methods.

## Verification Methods

No pass/fail verification is implemented in this dispatcher file. Verification methods are implemented by branch `TestInstance::iterate()` functions and helper routines.

## Test Principles Observed

- Keep root category registration flat and delegate implementation to branch files.
- Register all ten branch groups unconditionally; defer feature/extension support decisions to test cases.
- Use separate files for branch-specific families and a separate utility library for shared shader-object creation helpers as listed in [CMakeLists.txt](../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44).

## Notes / Uncertainties

- The root group name is provided by the caller of `createTests()`; the category path `shader_object` is inferred from Vulkan CTS category registration and verified by mustpass path checking, not from a string literal in this file.
