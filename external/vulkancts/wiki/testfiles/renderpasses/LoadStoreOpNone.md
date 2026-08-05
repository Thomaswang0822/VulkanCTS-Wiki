## Overview

**Core question:** Does the implementation honor `VK_ATTACHMENT_LOAD_OP_NONE` and `VK_ATTACHMENT_STORE_OP_NONE`, leaving attachment contents undefined inside the render area where specified, while preserving pre-initialized contents outside the render area?

- This page covers the `load_store_op_none` test family implemented in
  [vktRenderPassLoadStoreOpNoneTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp) and registered under every
  `renderpasses` suballocation subgroup (renderpass1, renderpass2, and dynamic rendering, non-SC) by
  [vktRenderPassTests.cpp](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8564-L8569).
- The test family exercises the `VK_EXT_load_store_op_none` and `VK_KHR_load_store_op_none` extensions across color, depth, stencil, and combined
  depth/stencil attachments.
- Each case pre-initializes one or more attachments, records a render pass (or dynamic rendering instance) with selected load/store ops, performs draws or
  clears inside a render area smaller than the image, then reads back the attachment and compares selected pixels against expected reference values.
- The core design relies on a render area (27×19) that is intentionally smaller than the image extent (32×32). This separates the region where `NONE` ops
  make contents undefined from the region where pre-initialized values must survive untouched.

## Background Knowledge

- **Render pass load and store operations.** Every attachment reference declares a load operation (`loadOp`, and separately `stencilLoadOp` for depth/stencil
  formats) and a store operation (`storeOp`, `stencilStoreOp`). These operations run at render pass scope: load operations execute before any attachment
  access in the first subpass using the attachment, and store operations execute after the last attachment access in the last subpass using it. The operations
  apply only within the render area; pixels outside the render area are not touched by load or store operations.
- **`VK_ATTACHMENT_LOAD_OP_NONE`.** The spec states that the previous contents of the image will be undefined inside the render pass, and no access type is
  used because the image is not accessed. This differs from `LOAD` (preserve previous contents) and `DONT_CARE` (contents become undefined, but the
  implementation may still read-modify-write the memory). With `NONE`, the attachment is simply not loaded.
- **`VK_ATTACHMENT_STORE_OP_NONE` dual behavior.** The spec defines two cases: if no values are written to the attachment during the render pass, the store
  operation does not access the contents and they are preserved. If values are written during the render pass, `STORE_OP_NONE` behaves identically to
  `STORE_OP_DONT_CARE`, making contents inside the render area undefined afterward. This distinction is the central property the test family validates.
- **Separable depth/stencil load/store ops.** Combined depth/stencil formats (for example `VK_FORMAT_D24_UNORM_S8_UINT`) allow independent `loadOp` /
  `stencilLoadOp` and `storeOp` / `stencilStoreOp` pairs. The test exercises cases where one aspect uses `NONE` while the other aspect uses `LOAD` or `STORE`,
  and verifies that writes to the active aspect do not corrupt the `NONE` aspect.

## Registration Hierarchy

```text
renderpasses.renderpass1.suballocation.load_store_op_none
├── color_load_op_load_store_op_none
├── color_load_op_none_store_op_dontcare
├── color_load_op_none_store_op_none
├── color_load_op_none_store_op_none_resolve
├── color_load_op_none_store_op_none_write_off
├── color_load_op_none_store_op_store
├── color_load_op_none_store_op_store_alphablend
├── depth_d16_unorm_load_op_load_store_op_none
├── stencil_s8_uint_load_op_load_store_op_none
├── depthstencil_d24_unorm_s8_uint_load_op_depth_load_stencil_none_store_op_depth_store_stencil_none_stencil_test_off
```

The `load_store_op_none` group is added to each rendering-type suballocation subgroup (`renderpass1`, `renderpass2`, and dynamic rendering) by
[vktRenderPassTests.cpp#L8564-L8569](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8564-L8569). The tree above uses `renderpass1` as the
representative path; the same case leaves appear identically under `renderpass2` and dynamic-rendering subgroups. Test case leaves are registered directly
under the group; there are no intermediate nodes between the group and the leaves. The tree shows representative leaves from each behavioral group; the full
set of depth, stencil, and depth/stencil leaves is parameterized by format and enumerated in [Parameter Dimensions and Observed Values](#parameter-dimensions-and-observed-values).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Attachment aspect | color, depth, stencil, combined depth/stencil | Determines which attachment aspect receives `NONE` ops and which reference values the verification checks. | [test case creation](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1536-L2216) |
| Load op | `LOAD`, `NONE`, `DONT_CARE`, `CLEAR` (via `cmdClearAttachments`) | Controls whether the attachment's previous contents are preserved (`LOAD`), left undefined (`NONE`, `DONT_CARE`), or overwritten by a clear inside the render area. | [AttachmentParams](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L93-L102) |
| Store op | `STORE`, `NONE`, `DONT_CARE` | Controls whether rendered contents are written back (`STORE`), left untouched if unwritten or undefined if written (`NONE`), or discarded (`DONT_CARE`). | [AttachmentParams](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L93-L102) |
| Depth/stencil format | `d16_unorm`, `d32_sfloat`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`, `s8_uint` | Expands depth, stencil, and combined depth/stencil cases across all depth- or stencil-capable formats supported by the device. | [format list](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1757-L1759) |
| Test/write enable | `color_write_off`, `depth_test_off`, `depth_write_off`, `stencil_test_off`, `stencil_write_off` | Disables the pipeline state that would otherwise write to the attachment, so `STORE_OP_NONE` with no writes can be verified as preserving contents. | [usage flags](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L74-L81) |
| Extension preference | `KHR`, `EXT` | Alternates between `VK_KHR_load_store_op_none` and `VK_EXT_load_store_op_none` by format index so both extension code paths are exercised. | [extPreference](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L116-L134) |
| Rendering type | `renderpass1`, `renderpass2`, `dynamic_rendering` | Provided by the `SharedGroupParams`; the group is instantiated once per rendering type. Some input-attachment cases require `VK_KHR_dynamic_rendering_local_read`. | [checkSupport](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L441-L503) |

### Full depth, stencil, and depth/stencil leaf enumeration

Depth cases are registered for every depth-capable format (`d16_unorm`, `d32_sfloat`, `d16_unorm_s8_uint`, `d24_unorm_s8_uint`,
`d32_sfloat_s8_uint`), each with four op variants:

| Leaf suffix | Depth load op | Depth store op | Color attachment |
|-------------|---------------|----------------|------------------|
| `load_op_load_store_op_none` | `LOAD` | `NONE` | `LOAD` / `STORE` |
| `load_op_none_store_op_none_write_off` | `NONE` | `NONE` (depth test off) | `LOAD` / `STORE` |
| `load_op_none_store_op_store` | `NONE` (cleared mid-pass) | `STORE` | `LOAD` / `STORE` |
| `load_op_none_store_op_dontcare` | `NONE` (cleared mid-pass) | `DONT_CARE` | `LOAD` / `STORE` |

Stencil cases are registered for every stencil-capable format (`d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`, `s8_uint`), each with the
same four op variants applied to the stencil aspect.

Combined depth/stencil cases are registered for every format with both aspects (`d16_unorm_s8_uint`, `d24_unorm_s8_uint`, `d32_sfloat_s8_uint`), each with
four variants that mix one aspect on `LOAD`/`STORE` with the other aspect on `NONE`/`NONE`.

## Behavior Parameters

The primary behavioral axis is the test case leaf, which clusters into four behavioral groups by attachment aspect. Within each group, the load/store op
combination determines what is tested. The groups share the same render-area design and verification method; they differ in which attachment aspect receives
the `NONE` ops and which pipeline state is configured.

### Color attachment tests

These cases exercise `NONE` ops on color attachments. The color attachment is pre-initialized to green, and the render area is smaller than the image so the
outer region retains green while the inner region reflects the op-specific outcome.

- `color_load_op_load_store_op_none`: attachment 0 uses `LOAD` / `STORE_NONE` and serves as an input attachment in a second subpass; attachment 1 uses
  `DONT_CARE` / `STORE`. Subpass 0 draws red into attachment 0; subpass 1 reads it back, adds blue, and writes magenta to attachment 1. Because attachment 0
  has `STORE_NONE` and was written, its inner contents are undefined; only the outer green is verified.
- `color_load_op_none_store_op_none_write_off`: `LOAD_NONE` / `STORE_NONE` with the color write mask set to zero. No writes occur, so the attachment is
  never accessed; both inner and outer must retain the pre-initialized green.
- `color_load_op_none_store_op_none`: `LOAD_NONE` / `STORE_NONE` with a draw. The draw writes red, so `STORE_NONE` behaves like `DONT_CARE`: inner is
  undefined, outer must remain green.
- `color_load_op_none_store_op_store`: `LOAD_NONE` / `STORE_STORE`. `LOAD_NONE` makes initial inner contents undefined, but a `cmdClearAttachments` writes
  dark blue mid-pass; `STORE_STORE` keeps it. Inner must be dark blue, outer must be green.
- `color_load_op_none_store_op_store_alphablend`: same as above but with alpha blending enabled and a draw instead of only a clear. Inner must match the
  blended result, outer must be green.
- `color_load_op_none_store_op_dontcare`: attachment 0 uses `LOAD_NONE` / `DONT_CARE` as an input attachment; same two-subpass flow as the first case.
  Inner is undefined, outer must be green.
- `color_load_op_none_store_op_none_resolve`: multisample color target with `LOAD_NONE` / `STORE_NONE` plus a resolve target using `LOAD` / `STORE`. The
  multisample attachment is never verified (its inner is undefined after `STORE_NONE` with writes), but the resolved target must contain the rendered red
  inside and green outside.

### Depth attachment tests

These cases exercise `NONE` ops on the depth aspect. A color attachment (always `LOAD` / `STORE`) accompanies the depth attachment so the test can verify
that depth testing and color writes still work correctly while depth contents follow the op rules.

- `depth_*_load_op_load_store_op_none`: depth uses `LOAD` / `STORE_NONE`. Two draws with depth compare op `GREATER`: the first draw (depth 1.0) passes and
  updates depth; the second draw (same depth) fails. Color inner must be red. Depth inner is undefined because `STORE_NONE` was written; depth outer must
  remain the pre-initialized 0.5.
- `depth_*_load_op_none_store_op_none_write_off`: depth uses `LOAD_NONE` / `STORE_NONE` with depth test disabled (no depth writes). The depth attachment is
  never written, so both inner and outer must retain 0.5.
- `depth_*_load_op_none_store_op_store`: depth uses `LOAD_NONE` / `STORE_STORE`. `LOAD_NONE` makes initial depth undefined, but `cmdClearAttachments` sets
  it to 0.25 mid-pass and a draw updates it to 1.0. Inner must be 1.0, outer must be 0.5.
- `depth_*_load_op_none_store_op_dontcare`: depth uses `LOAD_NONE` / `DONT_CARE`. Cleared mid-pass and updated by a draw, but `DONT_CARE` discards the
  result. Depth inner is undefined; outer must be 0.5.

### Stencil attachment tests

These cases are structurally identical to the depth tests but exercise the stencil aspect. A color attachment accompanies the stencil attachment. Stencil
testing uses compare op `GREATER` with a reference value of 255.

- `stencil_*_load_op_load_store_op_none`: stencil uses `LOAD` / `STORE_NONE`. Two draws: the first passes the stencil test and updates stencil to 255; the
  second fails. Color inner must be red. Stencil inner is undefined; stencil outer must remain 128.
- `stencil_*_load_op_none_store_op_none_write_off`: stencil uses `LOAD_NONE` / `STORE_NONE` with stencil test disabled (no stencil writes). Both inner and
  outer must retain 128.
- `stencil_*_load_op_none_store_op_store`: stencil uses `LOAD_NONE` / `STORE_STORE`. Cleared to 64 mid-pass, then updated to 255 by a draw. Inner must be
  255, outer must be 128.
- `stencil_*_load_op_none_store_op_dontcare`: stencil uses `LOAD_NONE` / `DONT_CARE`. Cleared and updated, but discarded. Stencil inner is undefined; outer
  must be 128.

### Depth/stencil combined tests

These cases use a single combined depth/stencil attachment and set independent ops on each aspect. One aspect is active (`LOAD` / `STORE`) while the other
uses `NONE` / `NONE`. The test verifies that writes to the active aspect do not corrupt the `NONE` aspect, which must retain its pre-initialized value
everywhere (because `STORE_NONE` with writes to the other aspect does not access this aspect).

- `depthstencil_*_load_op_depth_load_stencil_none_store_op_depth_store_stencil_none_stencil_test_off`: depth on `LOAD` / `STORE`, stencil on `NONE` / `NONE`
  with stencil test off. Depth is updated to 1.0; stencil must remain 128.
- `depthstencil_*_load_op_depth_none_stencil_load_store_op_depth_none_stencil_store_depth_test_off`: stencil on `LOAD` / `STORE`, depth on `NONE` / `NONE`
  with depth test off. Stencil is updated to 255; depth must remain 0.5.
- `depthstencil_*_load_op_depth_load_stencil_none_store_op_depth_store_stencil_none_stencil_write_off`: depth on `LOAD` / `STORE`, stencil on `NONE` / `NONE`
  with stencil write off. Depth is updated to 1.0; stencil must remain 128.
- `depthstencil_*_load_op_depth_none_stencil_load_store_op_depth_none_stencil_store_depth_write_off`: stencil on `LOAD` / `STORE`, depth on `NONE` / `NONE`
  with depth write off but depth test enabled with compare op `ALWAYS`. Stencil is updated to 255; depth must remain 0.5.

## Shader Analysis

Shader code is not part of the tested behavior. The fragment shaders are trivial vehicles for producing color and depth output: they pass through the vertex
color, optionally set `gl_FragDepth = 1.0`, and in one variant read an input attachment and add the vertex color
([initPrograms](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L505-L560)). No shader walkthrough is needed because the test
validates render pass load/store op semantics, not shader logic.

## Runtime Execution and Result Checking

- **Image and render area.** The image is 32×32 pixels; the render area is 27×19 pixels
  ([constructor](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L562-L569)). This gap is deliberate: pixels outside the render area
  are never touched by load or store operations, so they must retain their pre-initialized values regardless of the ops chosen.
- **Attachment pre-initialization.** Attachments flagged with `ATTACHMENT_INIT_PRE` are cleared to known reference values before the render pass begins. Color
  attachments are cleared to green `(0, 1, 0, 1)` or green-uint `(0, 255, 0, 255)` for integer formats; depth attachments to `0.5`; stencil attachments to
  `128` ([pre-init loop](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L983-L1020)).
- **Mid-pass clears.** Some cases set `ATTACHMENT_INIT_CMD_CLEAR`, which causes `vkCmdClearAttachments` to run at the start of the draw commands, writing a
  known value inside the render area before any draw. This produces a deterministic inner value that later load/store ops act upon
  ([drawCommands](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L782-L815)).
- **Render pass or dynamic rendering.** The test records a render pass (legacy or renderpass2) or a dynamic rendering instance depending on the group
  parameters. The command buffer records begin, draw commands (or clears), and end
  ([createCommandBuffer](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L571-L598),
  [dynamic variant](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L600-L780)).
- **Readback.** After the render pass completes, each attachment with `verifyAspects` entries is transitioned to a transfer source layout and copied to a
  host-visible buffer. Depth, stencil, and color aspects are read through their respective helpers
  ([verification loop](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1452-L1522)).
- **Pixel comparison.** For each verified aspect, every pixel is classified as inner (inside the 27×19 render area) or outer. The test checks the inner
  reference only when `verifyInner` is true and the outer reference only when `verifyOuter` is true. A pixel passes if all four channels are within `0.01` of
  the expected `tcu::Vec4` reference ([comparison](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1504-L1520)).
- **Pass condition.** The case passes only if every checked pixel on every verified aspect matches its reference within tolerance
  ([final result](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1524-L1527)).

| Resource | Created/configured by host? | Bound to GPU? | Device access | Host readback | Role |
|---------|-----------------------------|---------------|---------------|---------------|------|
| Attachment images | Yes | Framebuffer or dynamic rendering attachment | Read/written by render pass ops, draws, and clears | Yes, via transfer copy | The images whose load/store op behavior is under test. |
| Vertex buffer | Yes | Vertex binding 0 | Read by vertex shader | No | Provides the quad geometry and per-vertex colors for draws. |
| Input attachment descriptor | Yes | Descriptor set binding 0 | Read by fragment shader in subpass 1 | No | Used by the two-subpass color cases to feed subpass 0 output into subpass 1. |
| Readback buffer | Yes | Transfer destination | Written by copy command | Yes | Host-visible copy of attachment contents for pixel comparison. |

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Color `load_op_none_store_op_none_write_off` | `STORE_OP_NONE` with no writes not preserving contents; color write mask leak. |
| Color `load_op_none_store_op_none` | `STORE_OP_NONE` with writes not behaving as `DONT_CARE`; outer-region preservation failure. |
| Color `load_op_none_store_op_store` | `LOAD_OP_NONE` followed by mid-pass clear or draw not producing expected inner value; `STORE` not persisting. |
| Color `load_op_load_store_op_none` | Input attachment read in subpass 1 not seeing subpass 0 output; `STORE_NONE` corrupting outer region. |
| Color `load_op_none_store_op_none_resolve` | Multisample resolve not producing expected resolved target; `STORE_NONE` on multisample attachment corrupting resolve. |
| Depth `load_op_none_store_op_none_write_off` | `STORE_OP_NONE` with no depth writes not preserving depth contents. |
| Depth `load_op_load_store_op_none` | Depth test or write not updating depth correctly; `STORE_NONE` with writes corrupting outer depth. |
| Depth `load_op_none_store_op_store` | `LOAD_OP_NONE` plus clear/draw not producing expected depth; `STORE` not persisting depth. |
| Depth `load_op_none_store_op_dontcare` | `DONT_CARE` not allowing discard; outer-region depth corruption. |
| Stencil (all variants) | Same failure shapes as depth, applied to the stencil aspect with stencil test/reference logic. |
| Depth/stencil combined (all variants) | Cross-aspect corruption: writes to the active aspect modifying the `NONE` aspect of the same image. |
| Any case | Shared infrastructure: image layout transition, readback copy, or pixel comparison defect. |

### Cause Analysis

#### `STORE_OP_NONE` content preservation failure

**Possible failure symptoms:** A case that uses `STORE_OP_NONE` with no writes to the attachment (for example, `color_load_op_none_store_op_none_write_off`
or `depth_*_load_op_none_store_op_none_write_off`) fails because pixels inside the render area do not match the pre-initialized reference value.

**Possible implementation causes:** The spec requires that `STORE_OP_NONE` not access the attachment when no values are written during the render pass. If the
driver or hardware performs a read-modify-write or clear-on-exit for the store operation even when no writes occurred, the inner contents can be corrupted.
This would be a store-op handling defect in the render pass or dynamic rendering implementation.

#### `STORE_OP_NONE` with writes not behaving as `DONT_CARE`

**Possible failure symptoms:** A case that writes to an attachment during the render pass and uses `STORE_OP_NONE` (for example,
`color_load_op_none_store_op_none` or `depth_*_load_op_load_store_op_none`) fails because the outer region, which must retain pre-initialized values, has
been modified.

**Possible implementation causes:** The spec states that `STORE_OP_NONE` with writes behaves identically to `DONT_CARE`. Store operations may read-modify-write
any memory locations within the image subresource, not just the render area. If the implementation applies the store operation or a related memory transaction
to pixels outside the render area, the pre-initialized outer values can be overwritten. This is a render-area scoping or store-op semantics defect.

#### `LOAD_OP_NONE` not leaving contents undefined before writes

**Possible failure symptoms:** A case that uses `LOAD_OP_NONE` followed by a mid-pass clear or draw and `STORE_OP_STORE` (for example,
`color_load_op_none_store_op_store` or `depth_*_load_op_none_store_op_store`) fails because the inner contents after the clear or draw do not match the
expected reference.

**Possible implementation causes:** `LOAD_OP_NONE` means the attachment is not loaded and its contents inside the render area are undefined. If the
implementation incorrectly loads previous contents despite `NONE`, or if the mid-pass `cmdClearAttachments` or subsequent draw does not produce the expected
deterministic value, the inner comparison fails. The cause could be in load-op handling, clear-attachment execution, or draw pipeline state configuration.

#### Cross-aspect depth/stencil corruption

**Possible failure symptoms:** A combined depth/stencil case fails because the aspect using `NONE` / `NONE` does not retain its pre-initialized value, even
though writes occurred only to the other aspect.

**Possible implementation causes:** Combined depth/stencil images may share memory or use read-modify-write operations that affect both aspects. The spec
notes that for depth/stencil images, writes to one aspect may also result in read-modify-write operations for the other aspect when separate access is not
supported. If the implementation does not isolate the `NONE` aspect from writes to the active aspect, the pre-initialized value can be corrupted. This is a
separate-depth/stencil-access handling defect.

#### Input attachment subpass dependency failure

**Possible failure symptoms:** A two-subpass color case (for example, `color_load_op_load_store_op_none`) fails because attachment 1 does not contain the
expected magenta result inside the render area.

**Possible implementation causes:** Subpass 1 reads attachment 0 as an input attachment and adds blue to produce magenta. If the subpass dependency between
subpass 0's color write and subpass 1's input attachment read is not correctly enforced, or if the input attachment descriptor binding is misconfigured, the
input read can return stale or undefined data. This is a subpass dependency or input attachment pipeline defect.

## Case Pruning

### Requirement-based pruning

- Every case requires at least one of `VK_EXT_load_store_op_none` or `VK_KHR_load_store_op_none`. The test is skipped if neither is available
  ([checkSupport](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L460-L468)).
- `renderpass2` cases require `VK_KHR_create_renderpass2`
  ([L449-L450](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L449-L450)).
- Dynamic rendering cases require `VK_KHR_dynamic_rendering`, and multi-subpass dynamic rendering cases additionally require
  `VK_KHR_dynamic_rendering_local_read` ([L453-L458](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L453-L458)).
- Depth and stencil format variants are skipped if `getPhysicalDeviceImageFormatProperties` returns failure for the required format and usage combination
  ([L496-L501](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L496-L501)).
- The entire group is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`)
  ([vktRenderPassTests.cpp#L8567-L8569](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8567-L8569)).

### Design-based pruning

- The two-subpass color cases (`color_load_op_load_store_op_none` and `color_load_op_none_store_op_dontcare`) are registered only when secondary command
  buffers are not used, because their input-attachment flow depends on the primary command buffer path
  ([L1555](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1555),
  [L1691](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1691)).
- The remaining color cases and all depth/stencil cases are restricted to monolithic pipeline construction
  ([L1588](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1588),
  [L1755](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1755)).
- The `s8_uint` format appears only in stencil cases (it has no depth aspect); pure depth-only formats (`d16_unorm`, `d32_sfloat`) appear only in depth cases
  ([format loop](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1761-L1804)).

## Key Takeaways

- The test's core lever is the dual behavior of `STORE_OP_NONE`: it preserves contents when no writes occur during the render pass, but behaves like
  `DONT_CARE` when writes do occur. Every behavioral group exercises both sides of this split.
- The render area (27×19) is intentionally smaller than the image (32×32) so that outer pixels, which no load or store operation may touch, serve as an
  invariant control. Any outer-region mismatch points to a store-op or memory-scoping defect.
- `LOAD_OP_NONE` makes the attachment's previous contents undefined inside the render area without accessing the image. Cases that verify inner contents
  after `LOAD_OP_NONE` always pair it with a mid-pass clear or draw that produces a deterministic value first.
- Combined depth/stencil cases test aspect independence: one aspect on `NONE` / `NONE` must survive writes to the other aspect, validating that the
  implementation does not corrupt the unused aspect through shared memory or read-modify-write behavior.
- See [Failure Meaning](#failure-meaning) for how each failure mode maps to specific implementation defect categories.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Test family factory | [vktRenderPassLoadStoreOpNoneTests.cpp#L1532-L1534](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1532-L1534) | Creates the `load_store_op_none` group and registers all test case leaves. |
| Group attachment | [vktRenderPassTests.cpp#L8564-L8569](../../../modules/vulkan/renderpass/vktRenderPassTests.cpp#L8564-L8569) | Adds the group to each rendering-type suballocation subgroup. |
| Support checks | [vktRenderPassLoadStoreOpNoneTests.cpp#L441-L503](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L441-L503) | Extension, rendering-type, and depth/stencil format requirement checks. |
| Shader programs | [vktRenderPassLoadStoreOpNoneTests.cpp#L505-L560](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L505-L560) | Trivial vertex and fragment shaders used as rendering vehicles. |
| Test instance constructor | [vktRenderPassLoadStoreOpNoneTests.cpp#L562-L569](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L562-L569) | Sets the 32×32 image size and 27×19 render area. |
| Render pass creation | [vktRenderPassLoadStoreOpNoneTests.cpp#L213-L375](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L213-L375) | Builds the render pass object from attachment descriptions and subpass references. |
| Dynamic rendering command buffer | [vktRenderPassLoadStoreOpNoneTests.cpp#L600-L780](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L600-L780) | Records the dynamic rendering instance with attachment info and optional secondary command buffer. |
| Draw commands and mid-pass clears | [vktRenderPassLoadStoreOpNoneTests.cpp#L782-L883](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L782-L883) | Issues `cmdClearAttachments` and draws inside the render pass. |
| Main test iteration | [vktRenderPassLoadStoreOpNoneTests.cpp#L885-L1528](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L885-L1528) | Creates images, pre-initializes attachments, builds pipelines, submits, reads back, and compares. |
| Verification loop | [vktRenderPassLoadStoreOpNoneTests.cpp#L1452-L1527](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1452-L1527) | Reads back each verified aspect and compares inner/outer pixels against reference values. |
| Test case creation | [vktRenderPassLoadStoreOpNoneTests.cpp#L1536-L2216](../../../modules/vulkan/renderpass/vktRenderPassLoadStoreOpNoneTests.cpp#L1536-L2216) | Defines the `TestParams` for every registered case across all behavioral groups. |
| Mustpass entries | [renderpasses.txt](../../../mustpass/main/vk-default/renderpasses.txt) | Lists all `dEQP-VK.renderpasses.*.suballocation.load_store_op_none.*` entries across rendering types. |
