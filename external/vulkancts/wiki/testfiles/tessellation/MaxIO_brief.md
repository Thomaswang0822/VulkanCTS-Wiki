# Understanding Brief: `tessellation.tess_io`

## One-Sentence Test Purpose

These tests check whether tessellation shaders handle large, type-diverse control-to-evaluation interfaces and the built-in inner/outer tessellation levels, including the rule that a non-positive relevant outer level discards a patch.

## Background Knowledge

### Tessellation control and evaluation interfaces

A tessellation control shader (TCS) runs once per output control point. It can produce per-vertex values, which have one element for each control point, and per-patch values, which belong to the patch as a whole. A tessellation evaluation shader (TES) consumes those values after the fixed-function tessellator has generated coordinates for the patch.

User-defined interface variables consume numbered locations. A location contains four 32-bit components; some 64-bit vectors span two locations. Vulkan exposes separate limits for TCS per-vertex outputs, TCS per-patch outputs, and TES per-vertex inputs.

Why it matters here:
- `max_in_out` fills a device-dependent prefix of locations with mixed scalar and vector variables.
- The test separates per-vertex and per-patch ownership because they use different limits and lookup rules.
- Some cases read values in the TCS, the TES, both, or neither, so pipeline acceptance and shader-side checks cover distinct interface paths.

### Built-in tessellation levels and patch discard

The TCS writes four outer and two inner levels for a quad. The tessellator uses those values to subdivide the patch. A quad patch is discarded if any relevant outer level is less than or equal to zero; no primitives are generated and the TES does not run. Zero inner levels do not trigger that discard rule.

Why it matters here:
- `level_io` uses color to prove that the TES can read inner and outer levels written by the TCS.
- Its zero-write cases distinguish the discard effect of outer levels from the non-discard behavior of inner levels.

## One Concrete Example

The representative case is:

```text
dEQP-VK.tessellation.tess_io.level_io.tcs_writes0_outer_1
```

The TCS copies each input position, assigns a blue or yellow per-patch color according to `gl_PrimitiveID`, writes `gl_TessLevelOuter = {0, 1, 1, 1}`, and leaves both inner levels at one. Because the quad domain treats all four outer values as relevant, the zero first element discards both submitted patches. The TES and fragment shader produce no color fragments. The host therefore expects the attachment to remain at the transparent-black clear value.

This example isolates a built-in tessellation rule without descriptors or user-defined interface data. It also supplies a compact representative shader for the final page; the `max_in_out` shaders cannot be reconstructed as one device-independent exact source because their declarations and locations are regenerated after reading the current device's limits.

## End-to-End Test Flow

```text
1. max_in_out
[host] select one feature set, deterministic permutation, and TCS/TES read mode
[host] query tessellation IO limits and truncate the shuffled variable list at the first variable that does not fit
[host] regenerate and compile four GLSL shaders with device-dependent declarations and locations
[host] allocate and initialize a per-vertex or per-patch storage buffer
[host] create an 8 x 8 color attachment, readback buffer, descriptors, and four-stage graphics pipeline
[host] draw eight vertices as two four-control-point patches
[device] TCS copies typed source-buffer values into its large interface and optionally checks them
[device] tessellator emits quad-domain work at level one
[device] TES optionally checks transported values and emits blue/yellow on success or black on failure
[host] copy the image, wait, invalidate host memory, and compare against the two-color reference

2. level_io
[host] select one built-in level read or zero-write behavior
[host] generate fixed vertex, TCS, TES, and fragment shaders
[host] create the same 8 x 8 render and readback targets, without descriptors
[host] draw two four-control-point patches
[device] TCS writes the selected inner/outer levels and a per-patch color
[device] tessellator either emits the patches or discards them because of an outer zero
[device] TES reads selected levels into the color calculation, when the patch survives
[host] copy and compare the image against blue/yellow or clear black, according to the selected behavior
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `max_in_out` first creates mock GLSL from specification-minimum limits so the framework has programs during normal collection. At test-instance construction, it queries the device limits, regenerates `vert`, `tesc`, `tese`, and `frag`, replaces the mock binaries, and builds at the CTS baseline SPIR-V version.
- The generated interface declarations encode ownership (`patch` or per-vertex array), scalar/vector type, 16/32/64-bit width, interpolation qualifier, and explicit location.
- The TCS always writes every generated interface variable. Optional branches add TCS-side checks and an `outColor[]` transport. The TES optionally declares and checks the generated inputs.
- `level_io` emits fixed four-stage GLSL. Its TCS chooses six level constants; its TES either reads selected built-ins into color or forwards the per-patch color.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Per-vertex data buffer (`pvd`) | Yes, for per-vertex `max_in_out` cases | Storage-buffer descriptor | Read by TCS and TES as reference data | No | Supplies four control-point values for every generated interface variable. |
| Per-patch data buffer (`ppd`) | Yes, for per-patch `max_in_out` cases | Storage-buffer descriptor | Read by TCS and TES as reference data | No | Supplies one expected value for each of the two patches. |
| `R8G8B8A8_UNORM` color image | Yes | Color attachment | Written by fragment processing | Indirectly | Encodes interface-check success, level-read behavior, or patch discard. |
| Host-visible verification buffer | Yes | Transfer destination | Receives image copy | Yes | Supplies the 8 x 8 result to the image comparator. |
| Generated shader modules | Yes | Four graphics stages | Execute the selected behavior | No | Carry the generated interfaces or built-in level operations into the pipeline. |
| Descriptors in `level_io` | No | No | No | No | Built-in level cases need no buffer-backed reference data. |

The interface variables themselves are shader stage IO, not separate host-created resources. The host buffers provide values that let shaders verify that IO.

## What Is Checked

### `max_in_out`

- The pipeline must accept the generated interface within the current device's reported TCS/TES component limits.
- For per-vertex values, a TCS read compares each value selected by `gl_InvocationID` with the corresponding storage-buffer value. A TES read computes the expected interpolation bounds and requires each component to stay between the minimum and maximum of the four source control points.
- For per-patch values, a read requires `gl_PrimitiveID` 0 or 1 and exact equality with the corresponding source-buffer element.
- A successful check produces blue for patch 0 and yellow for patch 1. Any checked mismatch produces opaque black.
- The host compares all 64 pixels against an outer blue field with a centered 4 x 4 yellow field, using a per-channel threshold of 0.005.
- Cases where neither stage reads the user-defined values still require shader compilation, interface declaration, TCS writes, tessellation, and the shared rendered-image path to succeed.

### `level_io`

- `tes_reads_inner`, `tes_reads_outer`, and `tes_reads_both` multiply the known per-patch color by levels set to one, so the rendered blue/yellow image must remain unchanged.
- Writing one or all relevant outer levels to zero must discard both patches. The host expects the clear image.
- Writing one or both inner levels to zero does not discard a quad patch. The host still expects blue/yellow.
- The same 0.005 image threshold applies.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `max_in_out`, `level_io`

The intermediate nodes and leaves below each family refine its behavior. The family is the primary axis for this page because it switches between user-defined interface-capacity transport and built-in tessellation-level semantics.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `max_in_out` | Incorrect accounting, declaration, compilation, transport, interpolation, or checking of a large mixed-type TCS-to-TES interface; incorrect handling of a required numeric feature; or a shared render/readback defect. |
| `level_io` | Incorrect TCS write or TES read behavior for `gl_TessLevelOuter`/`gl_TessLevelInner`, incorrect patch-discard handling for outer zero, or a shared render/readback defect. |

## Important Variations and Special Cases

- `max_in_out` registers seven feature sets: `32_bits_only`, `with_i64`, `with_f64`, `all_but_16_bits`, `with_i16`, `with_f16`, and `all_types`.
- Each feature set has ten deterministic `permutation_0` through `permutation_9` intermediate nodes. Each contains eight leaves covering per-vertex/per-patch ownership and the four combinations of TCS reads and TES reads.
- The generator excludes illegal or unsupported combinations: normally interpolated integer variables, flat per-patch variables, and normally interpolated 64-bit floats. It does not generate 8-bit stage IO.
- The test requires the matching `shaderInt64`, `shaderFloat64`, `shaderInt16`, `shaderFloat16`, and `storageInputOutput16` features only when a selected feature set uses them.
- Runtime shader regeneration is necessary because explicit `location` declarations depend on the current device's reported limits. This means the exact `max_in_out` GLSL is device-dependent even for one registered path.
- The location calculation reserves built-in usage and, when TCS read diagnostics carry a color to the TES, one extra user location.
- `level_io` has eight direct leaves: three TES-read cases and five TCS-zero-write cases.
- Inner-zero leaves preserve rendering; outer-zero leaves expect patch discard. `tcs_writes0_outer_inner` also discards because its outer levels are zero.
- Both families require tessellation and `multiViewport`. The runtime creates two viewports even though shader code does not write `gl_ViewportIndex`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Interface variable model | [`IfaceVar`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L155-L455) | Generates names, GLSL types, location widths, declarations, buffer layout, assignments, and checks. |
| Device-dependent location budget | [`getMaxLocations()` and `getUsableLocations()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L490-L537) | Converts reported component limits into the fitting interface prefix. |
| `max_in_out` shader generation | [`makeShaders()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L622-L844) | Emits TCS outputs, optional checks, TES inputs/checks, and diagnostic colors. |
| Feature checks and shader regeneration | [`checkSupport()` and `reGeneratePrograms()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L851-L1010) | Gates numeric features and replaces mock shaders with device-specific programs. |
| `max_in_out` runtime and image check | [`MaxIOTestInstance`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1012-L1405) | Builds resources, initializes source buffers, draws, copies, and compares. |
| `level_io` shader generation | [`LevelIOTest::initPrograms()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1428-L1619) | Emits built-in level reads and zero writes. |
| `level_io` runtime and expectations | [`LevelIOTestInstance::iterate()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1648-L1790) | Selects blue/yellow or clear reference output and compares the copy. |
| Complete registration matrix | [`createTessIOTests()`](../../../modules/vulkan/tessellation/vktTessellationMaxIOTests.cpp#L1800-L1988) | Registers both families, all feature/permutation/read cases, and all level cases. |
| Parent registration | [`createTessellationTests()`](../../../modules/vulkan/tessellation/vktTessellationTests.cpp#L65-L81) | Places `tess_io` under `tessellation`. |
| Interface limits | [Vulkan limit definitions](../../../../vulkan-docs/src/chapters/limits.adoc#limits-maxTessellationControlPerVertexOutputComponents) | Defines the reported TCS per-vertex, per-patch, and TES input component limits. |
| Tessellation levels and discard | [Vulkan tessellation chapter](../../../../vulkan-docs/src/chapters/tessellation.adoc#tessellation) | Defines level-driven subdivision and the non-positive outer-level discard rule. |
| Built-in variables | [Vulkan built-in interface variables](../../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-builtin-variables-tesslevelouter) | Defines TCS write and TES read access for tessellation levels. |
| Mustpass inventory | [`vk-default/tessellation.txt`](../../../mustpass/main/vk-default/tessellation.txt#L416-L983) | Confirms 8 `level_io` cases and 560 `max_in_out` cases. |

## Questions / Risk Points for User Audit

- Is the test-family axis the clearest primary behavior parameter for a page that owns two distinct families?
- Is the distinction between stage IO and the storage buffers used as reference data clear?
- Does the page make clear that exact `max_in_out` declarations are device-dependent, which prevents one portable exact shader reconstruction?
- Is the contrast between outer-zero discard and inner-zero non-discard explicit?
- Are compile/link/interface-capacity coverage and shader-side value checks distinguished clearly?

No unresolved source, specification, registration, or mustpass risk changes the purpose, representative walkthrough selection, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Distill stage-interface locations and tessellator discard into compact Background Knowledge bullets.
- Keep `test family` as the primary behavior parameter, with `max_in_out` and `level_io` as its values.
- Copy the Failure Cause Mapping table unchanged into the final page.
- Use `dEQP-VK.tessellation.tess_io.level_io.tcs_writes0_outer_1` for the representative walkthrough. Its TCS is fixed, exact, and directly exposes patch discard.
- Explain the device-dependent `max_in_out` shader generator through parameter tables, behavior subsections, and runtime prose rather than presenting a misleading fixed reconstruction.
- Preserve the 568-case mustpass count and focused two-child registration tree; describe deeper values outside the parseable tree.
- Keep source navigation in the appendix.
