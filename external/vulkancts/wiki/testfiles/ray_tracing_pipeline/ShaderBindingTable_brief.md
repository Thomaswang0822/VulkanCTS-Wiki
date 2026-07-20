# Understanding Brief: `ray_tracing_pipeline.shader_binding_table`

## One-Sentence Test Purpose

This test checks whether a ray tracing pipeline correctly resolves shader binding table (SBT) entries for hit, miss, and callable shader selection through `traceRayEXT`'s `sbtRecordOffset`, `sbtRecordStride`, and `missIndex` parameters, and whether shader-group handles can be packed at every advertised power-of-two alignment without corrupting shader-record data.

## Background Knowledge

### Shader Binding Table layout

The SBT is a host-filled buffer that the device reads during `vkCmdTraceRaysKHR`. It is split into four `VkStridedDeviceAddressRegionKHR` regions: raygen, miss, hit, callable. Each region is an array of records. A record starts with a shader-group handle (size `VkPhysicalDeviceRayTracingPropertiesKHR::shaderGroupHandleSize`) and is followed by an optional shader-record data block visible to that group through `layout(shaderRecordEXT)`.

Why it matters here:

- `shaderGroupBaseAlignment` constrains the start of every SBT region and any host-supplied offset into an SBT buffer.
- `shaderGroupHandleSize` fixes the minimum stride between adjacent records when no shader-record data is appended.
- `shaderGroupHandleAlignment` constrains the alignment of each record inside a region; the host can pad records to satisfy this and any larger power-of-two alignment.

### SBT indexing for `traceRayEXT`

`traceRayEXT(topLevelAS, rayFlags, cullMask, sbtRecordOffset, sbtRecordStride, missIndex, origin, tmin, dir, tmax, payloadLoc)` selects the hit-group record using `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`, and selects the miss shader using the miss-region address plus `missIndex` stride. Only the low 4 bits of `sbtRecordOffset` and `sbtRecordStride` are required to be honored for hit SBT indexing; only the low 16 bits of `missIndex` are required to be honored for miss SBT indexing. Implementations may ignore the upper bits.

Why it matters here:

- The test deliberately feeds values with extra high bits set in the maximum-offset and maximum-stride cases, then expects the implementation to use only the low bits, exercising the "ignored upper bits" rule.
- `indexing_hit`, `indexing_miss`, and `indexing_call` cases change which region's indexing rule is the focus.

### Shader Record block

`layout(shaderRecordEXT) buffer block { uvec4 info; };` exposes the per-record data after the shader-group handle. The host writes a unique value per record so the receiving shader can confirm which SBT slot it ran from.

Why it matters here:

- The `shaderrecord` variants replace per-index constant shaders with a single shader that reads `info` from its own shader record. If SBT indexing is correct, the read value equals the expected per-record value.
- The `handle_alignment` family uses shader-record buffers of varying size and element type as padding to drive shader-group handle alignment, then reads them back through an SSBO to verify no corruption occurred.

## One Concrete Example

Reconstructed rgen shader for the representative path `ray_tracing_pipeline.shader_binding_table.indexing_hit.sbt_offset_0.no_shaderrecord.0_0` (derived from the `initPrograms` literal in [vktRayTracingShaderBindingTableTests.cpp](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L788-L812)):

```glsl
#version 460 core
#extension GL_EXT_ray_tracing : require
layout(location = 0) rayPayloadEXT uvec4 hitValue;
layout(r32ui, set = 0, binding = 0) uniform uimage2D result;
layout(set = 0, binding = 1) uniform TraceRaysParamsUBO
{
    uvec4 trParams; // x = sbtRecordOffset, y = sbtRecordStride, z = missIndex
};
layout(set = 0, binding = 2) uniform accelerationStructureEXT topLevelAS;

void main()
{
  float tmin     = 0.0;
  float tmax     = 1.0;
  vec3  origin   = vec3(float(gl_LaunchIDEXT.x) + 0.5f, float(gl_LaunchIDEXT.y) + 0.5f, 0.5f);
  vec3  direct   = vec3(0.0, 0.0, -1.0);
  hitValue       = uvec4(0,0,0,0);
  traceRayEXT(topLevelAS, 0, 0xFF, trParams.x, trParams.y, trParams.z, origin, tmin, direct, tmax, 0);
  imageStore(result, ivec2(gl_LaunchIDEXT.xy), hitValue);
}
```

The rgen threads itself is the same across `indexing_hit`, `indexing_miss`, and `indexing_call`. The UBO is filled differently per family:

- `STT_HIT`: `trParams = (sbtRecordOffsetPassedToTraceRay, sbtRecordStride, 0)`. Ray geometry and instances are arranged so each pixel hits a known `(instanceOffset, geometryIndex)` pair; the expected hit shader is at `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride`.
- `STT_MISS`: `trParams = (0, 0, sbtRecordOffsetPassedToTraceRay)`. All instances use `instanceCustomIndex = 0` and the geometry is positioned so rays miss; the expected miss shader is `sbtRecordOffset`.
- `STT_CALL`: `trParams = (sbtRecordOffsetPassedToTraceRay, sbtRecordStride, 0)`. The closest-hit shader calls `executeCallableEXT(sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride, 0)`, and the callable shader writes its index back through callable data into the ray payload.

The 8x8 checkerboard places triangles on every odd `(x+y)` cell, so half the pixels hit and half the pixels miss. The reference image is built host-side using the same indexing formula.

## End-to-End Test Flow

```text
[host] choose shaderTestType (HIT/MISS/CALL), sbtOffset (0,4,7,16), shaderRecordPresent (true/false),
       sbtRecordOffset in [0..3], sbtRecordStride in [0..MAX] (HIT only; others fix stride=0)
[host] if max offset or max stride is selected, set the value passed to traceRayEXT with extra high bits
[host] build the checkerboard bottom-level acceleration structures (32 triangle sets, 3 geometries each)
[host] build the top-level acceleration structure with instance custom indices driving SBT indexing
[host] generate the rgen shader and a stack of chit_*, miss_*, call_* shaders (one per SBT slot), or the
       chit_shaderRecord / miss_shaderRecord / call_shaderRecord variants when shaderRecordPresent
[host] fill the UBO with (sbtRecordOffsetPassedToTraceRay, sbtRecordStride, missIndex) for the family
[host] create the ray tracing pipeline with all shader groups in the right group order:
       rgen=0, chit_*=1..N (or chit_call_*=1..N for CALL), miss_0=N+1, call_*=N+2.. (CALL only)
[host] create SBT buffers; the active region (hit for HIT, miss for MISS, callable for CALL) is given a
       non-zero shaderBindingTableOffset = sbtOffset * shaderGroupBaseAlignment
[host] if shaderRecordPresent, append a uvec4 (idx, 0, 0, 0) after each shader-group handle in the active
       region and flush the writes to the device
[host] clear the result image to 0xFF000000
[host] cmdTraceRays over 8x8x1
[device] rgen walks each pixel, traces one ray, imageStores the payload color into result
[device] hit/miss/callable shader writes its slot index (or shader-record info) into the payload
[host] copy result image to host-visible buffer
[host] recompute the expected per-pixel reference using the same SBT indexing formula and compare with
       tcu::intThresholdCompare (zero tolerance)
```

For `handle_alignment`, the flow differs:

```text
[host] choose alignment (1, 2, 4, 8, 16, 32) and useLongVec (false/true, non-VulkanSC only)
[host] compute geoCount = 32/alignment + 1 and per-geometry shader-record data
       (1 byte for align=1, 2 bytes for align=2, alignment/4 uint32_t elements for align>=4)
[host] build a single BLAS with geoCount triangle geometries translated along X
[host] build a TLAS with one instance referring to that BLAS
[host] create the pipeline: rgen=0, miss=1, chit=2..geoCount+1 (all chit modules are the same)
[host] create the hit SBT with stride = shaderGroupHandleSize + alignment, passing per-geometry
       shader-record data and disabling autoalign so the explicit alignment is preserved
[host] allocate an SSBO of size geoCount * stride, zero it
[host] cmdTraceRays over geoCount x 1 x 1
[device] chit reads srb.data[i] for i in [0..elementCount) and writes to ssbo.data[gl_LaunchIDEXT.x][i]
[host] read back the SSBO and compare byte-by-byte against the per-geometry shader-record data
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline GLSL rgen shader, identical for all `indexing_*` cases. Bound at group 0.
- For `indexing_hit`: one `chit_<idx>` closest-hit shader per SBT slot (`shaderCount[STT_HIT]` modules), each writing `uvec4(idx,0,0,1)`. When `shaderRecordPresent`, a single `chit_shaderRecord` reads its `info` from `layout(shaderRecordEXT)` and writes that.
- For `indexing_miss`: one `miss_<idx>` per SBT slot writing `uvec4(idx,0,0,1)`, plus the `miss_shaderRecord` variant.
- For `indexing_call`: `chit_call_<idx>` calls `executeCallableEXT(idx, 0)` and copies callable data to the payload; `call_<idx>` writes `uvec4(idx,0,0,1)` to callable data; the `*_shaderRecord` variants route the value through the shader-record block.
- For `handle_alignment`: rgen, miss, chit. The chit shader is parameterized at GLSL-generation time by alignment, element type (`uint8_t`, `uint16_t`, or `uint32_t`), element count, and the GLSL extension that exposes that integer width. The `useLongVec` variant uses `vector<elemType, elementCount>` instead of an array.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result storage image (`r32ui`, 8x8) | yes | yes (binding 0) | written by rgen via `imageStore` | copied to host-visible buffer | Carries per-pixel SBT-resolved shader index back to the host for comparison. |
| `TraceRaysParamsUBO` uniform buffer (1 `uvec4`) | yes | yes (binding 1) | read by rgen | no | Carries `(sbtRecordOffset, sbtRecordStride, missIndex)` from `initUniformBuffer` to the shader; for `indexing_miss`, x and y are 0 and z carries the miss index. |
| Top-level acceleration structure | yes | yes (binding 2) | read by rgen via `traceRayEXT` | no | Drives instance contribution to hit-group indexing; the checkerboard BLAS instances are arranged so the geometry and instance offsets cycle through the SBT. |
| Raygen SBT buffer | yes | yes (raygen region) | read by trace-rays fixed function | no | Single record, no shader-record data. |
| Miss SBT buffer | yes | yes (miss region) | read by trace-rays fixed function | no | One record per `miss_*` shader; offset by `sbtOffset * shaderGroupBaseAlignment` from the start of the buffer in MISS cases. |
| Hit SBT buffer | yes | yes (hit region) | read by trace-rays fixed function | no | Carries `shaderCount[STT_HIT]` records; in HIT cases the region base is `sbtOffset * shaderGroupBaseAlignment` bytes into the buffer. |
| Callable SBT buffer | yes | yes (callable region) | read by trace-rays fixed function for CALL | no | Carries `shaderCount[STT_CALL]` callable records; in CALL cases the region base is offset by `sbtOffset * shaderGroupBaseAlignment`. |
| Shader-record data inside SBT buffers | yes (host writes `uvec4(idx,0,0,0)` per record when `shaderRecordPresent`) | yes (inside SBT) | read by chit/miss/call through `layout(shaderRecordEXT)` | no | Lets a single shader variant read its own slot index, so the test does not need a different shader module per SBT slot. |
| SSBO (handle_alignment only) | yes | yes (binding 1) | written by chit | yes | Receives the per-geometry shader-record bytes copied by the chit shader for byte-by-byte host comparison. |
| Per-geometry shader-record data (handle_alignment only) | yes (built by `getRecordData`) | yes (inside hit SBT) | read by chit through `layout(shaderRecordEXT)` | indirectly via SSBO | The exact bytes that must round-trip through the SBT at the chosen alignment. |

## What Is Checked

- `indexing_hit`: For each pixel of the 8x8 image, the stored `uvec4.x` value must equal `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride` for hit pixels, and 0 for miss pixels. With `shaderrecord`, the value comes from the per-record shader-record `uvec4.x`.
- `indexing_miss`: For each pixel, the value must equal `sbtRecordOffset` for miss pixels (where `sbtRecordOffset` is what was passed as `missIndex`), and 0 for hit pixels. The test arranges all instances with the same custom index so any hit still routes to a single `chit_0` shader that writes 0.
- `indexing_call`: For each pixel, the value must equal `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride` for hit pixels, where the value is delivered by a callable shader selected by `executeCallableEXT` with that index. Miss pixels are 0.
- `handle_alignment`: The SSBO contents must equal the per-geometry shader-record bytes exactly, byte for byte, with zero tolerance.

All `indexing_*` checks use `tcu::intThresholdCompare` with `tcu::UVec4(0)` tolerance, comparing the result image against a host-recomputed reference image. The `handle_alignment` check is a byte-by-byte host comparison that logs the first mismatched byte.

## Behavior Parameter Identification

> **Behavior parameter:** test family (the direct child of `ray_tracing_pipeline.shader_binding_table`)
>
> **Candidate values:** `indexing_hit`, `indexing_miss`, `indexing_call`, `handle_alignment`

Each value exercises a distinct SBT property: hit-region indexing, miss-region indexing, callable-region indexing, or shader-group handle alignment with shader-record padding. The remaining registered dimensions (`sbt_offset`, `shaderrecord` presence, `sbtRecordOffset_sbtRecordStride` leaf, and `alignment_N[_longvec]` leaf) are configuration that stress the family's mechanism but do not change what is being tested.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `indexing_hit` | The implementation computed the hit-group SBT index using a different formula than `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`, ignored the `sbtOffset * shaderGroupBaseAlignment` buffer offset, mishandled shader-record data placement, or honored upper bits of `sbtRecordOffset`/`sbtRecordStride` that the spec allows to be ignored. |
| `indexing_miss` | The implementation indexed the miss region using something other than `missIndex`, ignored the SBT buffer offset into the miss region, or honored non-low-16 bits of `missIndex` that the spec allows to be ignored. |
| `indexing_call` | The implementation indexed the callable region using something other than the `sbtRecordOffset + instanceOffset + geometryIndex * sbtRecordStride` value passed to `executeCallableEXT`, or did not preserve that index through the callable-data path. |
| `handle_alignment` | The implementation did not preserve shader-group handle alignment or shader-record data integrity when shader-record buffers pad each handle to a power-of-two alignment between 1 and 32 bytes, including 8-bit, 16-bit, 32-bit, and long-vector shader-record element layouts. |

All four families report failure through the same host-side image or SSBO comparison. The shader itself never writes a fail flag; it writes the SBT-resolved value, and the host compares it against the expected formula.

## Important Variations and Special Cases

- **Extra-bits cases.** When `sbtRecordOffset` equals its maximum (`MAX_SBT_RECORD_OFFSET = 3`) or `sbtRecordStride` equals its maximum, the value passed to `traceRayEXT` is OR'd with `~((1u << 4) - 1)` for hit/stride/offset and `~((1u << 16) - 1)` for `missIndex`. The leaf name gains `_extrabits` or `_extraSBTRecordStrideBits`. These cases exercise the spec rule that only the low bits are required for SBT indexing.
- **`shaderrecord` variants.** When `shaderRecordPresent` is true, the active region uses a single shader module that reads `info` from `layout(shaderRecordEXT)`, and the host writes a unique `uvec4(idx,0,0,0)` per record. This stresses both SBT indexing and shader-record data placement.
- **`sbt_offset_*` variants.** The `sbtOffset` value (0, 4, 7, 16) multiplies `shaderGroupBaseAlignment` to produce the host-supplied offset into the active SBT buffer. Non-zero values verify the implementation honors `shaderBindingTableOffset` correctly when computing region addresses.
- **`handle_alignment` long-vector variants.** Non-VulkanSC builds add `_longvec` leaves that use `vector<elemType, elementCount>` instead of arrays for the shader-record block, gated on `VK_EXT_shader_long_vector`.
- **8-bit and 16-bit shader-record elements.** `handle_alignment` with `alignment=1` requires `shaderInt8` and `storageBuffer8BitAccess`; `alignment=2` requires `shaderInt16` and `storageBuffer16BitAccess`. These cases are skipped if the device lacks the features.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Category root registration | [vktRayTracingShaderBindingTableTests.cpp#L1617-L1646](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1617-L1646) | Builds the `shader_binding_table` group and attaches all four direct children. |
| Indexing test parameter construction | [vktRayTracingShaderBindingTableTests.cpp#L1622-L1722](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1622-L1722) | Defines the indexing_hit/miss/call family loop, sbt_offset values, shader-record presence, and the extra-bits scheme. |
| Handle-alignment family construction | [vktRayTracingShaderBindingTableTests.cpp#L1724-L1743](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1724-L1743) | Defines the alignment values and long-vector variants. |
| `TestParams` struct | [vktRayTracingShaderBindingTableTests.cpp#L110-L122](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L110-L122) | Captures sbtOffset, sbtRecordOffset/Stride values (and the versions passed to traceRay), and shaderRecordPresent. |
| UBO fill per family | [vktRayTracingShaderBindingTableTests.cpp#L268-L304](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L268-L304) | Shows how `trParams.x/y/z` map to sbtRecordOffset, sbtRecordStride, or missIndex per family. |
| SBT construction per family | [vktRayTracingShaderBindingTableTests.cpp#L456-L639](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L456-L639) | Shows the `shaderBindingTableOffset` math, shader-record aligned size, and shader-record buffer fills. |
| Shader generation | [vktRayTracingShaderBindingTableTests.cpp#L782-L944](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L782-L944) | Generates rgen, chit_*, miss_*, call_*, and the *_shaderRecord variants. |
| Reference image computation | [vktRayTracingShaderBindingTableTests.cpp#L641-L709](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L641-L709) | Host-side re-derivation of expected per-pixel shader index for each family. |
| Handle-alignment shader and pipeline | [vktRayTracingShaderBindingTableTests.cpp#L1169-L1613](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1169-L1613) | Implements the `ShaderGroupHandleAlignmentParams` struct, GLSL element type selection, SBT construction with explicit alignment, and SSBO byte-by-byte comparison. |
| Support checks | [vktRayTracingShaderBindingTableTests.cpp#L765-L780](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L765-L780), [vktRayTracingShaderBindingTableTests.cpp#L1278-L1322](../../../modules/vulkan/ray_tracing/vktRayTracingShaderBindingTableTests.cpp#L1278-L1322) | Feature and property gates for both families. |

## Questions / Risk Points for User Audit

- Is the SBT-indexing formula description accurate for the implementation? The Vulkan spec defines hit SBT indexing as `instanceContributionToHitGroupIndex + sbtRecordOffset + geometryIndex * sbtRecordStride`, with `instanceContributionToHitGroupIndex` coming from `VkAccelerationStructureInstanceKHR::instanceShaderBindingTableRecordOffset`. The CTS host sets this contribution via `addInstance(..., 0u, 0xFF, i)` for HIT/CALL and `0` for MISS, so the formula maps to `i + sbtRecordOffset + geometryIndex * sbtRecordStride`. Confirm this matches the reader's mental model.
- Is the `extra-bits` explanation correct? The test feeds `MAX_SBT_RECORD_OFFSET | (~((1u << 4) - 1))` for non-miss cases and `MAX_SBT_RECORD_OFFSET | (~((1u << 16) - 1))` for miss cases, expecting only the low 4 or 16 bits to be honored. Confirm this matches the Vulkan spec's "valid usage" allowance.
- Is the `handle_alignment` mechanism described correctly? The host calls `createShaderBindingTable` with `shaderRecordSize = alignment` and `autoalign = false`, producing SBT records with stride `shaderGroupHandleSize + alignment` and per-geometry shader-record data of that size. Confirm this is the intended alignment-stressing mechanism.
- Is the SSBO layout in the `handle_alignment` chit shader correct? The shader writes `ssbo.data[gl_LaunchIDEXT.x][i] = srb.data[i]`, and the host reads the SSBO as `geoCount * hitSBTStride` bytes. The shader writes only `elementCount` bytes per geometry, leaving the rest of the stride untouched.

## Conversion Notes for Final Wiki Rewrite

- The brief's `Background Knowledge` distills into a short list of page-specific prerequisites: SBT region layout, `shaderGroupBaseAlignment` vs `shaderGroupHandleSize` vs `shaderGroupHandleAlignment`, `traceRayEXT` SBT indexing formula with low-bit-only semantics, and the `layout(shaderRecordEXT)` mechanism.
- The representative walkthrough uses the `indexing_hit.sbt_offset_0.no_shaderrecord.0_0` rgen shader as the default, because it is the simplest case that exercises the hit SBT indexing formula. A second walkthrough is not needed because the rgen shader is shared across the indexing families; family differences are in the host-side UBO and SBT construction, which belong in the runtime section.
- The brief's source-mapping table compresses into the Source Reference Appendix; line ranges are kept for traceability.
- The `### Failure Cause Mapping` table is copied directly into the final page's `## Failure Meaning` section.
- The "extra-bits" and `shaderrecord` variations belong in `## Behavior Parameters` and `## Case Pruning` rather than repeated in failure analysis.
- Beginner scaffolding in `One Concrete Example` and `End-to-End Test Flow` is shortened; the final page uses prose and the runtime section instead of `[host]`/`[device]` markers.
