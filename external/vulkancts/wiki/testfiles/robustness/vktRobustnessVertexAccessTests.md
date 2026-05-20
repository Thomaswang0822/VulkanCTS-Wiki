# vktRobustnessVertexAccessTests

## Overview

This page documents the Vulkan CTS `robustness.vertex_access` group implemented by
[`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1-L1300).
The tests draw with deliberately undersized or partially valid vertex and instance input buffers while robust buffer
access is enabled, then verify that in-range vertex input values are preserved and out-of-range vertex input values are
limited to values allowed by the robustness rules.

## Role of file

[`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1290-L1297)
is an implementation file that also registers the `vertex_access` Level-3 group. The robustness category root adds this
file's factory directly with `createVertexAccessTests(testCtx)` in
[`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L65-L67). The header exposes the
factory in
[`vktRobustnessVertexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.hpp#L31-L37).

## Source code link

- Source: [`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1-L1300)
- Header: [`vktRobustnessVertexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.hpp#L1-L41)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99) | Category root registration and direct `vertex_access` insertion. |
| [`vktRobustnessUtil.hpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L41-L54) | Robust-device and verification helper declarations used by this file. |
| [`vktRobustnessUtil.cpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87) | `createRobustBufferAccessDevice()` enables `robustBufferAccess` on the dedicated device. |
| [`vktRobustnessUtil.cpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L352-L500) | `GraphicsEnvironment` pipeline setup used by the draw execution path. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963) | Mustpass paths confirming the registered leaves for all observed format and draw combinations. |

## Registration Hierarchy

```text
robustness.vertex_access
├── r32_uint
├── r32_sint
├── r32_sfloat
├── r32g32_uint
├── r32g32_sint
├── r32g32_sfloat
├── r32g32b32_uint
├── r32g32b32_sint
├── r32g32b32_sfloat
├── r32g32b32a32_uint
├── r32g32b32a32_sint
├── r32g32b32a32_sfloat
├── r64_uint
├── r64_sint
└── a2b10g10r10_unorm_pack32
```

The root group is constructed as `vertex_access`, and each direct child is generated from the `vertexFormats` array by
lower-casing the Vulkan format name after the `VK_FORMAT_` prefix
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1287)).
The mustpass list contains the same format children under `dEQP-VK.robustness.vertex_access`
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963)).

## Test Families

Each direct child below is one vertex input format group. For every format group, the file registers the same two nested
families: `draw` and `draw_indexed`
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1280-L1285)).

### r32_uint

Unsigned 32-bit scalar vertex input coverage. Mustpass leaves include `draw.{vertex_out_of_bounds,vertex_incomplete,instance_out_of_bounds}` and `draw_indexed.{last_index_out_of_bounds,indices_out_of_bounds,triangle_out_of_bounds}` for this format
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96892-L96897)).

### r32_sint

Signed 32-bit scalar vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96886-L96891)).

### r32_sfloat

32-bit float scalar vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96880-L96885)).

### r32g32_uint

Unsigned two-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96910-L96915)).

### r32g32_sint

Signed two-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96904-L96909)).

### r32g32_sfloat

Float two-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96898-L96903)).

### r32g32b32_uint

Unsigned three-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96928-L96933)).

### r32g32b32_sint

Signed three-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96922-L96927)).

### r32g32b32_sfloat

Float three-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96916-L96921)).

### r32g32b32a32_uint

Unsigned four-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96946-L96951)).

### r32g32b32a32_sint

Signed four-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96940-L96945)).

### r32g32b32a32_sfloat

Float four-component 32-bit vertex input coverage with the common draw and indexed-draw leaf set
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96934-L96939)).

### r64_uint

Unsigned 64-bit scalar vertex input coverage. These cases additionally require the 64-bit shader path and format support
checks described below
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L530-L539),
[`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96958-L96963)).

### r64_sint

Signed 64-bit scalar vertex input coverage with the same additional 64-bit requirements as `r64_uint`
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L530-L539),
[`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96952-L96957)).

### a2b10g10r10_unorm_pack32

Packed 10/10/10/2 normalized vertex input coverage. The verification code has a dedicated packed-value path for this
format
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1005-L1038),
[`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96874-L96879)).

### Nested `draw` leaves

`createDrawTests()` registers three non-indexed draw leaves per format
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1190-L1225)):

| Leaf | Observed setup |
|------|----------------|
| `vertex_out_of_bounds` | Creates data for 6 vertices and draws 9 vertices. |
| `vertex_incomplete` | Creates data for half a vertex and draws 3 vertices. |
| `instance_out_of_bounds` | Creates data for 1 instance and draws 3 instances. |

### Nested `draw_indexed` leaves

`createDrawIndexedTests()` registers three indexed draw leaves per format
([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1227-L1256)):

| Leaf | Observed index pattern |
|------|------------------------|
| `last_index_out_of_bounds` | Only the last submitted index is out of bounds. |
| `indices_out_of_bounds` | Multiple noncontiguous indices are out of bounds. |
| `triangle_out_of_bounds` | The first triangle references out-of-bounds indices. |

## Parameter dimensions and observed values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Format group | `r32_uint`, `r32_sint`, `r32_sfloat`, `r32g32_uint`, `r32g32_sint`, `r32g32_sfloat`, `r32g32b32_uint`, `r32g32b32_sint`, `r32g32b32_sfloat`, `r32g32b32a32_uint`, `r32g32b32a32_sint`, `r32g32b32a32_sfloat`, `r64_uint`, `r64_sint`, `a2b10g10r10_unorm_pack32` | [`vertexFormats`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1275) |
| Draw mode | `draw`, `draw_indexed` | Format groups add both families in [`addVertexFormatTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1277-L1286). |
| Non-indexed leaf | `vertex_out_of_bounds`, `vertex_incomplete`, `instance_out_of_bounds` | [`createDrawTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1204-L1222) |
| Indexed leaf | `last_index_out_of_bounds`, `indices_out_of_bounds`, `triangle_out_of_bounds` | [`createDrawIndexedTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1236-L1253) |
| Vertex input rate | Vertex-rate bindings and instance-rate binding are both present. | Binding descriptions use `VK_VERTEX_INPUT_RATE_VERTEX` and `VK_VERTEX_INPUT_RATE_INSTANCE` in [`VertexAccessInstance`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L541-L589). |
| Index data | Out-of-bounds index values use `100`, `101`, and `102` in the observed arrays. | Index arrays and configuration table in [`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435). |

## Support / feature requirements

- On devices exposing `VK_KHR_portability_subset`, the test rejects implementations without
  `robustBufferAccess`
  ([`VertexAccessTest::checkSupport()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L255-L261)).
- Test instances create a dedicated device with robust buffer access enabled through
  [`createRobustBufferAccessDevice()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L378-L417), whose utility implementation sets
  `enabledFeatures.robustBufferAccess = true`
  ([`vktRobustnessUtil.cpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87)).
- The vertex stage must support storage writes because the vertex shader writes observed attribute values to an SSBO
  ([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L524-L528)).
- For `r64_uint` and `r64_sint`, the file requires `VK_EXT_shader_image_atomic_int64` and checks
  `VK_FORMAT_FEATURE_VERTEX_BUFFER_BIT` for the input format
  ([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L530-L539)).

## Verification methods

- The generated vertex shader writes three vertex attributes per vertex or instance into a storage buffer for host-side
  inspection
  ([`VertexAccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L263-L366)).
- `iterate()` submits the prepared graphics command buffer, invalidates the output allocation, and returns pass or fail
  from `verifyResult()`
  ([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L806-L858)).
- `verifyResult()` maps each output scalar back to the expected vertex-rate or instance-rate buffer index, detects
  out-of-bounds accesses, and accepts either the expected in-bounds value or robustness-allowed out-of-bounds values
  ([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L860-L1003)).
- For out-of-bounds accesses, accepted values are values already within the bound buffer range, zero, or the documented
  `[0, 0, 0, x]` vector pattern when applicable
  ([`vktRobustnessVertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L959-L991)).
- Expected in-bounds comparisons are format-sensitive, including integer, floating-point, 64-bit, and packed normalized
  cases
  ([`isExpectedValueFromVertexBuffer()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1045-L1097)).

## Test principles

- Exercise robust vertex input handling by making the draw consume more vertex or instance data than the bound buffers
  provide, rather than by checking API errors
  ([`createDrawTests()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1204-L1212)).
- Exercise indexed vertex fetching by using valid and invalid indices in different spatial patterns
  ([`DrawIndexedAccessTest::s_indexConfigs`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L421-L435)).
- Cover scalar, vector, signed, unsigned, floating, 64-bit, and packed formats through a uniform registration matrix
  ([`vertexFormats`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L1258-L1275)).
- Use shader-visible storage output to verify returned attribute values after execution, not just that drawing completes
  ([`VertexAccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustnessVertexAccessTests.cpp#L341-L355)).

## Notes / uncertainties

- The hierarchy tree intentionally lists only the direct format children of `robustness.vertex_access`; nested `draw` and
  `draw_indexed` leaves are documented in `Test Families` to satisfy the Level-3 one-level hierarchy contract.
- The inspected mustpass file confirms 90 `vertex_access` leaves in this profile: 15 formats multiplied by 2 draw
  families and 3 leaves per draw family
  ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L96874-L96963)). Other mustpass profiles were not
  inspected for this page.
- No separate test-plan document was used for these claims; the page is based on the category root, assigned source and
  header, inspected utility code, and the default mustpass list.
