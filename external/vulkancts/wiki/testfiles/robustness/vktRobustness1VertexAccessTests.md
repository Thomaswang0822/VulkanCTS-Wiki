# vktRobustness1VertexAccessTests

## Overview

This page documents the Vulkan CTS `robustness.robustness1_vertex_access` group implemented by
[`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L1-L955).
The file defines four robustness1 vertex input tests that render a small indexed triangle grid with intentionally
out-of-range vertex attribute access patterns, then verify every output pixel is green.

## Role of file

[`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L951)
is an implementation file that registers the `robustness1_vertex_access` Level-3 group. The robustness category root adds
this group directly with `createRobustness1VertexAccessTests(testCtx)` in
[`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L91-L97). The header exposes the
factory in
[`vktRobustness1VertexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.hpp#L28-L34).

## Source code link

- Source: [`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L1-L955)
- Header: [`vktRobustness1VertexAccessTests.hpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.hpp#L1-L38)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [`vktRobustnessTests.cpp`](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L61-L99) | Category root registration and direct `robustness1_vertex_access` insertion. |
| [`vktRobustnessUtil.hpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.hpp#L41-L54) | Robust-device helper declaration. |
| [`vktRobustnessUtil.cpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87) | `createRobustBufferAccessDevice()` enables `robustBufferAccess` on the dedicated device. |
| [`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029) | Mustpass paths confirming the four registered leaves. |

## Registration Hierarchy

```text
robustness.robustness1_vertex_access
├── out_of_bounds_stride_0
├── out_of_bounds_stride_16_single_buffer
├── out_of_bounds_stride_30_middle_of_buffer
└── out_of_bounds_stride_8_middle_of_buffer_separate
```

The root group is constructed as `robustness1_vertex_access`, and every direct child is added from the
`robustness1Tests` vector
([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389),
[`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L943-L949)).
The same four leaves are present in the inspected default mustpass file
([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029)).

## Test Families

### out_of_bounds_stride_0

This leaf uses three vertex bindings: positions, a zero-stride color binding, and a color structure binding. It generates
a 3-by-3 tile grid with invalid logical vertices `5`, `6`, `9`, and `10`, binds one color element with stride 0, and
truncates the color structure buffer size so the vertex fetch can read past the valid range
([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L210-L251)).

### out_of_bounds_stride_16_single_buffer

This leaf uses a single `Vertex` buffer as two bindings with `sizeof(Vertex)` stride. The second binding is intentionally
shortened before the `color2` member near the end, so indexed drawing can exercise out-of-range vertex attribute fetches
from a shared underlying allocation
([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L252-L293)).

### out_of_bounds_stride_30_middle_of_buffer

This leaf uses padded allocation around a `Vertex` array and offsets the vertex attributes into the padded data. It then
uses a shortened second binding so the invalid middle vertices map beyond the valid color data
([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L294-L346)).

### out_of_bounds_stride_8_middle_of_buffer_separate

This leaf stores positions and colors in separate padded arrays. The comments note that out-of-range padding is initialized
with `unusedColor` because the spec allows an out-of-range access to return any value from within the bound memory range;
this distinguishes robustly accepted values from the explicitly rejected `outOfRangeColor`
([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L347-L389)).

## Parameter dimensions and observed values

| Dimension | Observed values / ranges | Evidence |
|-----------|--------------------------|----------|
| Leaf names | `out_of_bounds_stride_0`, `out_of_bounds_stride_16_single_buffer`, `out_of_bounds_stride_30_middle_of_buffer`, `out_of_bounds_stride_8_middle_of_buffer_separate` | [`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389) |
| Render target size | `12 x 12` pixels | [`renderTargetSize`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L195-L202) |
| Grid dimensions used by all four leaves | `3 x 3` tiles, producing `(3 + 1) * (3 + 1)` vertices | Calls to `GenerateTriangles(3u, 3u, ...)` and [`GetVerticesCountForTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L218-L226) |
| Invalid logical vertex indices | `5`, `6`, `9`, `10` | Observed in each leaf setup, for example [`out_of_bounds_stride_0`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L225-L227) and [`out_of_bounds_stride_30_middle_of_buffer`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L294-L299). |
| Vertex attribute format | `VK_FORMAT_R32G32B32A32_SFLOAT` for positions and colors | Attribute descriptions in the four leaves, for example [`out_of_bounds_stride_0`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L237-L240). |
| Draw type | Indexed draw when `InputInfo::indices` is non-empty; otherwise non-indexed draw. The four observed leaves pass indices. | Draw dispatch in [`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L731-L750). |
| Accepted semantic colors | `expectedColor`, `unusedColor`, and specified zero variants for invalid/out-of-range cases | Color constants and accepted lists in [`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L123-L130). |

## Support / feature requirements

- The file creates a dedicated device with robust buffer access enabled before running each leaf
  ([`Robustness1AccessTest::createInstance()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L861-L884)).
- The robust-device helper sets `enabledFeatures.robustBufferAccess = true`
  ([`vktRobustnessUtil.cpp`](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp#L53-L87)).
- No explicit `checkSupport()` override or additional feature gate was observed in this file; support requirements beyond
  robust buffer access are therefore limited to the Vulkan operations used by the graphics pipeline setup in the inspected
  code.

## Verification methods

- Each leaf calls `robustness1TestFn()` with one `InputInfo` bundle describing bindings, attributes, buffer data,
  vertex count, and indices
  ([`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389)).
- The helper creates a color attachment, render pass, framebuffer, vertex buffers, optional index buffers, shader modules,
  and graphics pipeline for the supplied input configuration
  ([`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L480-L710)).
- Execution binds the vertex buffers and index buffer, then uses `cmdDrawIndexed()` for the observed inputs
  ([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L731-L750)).
- The generated vertex shader validates the fetched colors. It outputs green if valid vertices receive expected or unused
  colors, or if invalid/out-of-range vertices receive an accepted invalid value
  ([`Robustness1AccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L932)).
- After rendering, the color attachment is read back and every pixel must equal `vec4(0, 1, 0, 1)`; any mismatch logs the
  image and fails the test
  ([`vktRobustness1VertexAccessTests.cpp`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L761-L779)).

## Test principles

- Use padded host-side allocations to place recognizable values before and after the valid data range, making accidental
  out-of-range values observable in shader validation
  ([`PaddedAlloc`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L136-L193)).
- Generate a small indexed triangle mesh and move invalid vertices to the end of the allocation so the same geometry can
  exercise in-range and out-of-range fetches
  ([`GenerateTriangles()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L391-L456)).
- Encode the expected robustness behavior in shader logic and reduce the host-side verdict to an image-wide green-pixel
  check
  ([`Robustness1AccessTest::initPrograms()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L887-L940),
  [`robustness1TestFn()`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L761-L779)).
- Vary stride and buffer layout patterns across the four leaves: zero stride, one-buffer shortened binding, padded middle
  access, and separate padded position/color buffers
  ([`robustness1Tests`](../../../modules/vulkan/robustness/vktRobustness1VertexAccessTests.cpp#L202-L389)).

## Notes / uncertainties

- The hierarchy tree lists all direct children because `robustness1_vertex_access` has four leaf tests and no deeper
  registered subgroup level observed in the assigned file.
- The inspected default mustpass file confirms the four leaves for this profile
  ([`robustness.txt`](../../../mustpass/main/vk-default/robustness.txt#L15026-L15029)). Other mustpass profiles were not
  inspected for this page.
- The name `out_of_bounds_stride_30_middle_of_buffer` is documented as registered, but the inspected code uses
  `sizeof(Vertex)` for the binding stride rather than a literal `30`; no additional explanation for the historical or
  semantic meaning of `30` was found in the inspected files.
- No separate test-plan document was used for these claims; the page is based on the category root, assigned source and
  header, inspected utility code, and the default mustpass list.
