# Understanding Brief: Shader module identifiers

## The Question This Family Answers

The `shader_module_identifier` family tests `VK_EXT_shader_module_identifier`. It asks whether a driver returns valid, stable identifiers for shader binaries and can use those identifiers in place of shader-module code during pipeline creation. The family also checks HLSL tessellation pipelines and optional executable-property capture.

## Concepts You Need Before Reading the Test

`vkGetShaderModuleIdentifierEXT` returns an identifier for an existing `VkShaderModule`. `vkGetShaderModuleCreateInfoIdentifierEXT` returns one for the same code through `VkShaderModuleCreateInfo`. A pipeline stage can carry `VkPipelineShaderStageModuleIdentifierCreateInfoEXT` instead of a module handle and code. The driver can use that identifier to look up a previously compiled shader.

The extension feature is `shaderModuleIdentifier` in `VkPhysicalDeviceShaderModuleIdentifierFeaturesEXT`; the CTS requires `VK_EXT_shader_module_identifier` before running a case. The [extension metadata](../../../scripts/src/extensions/VK_EXT_shader_module_identifier.json#L1) records that feature requirement.

An identifier must be a nonempty byte sequence no larger than `VK_MAX_SHADER_MODULE_IDENTIFIER_SIZE_EXT`. For the same shader code, the two query routes should agree. Different shader binaries in the cases must not collapse to one identifier. An identifier is not portable across devices, so the cross-device cases compare each query route on its own device only when the test asks for different devices.

## What the Test Varies

| Behavior parameter | Values | Why it matters |
|---|---|---|
| Test family | `properties`, `constant_identifiers`, `pipeline_from_id`, `hlsl_tessellation`, `misc` | Selects a property check, identifier-consistency check, runnable pipeline path, HLSL path, or maintenance5 capture path. |
| Pipeline type | compute, graphics, ray tracing, ray-tracing libraries | Selects pipeline creation and execution machinery. |
| Pipeline count | `1_variants`, `4_variants` | Creates one or several shader sets and selects the pipeline that runs. |
| Specialization constants | `no_spec_constants`, `use_spec_constants` | Checks identifier-backed stages with and without specialization data. |
| Identifier query route | `module_id`, `create_info_id`, `both_ids` | Chooses module-query, create-info-query, or cross-route consistency checks. |
| Device selection | `same_device`, `different_devices` | Exercises the alternate-device query path. |
| Pipeline cache | `no_pipeline_cache`, `use_pipeline_cache` | Changes cache use during identifier-backed creation. |
| Stage identifier payload | `use_id`, zero-length forms, all-zero, all-one, pseudorandom | Distinguishes a valid ID from invalid or deliberately empty payloads. |
| Capture selection | `no_exec_properties`, `capture_stats`, `capture_irs` | Compares executable properties between classic and identifier-backed pipelines. |

## How to Read a Result

For constant-identifier leaves, CTS creates shader modules when required, queries identifiers through the selected APIs, compares the results for the same binary, and inserts each identifier into a set. A mismatch for the same binary or a duplicate across different binaries fails.

For runnable `pipeline_from_id` leaves, CTS first creates ordinary pipelines and obtains stage identifiers. It then creates an equivalent pipeline with identifier structures attached to the stage data. Graphics cases render or write stage data, compute cases dispatch, and ray-tracing cases trace rays. The host compares the framebuffer when a fragment stage exists and compares the storage-buffer values written by each selected shader stage. Capture leaves also compare the sets of executable properties from classic and identifier-backed pipelines.

The HLSL tessellation case makes four tessellation-control variants, queries their IDs, builds pipelines from those IDs, draws one pixel per pipeline into a 2 by 2 image, and compares the four expected colors.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | The test observed | Likely fault area |
|---|---|---|
| `properties` | A changing or all-zero `shaderModuleIdentifierAlgorithmUUID` | Physical-device shader-module-identifier property query |
| `constant_identifiers` | The same binary returned different IDs, or different binaries shared an ID | Identifier generation or the module/create-info query path |
| `pipeline_from_id` with `use_id` | An identifier-backed pipeline fails to create, produces a wrong color, or writes wrong stage data | Identifier lookup, pipeline compilation, or stage substitution |
| `capture_stats` or `capture_irs` | Classic and identifier-backed executable-property sets differ | Pipeline executable capture or identifier-backed compilation metadata |
| `hlsl_tessellation` | IDs are not unique or the 2 by 2 output differs from the four expected colors | HLSL tessellation stage handling or identifier-backed graphics pipeline creation |
| Invalid or empty identifier forms | The result conflicts with the selected expected cache-miss or compile-required behavior | Validation of `VkPipelineShaderStageModuleIdentifierCreateInfoEXT` payloads or pipeline-cache handling |

### Limits of the Result

The output checks localize a failure to identifier production, identifier-backed pipeline creation, or a selected shader execution path. They do not identify the compiler, cache, or driver subsystem responsible. A compile-required outcome has case-specific handling: some leaves expect a cache miss, some pass it, and cache-use cases without executable capture can report a quality warning.

## Source Trail

- [Legacy navigation page](vktPipelineShaderModuleIdentifierTests.md)
- [Identifier helpers and support check](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L80)
- [Constant-identifier comparison](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L1570)
- [Identifier-backed runtime path and result checks](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L2025)
- [HLSL tessellation path](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L3258)
- [Family registration](../../../modules/vulkan/pipeline/vktPipelineShaderModuleIdentifierTests.cpp#L3737)
- [Extension feature requirement](../../../scripts/src/extensions/VK_EXT_shader_module_identifier.json#L1)
- Mustpass lists: `pipeline/monolithic/monolithic.txt`, `pipeline/fast-linked-library.txt`, and `pipeline/pipeline-library.txt`
