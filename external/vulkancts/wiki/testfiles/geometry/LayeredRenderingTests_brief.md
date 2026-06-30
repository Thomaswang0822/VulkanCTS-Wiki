# Understanding Brief: geometry.layered

## One-Sentence Test Purpose

This test family checks whether a geometry shader can choose the correct destination layer for rendered primitives, and whether
Vulkan preserves the expected per-layer image contents through normal rendering, readback, and secondary command buffer paths.

## Concrete Mental Model: One Fixed Prefix, Ten Different Behaviors

Use this fixed prefix while reading the whole brief:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.<leaf>
```

For every leaf below this prefix:

- the render target is a 64x64 2D-array image;
- it has exactly four layers: layer 0, layer 1, layer 2, and layer 3;
- the host checks all four layers after rendering;
- only the final `<leaf>` changes what the shaders and validation expect.

Think of the framebuffer as four transparent sheets stacked together:

```text
layer 0: 64x64 pixels
layer 1: 64x64 pixels
layer 2: 64x64 pixels
layer 3: 64x64 pixels
```

Most leaves render a rectangle covering the left half of one or more layers. A correct implementation puts each rectangle on the
intended sheet and leaves unintended sheets black.

## The Ten Leaves Under `2d_array.64_64_4`

### 1. `render_to_default_layer`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.render_to_default_layer
```

What happens:

- The geometry shader emits one rectangle.
- It does **not** assign `gl_Layer`.
- Without an explicit layer assignment, the primitive should go to default layer 0.

Expected image:

```text
layer 0: left half is white
layer 1: black
layer 2: black
layer 3: black
```

Why this leaf exists:

- It checks the baseline rule: if the geometry shader does not select a layer, rendering lands in layer 0.

### 2. `render_to_one`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.render_to_one
```

What happens:

- The geometry shader emits one rectangle.
- It explicitly writes `gl_Layer = 2`, the middle target layer for four layers.

Expected image:

```text
layer 0: black
layer 1: black
layer 2: left half is white
layer 3: black
```

Why this leaf exists:

- It checks the simplest explicit layer selection: one primitive should move away from default layer 0 to one chosen layer.

### 3. `render_to_all`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.render_to_all
```

What happens:

- One geometry shader invocation loops over all four layers.
- For each layer, it writes `gl_Layer = layerNdx` and emits one rectangle.
- It also writes a different color for each layer.

Expected image:

```text
layer 0: left half is white
layer 1: left half is red
layer 2: left half is green
layer 3: left half is blue
```

Why this leaf exists:

- It checks that one geometry shader invocation can target every layer in sequence, not just one selected layer.
- It also makes swapped or repeated layer routing obvious because each layer has a different expected color.

### 4. `render_different_content`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.render_different_content
```

What happens:

- The geometry shader loops over layers.
- Instead of drawing the same rectangle everywhere, it draws a different width on each layer.
- Layer 0 intentionally remains empty.

Expected image:

```text
layer 0: black
layer 1: a narrow white bar, about 1/4 image width
layer 2: a wider white bar, about 1/2 image width
layer 3: a still wider white bar, about 3/4 image width
```

Why this leaf exists:

- `render_to_all` proves that every layer can receive something.
- `render_different_content` proves that layers do not accidentally share, duplicate, or overwrite the same content.

### 5. `fragment_layer`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.fragment_layer
```

What happens:

- The geometry shader still chooses a destination layer with `gl_Layer`.
- The fragment shader then reads `gl_Layer` and computes the output color from that value.
- In other words, this leaf checks that the layer value is visible correctly in the fragment stage too.

Expected image:

```text
layer 0: left half has the color encoded for fragment gl_Layer == 0
layer 1: left half has the color encoded for fragment gl_Layer == 1
layer 2: left half has the color encoded for fragment gl_Layer == 2
layer 3: left half has the color encoded for fragment gl_Layer == 3
```

More concretely, the fragment shader uses this pattern:

```text
red   = 0.5 for even layers, 1.0 for odd layers
green = 0.5 for layers 0-1, 1.0 for layers 2-3
blue  = 1.0 only for layer 0, otherwise 0.0
```

Why this leaf exists:

- The previous leaves mainly check where pixels land.
- This leaf also checks what `gl_Layer` means to the fragment shader after rasterization.

### 6. `invocation_per_layer`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.invocation_per_layer
```

What happens:

- The geometry shader is run with four invocations for one input point.
- Invocation 0 writes layer 0.
- Invocation 1 writes layer 1.
- Invocation 2 writes layer 2.
- Invocation 3 writes layer 3.
- Each invocation uses `gl_InvocationID` as the layer number.

Expected image:

```text
layer 0: left half is white
layer 1: left half is red
layer 2: left half is green
layer 3: left half is blue
```

Why this leaf exists:

- `render_to_all` uses one invocation with a loop.
- `invocation_per_layer` uses multiple geometry shader invocations, one per layer.
- If a driver mishandles geometry shader invocations or `gl_InvocationID`, this leaf can fail even when `render_to_all` passes.

### 7. `multiple_layers_per_invocation`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.multiple_layers_per_invocation
```

What happens:

- The geometry shader again uses multiple invocations.
- Each invocation writes to two layers:
  - its own layer;
  - the next layer, wrapping around from layer 3 back to layer 0.
- The rectangles have layer-dependent widths.

Expected image:

```text
layer 0: black
layer 1: a narrow white bar, about 1/4 image width
layer 2: a wider white bar, about 1/2 image width
layer 3: a still wider white bar, about 3/4 image width
```

Why this leaf exists:

- `invocation_per_layer` is one invocation to one layer.
- `multiple_layers_per_invocation` checks the harder case where one invocation emits primitives for more than one layer.
- This can catch implementations that incorrectly assume a geometry shader invocation has only one layer target.

### 8. `readback`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.readback
```

What happens:

- The host first initializes color, depth, and stencil attachments.
- The test renders twice.
- A small uniform tells the geometry shader whether it is pass 0 or pass 1.
- The render pass uses attachment load behavior, so pass 1 must preserve and combine with results from pass 0.
- After rendering, the host copies color, depth, and stencil results back to CPU-visible buffers.

Expected image shape per layer:

```text
left region: result from pass 1
middle region: result from pass 0
right region: original cleared content
```

The host checks this pattern three times:

```text
color buffer: expected color bars
depth buffer: expected depth-value bars converted for comparison
stencil buffer: expected stencil-value bars converted for comparison
```

Why this leaf exists:

- This is not just another color-only `gl_Layer` case.
- It checks layered rendering together with attachment load, depth/stencil output, layout transitions, image copies, and CPU
  readback.

### 9. `secondary_cmd_buffer`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.secondary_cmd_buffer
```

What happens:

- The actual rendering commands are recorded into a secondary command buffer.
- The secondary command buffer is begun without inheriting a concrete framebuffer.
- Before rendering, the host initializes a layered storage image with different colors.
- The geometry shader renders colored rectangles to all layers.
- The fragment shader reads the storage image, averages it with the incoming geometry color, writes the result to the color
  attachment, and stores the same result back to the storage image.
- The test draws twice with a fragment shader memory barrier between draws.

Expected result:

```text
for each layer:
  final color = average(average(initial storage-image color, geometry color), geometry color)
```

Only part of each layer is expected to contain this final color; the validation also accounts for clear rectangles recorded in
the secondary command buffer.

Why this leaf exists:

- It checks that layered rendering still works when draw commands are executed through a secondary command buffer.
- It also checks shader image load/store ordering between two draws.

### 10. `secondary_cmd_buffer_inherit_framebuffer`

Full case name:

```text
dEQP-VK.geometry.layered.2d_array.64_64_4.secondary_cmd_buffer_inherit_framebuffer
```

What happens:

- Shader behavior and expected colors are the same as `secondary_cmd_buffer`.
- The important change is command-buffer setup:
  - `secondary_cmd_buffer` begins the secondary command buffer with no inherited framebuffer;
  - `secondary_cmd_buffer_inherit_framebuffer` begins it with the actual framebuffer in the inheritance info.

Expected result:

```text
same per-layer final image as secondary_cmd_buffer
```

Why this leaf exists:

- It checks the inherited-framebuffer variant of the secondary-command-buffer path.
- If only this leaf fails, the likely problem is not basic `gl_Layer` routing but secondary command buffer framebuffer inheritance.

## End-to-End Flow for the Simple Leaves

This flow applies to:

```text
render_to_default_layer
render_to_one
render_to_all
render_different_content
fragment_layer
invocation_per_layer
multiple_layers_per_invocation
```

```text
[host] create one 64x64 color image with four array layers
[host] create a layered framebuffer that exposes all four layers
[host] generate shaders for the selected leaf
[host] clear all layers to black
[host] draw one point
[device] geometry shader expands that point into rectangles and chooses destination layers
[device] fragment shader writes white, per-layer color, or fragment-gl_Layer-derived color
[host] copy all four layers to a CPU-visible buffer
[host] check layer 0, then layer 1, then layer 2, then layer 3 against that leaf's expected image
```

## Special Flow: `readback`

`readback` adds depth/stencil and two render passes, so its flow is different:

```text
[host] create layered color image and layered depth/stencil image
[host] pre-fill color, depth, and stencil attachments with known values
[host] render pass 0 with uniform pass = 0
[device] geometry shader writes pass-0 rectangles to every layer
[host] barrier between render passes while keeping attachment contents loadable
[host] render pass 1 with uniform pass = 1
[device] geometry shader writes pass-1 rectangles to every layer
[host] copy color, depth, and stencil images to CPU-visible buffers
[host] validate the three-region bar pattern in color, depth, and stencil for every layer
```

## Special Flow: Secondary Command Buffer Leaves

This flow applies to both secondary-command-buffer leaves:

```text
secondary_cmd_buffer
secondary_cmd_buffer_inherit_framebuffer
```

```text
[host] create layered color attachment and layered storage image
[host] pre-fill the storage image with known per-layer colors
[host] record clear commands, two draws, and a shader memory barrier into a secondary command buffer
[host] choose whether the secondary command buffer inherits the framebuffer
[host] execute the secondary command buffer inside a primary render pass
[device] geometry shader routes rectangles to layers
[device] fragment shader blends geometry color with storage-image color and stores the result
[host] copy the layered color attachment to a CPU-visible buffer
[host] validate the final per-layer blended result
```

## What Failure Means

Use the failing leaf name to narrow the suspected problem:

| If this leaf fails | Most likely area to investigate |
|--------------------|---------------------------------|
| `render_to_default_layer` | Default layer selection when `gl_Layer` is not written. |
| `render_to_one` | Explicit `gl_Layer` assignment to one nonzero layer. |
| `render_to_all` | Looping over layers and repeatedly changing `gl_Layer`. |
| `render_different_content` | Keeping each layer's contents independent instead of duplicating or mixing layers. |
| `fragment_layer` | Fragment-stage `gl_Layer` value. |
| `invocation_per_layer` | Geometry shader invocations and `gl_InvocationID`. |
| `multiple_layers_per_invocation` | One geometry invocation emitting primitives for multiple layers. |
| `readback` | Attachment load, depth/stencil layered rendering, image layout transitions, image copy, or CPU readback. |
| `secondary_cmd_buffer` | Layered rendering through secondary command buffer execution, storage-image feedback, or shader barriers. |
| `secondary_cmd_buffer_inherit_framebuffer` | Same as `secondary_cmd_buffer`, plus framebuffer inheritance handling. |

## Important Variations Outside the Concrete Prefix

The same ten leaves repeat under other image shapes:

```text
1d_array.<size>.<leaf>
2d_array.<size>.<leaf>
cube.<size>.<leaf>
cube_array.<size>.<leaf>
3d.<size>.<leaf>
```

Only the image interpretation changes:

| Prefix component | What a layer number means |
|------------------|---------------------------|
| `1d_array` | A 1D array layer. |
| `2d_array` | A 2D array layer. |
| `cube` | One of the six cube faces. |
| `cube_array` | One face of one cube in a cube array. |
| `3d` | One z slice of a 3D image. |

The leaf meaning stays the same. For example, `render_to_all` always means “target every layer-like destination,” whether those
destinations are 2D-array layers, cube faces, cube-array face slices, or 3D z slices.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader generation | [initPrograms()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L850-L1220) | Shows how each leaf changes geometry and fragment shader behavior. |
| Simple rendering path | [test()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1223-L1307) | Used by the seven simple leaves. |
| Readback path | [testLayeredReadBack()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1309-L1692) | Used only by `readback`. |
| Secondary command buffer path | [testSecondaryCmdBuffer()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1694-L1963) | Used by both secondary-command-buffer leaves. |
| Per-layer validation | [verifyLayerContent()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L687-L800) | Defines the expected image for each leaf. |
| Registration matrix | [createLayeredRenderingTests()](../../../modules/vulkan/geometry/vktGeometryLayeredRenderingTests.cpp#L1996-L2075) | Builds image prefix + size prefix + behavior leaf paths. |

## Questions / Risk Points for User Audit

Resolved by this regenerated brief:

- The ten behavior leaves are explained under one concrete prefix, `dEQP-VK.geometry.layered.2d_array.64_64_4.<leaf>`.
- `secondary_cmd_buffer_inherit_framebuffer` is included separately from `secondary_cmd_buffer`.
- The brief avoids source macro names in the main behavior explanation and uses source links only in the final mapping table.

Remaining checkpoint before final rewrite:

- The final wiki page should not be written until this concrete ten-leaf explanation is acceptable as the mental model.
