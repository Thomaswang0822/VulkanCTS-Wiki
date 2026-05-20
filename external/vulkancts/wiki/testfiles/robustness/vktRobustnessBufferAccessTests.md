# vktRobustnessBufferAccessTests.cpp

## Overview

This page documents the Vulkan CTS robustness buffer-access implementation in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1-L24).
The file generates robustness tests for out-of-bounds access through uniform buffers, storage buffers, uniform texel
buffers, and storage texel buffers. It registers one Vulkan and Vulkan SC group, `robustness.buffer_access`, and two
non-VulkanSC groups, `robustness.pipeline_robustness_buffer_access` and
`robustness.descriptor_heap_buffer_access`, through the same shared builder
[addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2095).

## Role of file

[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp) is an
implementation-heavy test file with local registration functions. The root robustness dispatcher registers its factories
under the `robustness` category: `createBufferAccessTests()` is unconditional, while
`createPipelineRobustnessBufferAccessTests()` and `createDescriptorHeapBufferAccessTests()` are registered only outside
Vulkan SC builds in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L95).

The implementation uses one parameterized generator to build the stage, shader-access, format, access-type, and range
matrix for all three roots. The three roots differ mainly in feature/device setup flags passed to
[addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2097-L2119): regular
robust buffer access uses `testPipelineRobustness=false` and `testDescriptorHeaps=false`; pipeline robustness uses
`testPipelineRobustness=true`; descriptor-heap coverage uses `testDescriptorHeaps=true`.

## Source code link

- Source: [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp)
- Header declarations: [vktRobustnessBufferAccessTests.hpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.hpp#L35-L37)
- Root robustness dispatcher: [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L49-L65) | Local shader-type and buffer-access-type enums used by the generated cases. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L281-L316) | Fixed accessed byte counts and common support checks. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L318-L699) | Generated GLSL for buffer and texel-buffer access in compute, vertex, and fragment stages. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L721-L905) | Per-test device creation, robust-buffer-access, pipeline-robustness, and descriptor-heap feature setup. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L918-L1536) | Buffer, descriptor-set, descriptor-heap, compute, and graphics environment setup. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1543-L1851) | Result verification and pass/fail criteria. |
| [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2122) | Registration hierarchy, generated child names, parameter arrays, and the three root factory functions. |
| [vktRobustnessBufferAccessTests.hpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.hpp#L35-L37) | Public declarations for the three factory functions. |
| [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L95) | Category-level registration and non-VulkanSC guards for the two extension-specific roots. |
| [vktRobustnessUtil.hpp](../../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L41-L54) | Helper declarations for custom robust devices and verification predicates used by this file. |
| [vktRobustnessUtil.hpp](../../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L56-L149) | Shared `TestEnvironment`, `GraphicsEnvironment`, `ComputeEnvironment`, and descriptor-heap parameter support. |
| [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L158) | Custom device creation with robust buffer access enabled by default. |
| [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L166-L243) | Helper checks for zero values, values sourced from the input buffer, and allowed out-of-bounds vec4 patterns. |
| [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L245-L305) | Input-buffer test-value population and value logging. |
| [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L42-L449) | Mustpass examples for regular `buffer_access` cases and direct children. |

## Registration Hierarchy

### `robustness.buffer_access`

```text
robustness.buffer_access
├── compute
├── fragment
├── through_pointers (registered into this root by vktRobustnessTests.cpp; implemented in another file)
└── vertex
```

The `compute`, `fragment`, and `vertex` children are added by
[addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1939-L1973) and released
to the parent in [addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2091-L2094).
The `through_pointers` child is not implemented by this file; it is inserted below the existing `buffer_access` node by
the root dispatcher in [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82), so it
is listed here only to keep the canonical one-level tree accurate for the registered root.

### `robustness.pipeline_robustness_buffer_access` (non-VulkanSC only)

```text
robustness.pipeline_robustness_buffer_access
├── compute
├── fragment
└── vertex
```

This root is compiled and registered only when `CTS_USES_VULKANSC` is not defined. It is created with the literal group
name `pipeline_robustness_buffer_access` and populated by the shared builder with `testPipelineRobustness=true` in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2106-L2114).

### `robustness.descriptor_heap_buffer_access` (non-VulkanSC only)

```text
robustness.descriptor_heap_buffer_access
├── compute
├── fragment
└── vertex
```

This root is also compiled and registered only when `CTS_USES_VULKANSC` is not defined. It is created with the literal
group name `descriptor_heap_buffer_access` and populated by the shared builder with `testDescriptorHeaps=true` in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2116-L2122).

## Test Families

### compute

The `compute` child runs the same buffer-access matrix through a compute shader. The generator maps
`VK_SHADER_STAGE_COMPUTE_BIT` to the registered child name `compute` and emits a GLSL compute shader with local size
`1,1,1` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1906-L1915)
and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L609-L626).
Runtime execution uses a `ComputeEnvironment` when the selected stage is compute in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1465-L1469).

### fragment

The `fragment` child runs the matrix through a graphics pipeline where the tested buffer access occurs in the fragment
shader. The stage name comes from `getShaderStageName()` and fragment shader source is generated when
`shaderStage == VK_SHADER_STAGE_FRAGMENT_BIT` in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1906-L1915)
and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L669-L685).
Runtime execution uses `GraphicsEnvironment` for non-compute stages in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1471-L1535).

### vertex

The `vertex` child runs the matrix through a graphics pipeline where the tested buffer access occurs in the vertex
shader. Vertex-stage source is generated when `shaderStage == VK_SHADER_STAGE_VERTEX_BIT` in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L632-L651), and
the graphics environment supplies a small vertex buffer and draw configuration in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1475-L1535).

### through_pointers

`through_pointers` is a direct child of `robustness.buffer_access` in the registered tree, but it is not implemented by
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp). The child is
inserted by the root dispatcher after it finds or creates the `buffer_access` node in
[vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L69-L82). This page does not document
that subgroup's generated tests beyond listing it in the parseable tree for the `buffer_access` root.

### Nested shader-access families generated under each stage

Under each implemented stage child, [addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1974-L2091)
creates these shader-access children from `shaderTypeNames`: `mat4_copy`, `vec4_copy`, `vec4_member_copy`,
`scalar_copy`, and `texel_copy`. The non-texel shader paths generate storage/uniform-buffer GLSL declarations and copy
patterns for matrices, vectors, vector members, and scalars in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L318-L517).
The texel path generates texture/image buffer declarations and copies texels with `texelFetch` or `imageLoad` followed
by `imageStore` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L519-L574).

For each supported format child, the builder creates `oob_uniform_read`, `oob_storage_read`, and `oob_storage_write`
subgroups in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2023-L2058).
For each shader-access child, it also creates an `out_of_alloc` subgroup containing tests named `oob_uniform_read`,
`oob_storage_read` outside pipeline-robustness mode, and `oob_storage_write` in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2063-L2089).

Pipeline-robustness roots intentionally reduce duplication: only selected formats are kept, and storage-buffer read
children are skipped when `testPipelineRobustness` is true in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2015-L2021)
and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2045-L2049).

## Parameter dimensions and observed values

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Root mode | `buffer_access`; `pipeline_robustness_buffer_access`; `descriptor_heap_buffer_access` | Factory functions and flags in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2097-L2122). |
| Shader stage / direct child | `vertex`, `fragment`, `compute` | Stage array and name mapping in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1906-L1943). |
| Shader access type | `mat4_copy`, `vec4_copy`, `vec4_member_copy`, `scalar_copy`, `texel_copy` | `ShaderType` enum and name array in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L49-L58) and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1965-L1967). |
| Non-texel formats | `r32_sint`, `r32_uint`, `r64_sint`, `r64_uint`, `r32_sfloat` | `bufferFormats` array and lower-cased format-name group construction in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1945-L1946) and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2023-L2025). |
| Texel-buffer formats | `r32g32b32a32_sint`, `r32g32b32a32_uint`, `r32g32b32a32_sfloat`, `a2b10g10r10_unorm_pack32` | `texelBufferFormats` array in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1948-L1951). |
| Non-texel range names and values | `range_1_byte` = 1 byte, `range_3_bytes` = 3 bytes, `range_4_bytes` = 4 bytes, `range_32_bytes` = 32 bytes | `bufferRangeConfigs` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1953-L1958). |
| Texel range names and values | `range_1_texel`, `range_3_texels`, multiplied by texel byte size for buffer ranges | `texelBufferRangeConfigs` and `rangeMultiplier` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1960-L1963) and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2005-L2007). |
| Access operation subgroup | `oob_uniform_read`, `oob_storage_read`, `oob_storage_write` | Subgroup construction in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2027-L2058). |
| Out-of-allocation subgroup | `out_of_alloc` containing `oob_uniform_read`, conditionally `oob_storage_read`, and `oob_storage_write` | Out-of-allocation branch in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2063-L2089). |
| Accessed byte count | 64 bytes for most shader types; 16 bytes for `vec4_member_copy` | Static constants and `getNumberOfBytesAccesssed()` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L72-L93) and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L281-L284). |
| Test array/vector sizes | `s_testArraySize = 128`; `s_testVectorSize = 4` | Static constants in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L281-L284). |

Observed exclusions and reductions:

- `mat4_copy` is generated only for floating-point formats; non-float formats break out of that format loop in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2009-L2013).
- `vec4_member_copy` skips ranges whose byte size is greater than 16 in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2031-L2039).
- Pipeline-robustness mode keeps only `VK_FORMAT_R32_UINT`, `VK_FORMAT_R64_SINT`, `VK_FORMAT_R32_SFLOAT`, and
  `VK_FORMAT_A2B10G10R10_UNORM_PACK32` among the candidate formats in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2015-L2021).
- Pipeline-robustness mode does not add `oob_storage_read` children for regular range cases or out-of-allocation cases
  in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2045-L2049)
  and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2078-L2082).

## Support / feature requirements

- If `VK_KHR_portability_subset` is supported, the test requires `robustBufferAccess` to be supported by the
  implementation in [RobustBufferAccessTest::checkSupport()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L301-L307).
- Tests using `VK_FORMAT_R64_SINT` or `VK_FORMAT_R64_UINT` require `shaderInt64` in
  [RobustBufferAccessTest::checkSupport()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L308-L310)
  and emit `GL_EXT_shader_explicit_arithmetic_types_int64` in the generated shader source in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L599-L602).
- Vertex-stage and fragment-stage tests require `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`,
  respectively, in [RobustBufferAccessTest::checkSupport()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L311-L315).
  The instance constructor repeats runtime store-support checks for vertex and fragment stages in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L965-L979).
- Regular non-pipeline-robustness tests request a custom device with `robustBufferAccess` enabled in
  [RobustBufferReadTest::createInstance()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L727-L775)
  and [RobustBufferWriteTest::createInstance()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L829-L882).
  The helper also sets `enabledFeatures.robustBufferAccess = true` before custom device creation in
  [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L85-L92).
- `pipeline_robustness_buffer_access` requires `VK_EXT_pipeline_robustness` and uses
  `VkPhysicalDevicePipelineRobustnessFeaturesEXT` in read and write instance creation in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L741-L751)
  and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L843-L856).
- `descriptor_heap_buffer_access` requires `VK_EXT_descriptor_heap` and `VK_KHR_buffer_device_address`, and enables
  descriptor-heap and buffer-device-address feature structures in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L753-L768)
  and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L858-L875).
- For 64-bit formats, the instance constructor requires `VK_EXT_shader_image_atomic_int64` in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L960-L963).
- Texel-buffer cases require both storage-texel-buffer and uniform-texel-buffer format support before running, as checked
  in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L981-L999).
- Out-of-allocation cases may be skipped if the allocation is too large to permit the intended access beyond the backing
  memory, as guarded in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1083-L1095).

## Verification methods

The test writes known input data, executes one compute dispatch or graphics draw, invalidates the output allocation, and
then validates the output memory. Input buffers are populated with deterministic nonzero/non-one values by
[populateBufferWithTestValues()](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L245-L277); output buffers are
initialized to `0xFF` in [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1100-L1104).
The command buffer is submitted and waited on in [BufferAccessInstance::iterate()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1591-L1613),
and the output allocation is invalidated before verification in
[vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1615-L1626).

[BufferAccessInstance::verifyResult()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1634-L1851)
then checks every 4-byte output slot:

- Bytes beyond the shader's intended write footprint must remain unchanged, except that out-of-bounds writes are allowed
  to place a value that is either within the input buffer or zero, as checked in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1651-L1661).
- In-bounds reads must reproduce the expected deterministic input value according to format-specific comparison in
  [isExpectedValueFromInBuffer()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1543-L1581) and
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1826-L1835).
- Out-of-bounds reads must produce either a value from the backing input buffer or zero; partial out-of-bounds accesses
  validate the in-bounds and out-of-bounds byte portions separately in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1727-L1761).
- Out-of-bounds writes must leave the destination bytes unchanged or, where allowed by the memory range backing the
  buffer, write a value that is within the input buffer or zero in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1763-L1783).
- Some out-of-bounds vector reads may also match the accepted `[0, 0, 0, x]` pattern, with `x` constrained by format; the
  local verifier delegates this pattern to
  [verifyOutOfBoundsVec4()](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L215-L243) through
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1785-L1807).

The final result is `pass("All values OK")` or `fail("Invalid value(s) found")` based on `verifyResult()` in
[BufferAccessInstance::iterate()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1628-L1631).

## Test principles observed in the file

- Use one shared registration matrix for related robustness modes, then vary only feature setup and selected reductions
  through `testPipelineRobustness` and `testDescriptorHeaps` flags in
  [addBufferAccessTests()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1930-L2095).
- Exercise multiple shader stages with equivalent access patterns so robustness behavior is checked in compute and
  graphics pipelines, as shown by the stage array and compute/graphics environment split in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1939-L1943)
  and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1465-L1536).
- Cover several access granularities: scalar, vector, member-by-member vector, matrix, and texel-buffer copies are
  represented by local shader-generation branches in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L318-L574).
- Test both descriptor range limits and backing-allocation limits. Regular range cases shrink the descriptor/buffer view
  range, while `out_of_alloc` cases move indices near the end of the test array/vector to reach beyond backing memory in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1023-L1042),
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1066-L1098),
  and [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1154-L1178).
- Keep verification permissive only where robustness rules allow implementation variation: out-of-bounds reads may be
  zero or an in-bounds value, and out-of-bounds writes must not introduce unknown values outside allowed ranges, as
  encoded in [BufferAccessInstance::verifyResult()](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1634-L1851).
- Descriptor-heap mode replaces normal descriptor-set updates with a resource heap, buffer-device addresses, resource
  descriptor writes, and binding mappings in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L1284-L1448),
  while keeping the same shader and verification logic.

## Notes / uncertainties

- The `robustness.buffer_access` canonical tree includes `through_pointers` because it is a registered direct child of
  that root in the inspected root dispatcher and mustpass list, but that child is not implemented in
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp). Its internal
  cases are intentionally not documented on this page.
- The observed mustpass file contains many generated leaves under the documented roots. This page summarizes the source
  generation logic rather than enumerating every generated leaf.
- The accepted result sets are documented from the local verifier and helper utilities. This page does not make broader
  Vulkan specification claims beyond what the inspected code checks.
- Pipeline-robustness and descriptor-heap roots are non-VulkanSC because both the root dispatcher registration and the
  corresponding factory definitions are guarded by `#ifndef CTS_USES_VULKANSC` in
  [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L86-L95) and
  [vktRobustnessBufferAccessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessBufferAccessTests.cpp#L2106-L2123).
