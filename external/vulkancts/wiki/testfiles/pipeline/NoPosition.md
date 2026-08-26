## Overview

**Core question:** Can a graphics pipeline execute the generated pre-rasterization stage combinations when selected stages omit assignments to `gl_Position`?

- [`vktPipelineNoPositionTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1) implements the `no_position` test family under each pipeline construction variant.
- The family generates vertex, optional tessellation, and optional geometry shaders. A stage mask selects which stages are present; a write mask independently selects which present stages assign the `Position` built-in.
- `implicit_declarations` and `explicit_declarations` test the same behavior with GLSL's implicit built-in interface or explicit `gl_PerVertex` blocks.
- `basic` checks the blue color attachment after the draw. `ssbo_writes` adds per-stage atomic counters, so CTS can observe execution of selected pre-rasterization stages separately from the attachment result. In `device_index_as_view_index` cases, a loop-bound mismatch skips the attachment comparison, leaving the counters as the effective oracle.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

- The Vulkan `Position` built-in transports the position output of the last pre-rasterization stage to primitive assembly, clipping, and rasterization. Vertex, tessellation-control, tessellation-evaluation, and geometry shaders can declare it; later stages consume the preceding stage's output through their interface. See [the `Position` built-in definition](../../../../vulkan-docs/src/chapters/interfaces.adoc#L4147-L4165).
- An explicit `gl_PerVertex` block and GLSL's implicit declaration describe the same built-in interface form for this test. A `gl_Position` assignment is independent of that declaration.
- A blue color image is a completion and readback check in this family. It is not proof that rasterization produced the color, because the render pass clears the attachment to blue and the fragment shader writes the same blue value.

## Registration Hierarchy

```text
pipeline.monolithic.no_position
├── implicit_declarations
└── explicit_declarations
```

[`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1094-L1190) adds both declaration forms. Each form contains the `basic` and `ssbo_writes` intermediate nodes; those nodes then select a view mode, a legal selected-stage mask, and every subset of that mask as a write mask. [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L171-L175) attaches this family to each pipeline construction variant.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Declaration form | `implicit_declarations`, `explicit_declarations` | Chooses GLSL's implicit interface or emitted `gl_PerVertex` input/output blocks. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L255-L375) |
| Observation mode | `basic`, `ssbo_writes` | Chooses color-image checking alone or color-image checking plus per-stage SSBO counters. | [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1106-L1112) |
| View mode | `single_view`, `multiview`, `device_index_as_view_index` | Selects one view, multiview layers, or a device-group path that maps device index to view index. | [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1112-L1136) |
| Selected stages | `v`, `v_c_e`, `v_g`, `v_c_e_g` | Installs vertex alone, vertex plus tessellation, vertex plus geometry, or all available pre-rasterization stages. Vertex is mandatory and tessellation-control and tessellation-evaluation occur together. | [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1138-L1148) |
| Position write mask | each subset of the selected stages | Names the selected stages that assign `gl_Position`; for example, `v1_c0_e1_g0`. | [`getWriteSubCases()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L117-L124), [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1149-L1177) |
| Pipeline construction type | pipeline construction variants | Repeats the family under the construction variants created by the pipeline test category. | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L171-L175) |

The source registers one and two views for `basic`; `ssbo_writes` also registers `device_index_as_view_index`. Shader-object construction omits any view mode other than `single_view`.

## Behavior Parameters

The intermediate node below each declaration form is the primary behavioral axis. It changes the observation method rather than merely changing shader syntax or a generated configuration.

### basic: color attachment observation

`basic` generates the selected shader stages and draws the triangle without an SSBO. The render pass clears the `VK_FORMAT_R8G8B8A8_UNORM` attachment to blue, and the fragment shader writes that same blue value. CTS copies every view to a host-visible buffer and requires each pixel to remain blue.

This path checks the generated pipeline, attachment handling, submission, and copyback path. It does not use the color value to claim that a no-position primitive rasterized.

### ssbo_writes: stage execution observation

`ssbo_writes` adds a `std430` storage buffer at set `0`, binding `0`. Each selected pre-rasterization stage atomically increments its own counter range, with `gl_ViewIndex` selecting a per-view counter when required. The host normally checks the color image and then checks that each selected stage has reached its minimum counter value. For `device_index_as_view_index`, however, `params.numViews` is zero while the runtime view count comes from the physical-device group; the image-validation loop uses the former and therefore checks no layers.

This path retains the `basic` attachment check for `single_view` and `multiview` and adds an execution signal that does not depend on the fragment output. It also enables `device_index_as_view_index` coverage, where only the SSBO counters are actually validated.

## Shader Analysis

The generator emits GLSL directly from the declaration, stage, write-mask, and SSBO choices. The representative shader below is a deliberately empty-position vertex stage: it declares the explicit output interface but does not assign `gl_Position`.

### Representative Shader Walkthrough 1

#### Parameter Values Chosen

Representative path:

```text
dEQP-VK.pipeline.monolithic.no_position.explicit_declarations.basic.single_view.v0
```

| Parameter choice | Meaning in this representative case |
|------------------|-------------------------------------|
| `explicit_declarations` | The vertex shader emits an explicit output `gl_PerVertex` block. |
| `basic` | The case has no SSBO counters; CTS checks the color attachment after the draw. |
| `single_view` | The render pass uses one color-image layer. |
| `v0` | Vertex is the only selected pre-rasterization stage and does not assign `gl_Position`. |

#### Purpose

This vertex shader exercises the explicit interface declaration while omitting the `Position` assignment. It provides the simplest generated no-position case: no tessellation or geometry stage can produce a later position value, and no SSBO instrumentation changes the shader body.

#### Structural Design

| Part | Role in this representative shader |
|------|------------------------------------|
| `in_pos` input | Preserves the generated vertex-input declaration even though this write-mask variant does not consume it. |
| Explicit `gl_PerVertex` output | Declares the built-in output interface, including `gl_Position`. |
| Empty `main` | Omits the assignment selected by the `v0` write mask. |

#### Shader Code

```glsl
#version 450

/// Generated vertex-input declaration. This v0 case leaves it unused.
layout (location=0) in vec4 in_pos;

/// Explicit output interface selected by explicit_declarations.
out gl_PerVertex
{
    vec4 gl_Position;
    float gl_PointSize;
    float gl_ClipDistance[];
    float gl_CullDistance[];
};

void main (void)
{
    /// The v0 write mask emits no gl_Position assignment.
}
```

#### Additional Info

- [`NoPositionCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L255-L273) emits `gl_Position = in_pos;` only when the vertex bit is set in `writeStages`.
- The generated fragment shader remains present and writes the same blue value used to clear the attachment, so the `basic` result does not distinguish clear from fragment output.

#### Parameter Variation Summary

| Parameter dimension | Shader-level variation from this shader | Evidence |
|---------------------|---------------------------------------|----------|
| Write mask | A set vertex bit adds `gl_Position = in_pos;`; later-stage bits add copying or interpolation assignments in their own generated stages. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L270-L372) |
| Declaration form | `implicit_declarations` omits the explicit `gl_PerVertex` text while keeping the stage generator and assignment choices. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L260-L267) |
| Selected stages | Tessellation-control, tessellation-evaluation, and geometry add their generated shader modules and their stage-specific optional position writes. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L275-L375) |
| `ssbo_writes` and view mode | Adds the storage-buffer declaration and atomic increments; multiview and device-group paths index the counters with `gl_ViewIndex`. | [`initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L225-L253) |

#### SPIR-V

- Status: generated and validated
- Source: reconstructed `GLSL` from this walkthrough
- Stage: `vert`
- Target SPIRV version: `spirv1.0`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
; SPIR-V
; Version: 1.0
; Generator: Khronos Glslang Reference Front End; 11
; Bound: 16
; Schema: 0
               OpCapability Shader
          %1 = OpExtInstImport "GLSL.std.450"
               OpMemoryModel Logical GLSL450
               OpEntryPoint Vertex %main "main" %in_pos %_
               OpSource GLSL 450
               OpName %main "main"
               OpName %in_pos "in_pos"
               OpName %gl_PerVertex "gl_PerVertex"
               OpMemberName %gl_PerVertex 0 "gl_Position"
               OpMemberName %gl_PerVertex 1 "gl_PointSize"
               OpMemberName %gl_PerVertex 2 "gl_ClipDistance"
               OpMemberName %gl_PerVertex 3 "gl_CullDistance"
               OpName %_ ""
               OpDecorate %in_pos Location 0
               OpDecorate %gl_PerVertex Block
               OpMemberDecorate %gl_PerVertex 0 BuiltIn Position
               OpMemberDecorate %gl_PerVertex 1 BuiltIn PointSize
               OpMemberDecorate %gl_PerVertex 2 BuiltIn ClipDistance
               OpMemberDecorate %gl_PerVertex 3 BuiltIn CullDistance
       %void = OpTypeVoid
          %3 = OpTypeFunction %void
      %float = OpTypeFloat 32
    %v4float = OpTypeVector %float 4
%_ptr_Input_v4float = OpTypePointer Input %v4float
     %in_pos = OpVariable %_ptr_Input_v4float Input
       %uint = OpTypeInt 32 0
     %uint_1 = OpConstant %uint 1
%_arr_float_uint_1 = OpTypeArray %float %uint_1
%gl_PerVertex = OpTypeStruct %v4float %float %_arr_float_uint_1 %_arr_float_uint_1
%_ptr_Output_gl_PerVertex = OpTypePointer Output %gl_PerVertex
          %_ = OpVariable %_ptr_Output_gl_PerVertex Output
       %main = OpFunction %void None %3
          %5 = OpLabel
               OpReturn
               OpFunctionEnd
```

</details>

## Runtime Execution and Result Checking

- The case uses a `64x64` `VK_FORMAT_R8G8B8A8_UNORM` color image with color-attachment and transfer-source usage. The host writes three triangle positions into a host-visible vertex buffer.
- For multiview, the instance creates an array image and configures the render pass with multiview masks. The device-group mode derives the number of views from the selected physical-device group and creates one subpass per view.
- The pipeline installs wrappers only for selected pre-rasterization shaders, always installs the generated fragment shader, and chooses patch-list topology when tessellation is present.
- The render pass clears each attachment to blue. CTS binds the pipeline, binds the SSBO descriptor set when present, binds the vertex buffer, and records one three-vertex draw per subpass.
- After the draw, CTS transitions the color image for transfer, copies all layers to a host-visible verification buffer, adds a transfer-to-host barrier, submits, and waits. SSBO cases also add an all-graphics shader-write-to-host-read barrier.
- CTS scans every copied pixel for the blue value in `single_view` and `multiview`. In `device_index_as_view_index`, it still copies all runtime layers, but the scan iterates to `m_params.numViews` (zero for this mode) instead of `m_numViews`, so no pixels are checked. For `ssbo_writes`, CTS invalidates the host-visible SSBO allocation and checks counters for the selected stages: at least `3` for vertex, tessellation-control, and tessellation-evaluation; at least `1` for geometry. A nonzero multiple of the minimum is accepted.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `basic` | The generated stage/interface combination, pipeline execution, color attachment handling, or image readback does not preserve the expected blue image. |
| `ssbo_writes` | A `basic`-path cause, or selected pre-rasterization stages do not execute or expose their atomic SSBO writes as required. |

### Cause Analysis

#### Generated interface, pipeline, attachment, or readback failure

**Possible failure symptoms:** CTS finds a non-blue pixel in a copied color-image layer and reports its pixel coordinates and layer.

**Possible implementation causes:** The source does not distinguish the stage of failure. An implementation can investigate generation or compilation of the selected built-in interface, pipeline creation and execution, color attachment clearing or fragment output, image layout transition and copy, and host-visible readback. The test's color oracle alone cannot isolate rasterization because clear and fragment output are both blue.

#### Selected-stage SSBO execution or visibility failure

**Possible failure symptoms:** An `ssbo_writes` case reports an unexpected counter for a view and shader stage. A selected vertex, tessellation-control, or tessellation-evaluation stage has zero or a value that is not a multiple of `3`; a selected geometry stage has zero or a value that is not a multiple of `1`.

**Possible implementation causes:** The generated stage may fail to execute, its `atomicAdd` may not update the storage buffer as required, or the shader-write-to-host-read synchronization and host invalidation path may fail to make the counter visible. Source-level investigation is needed to distinguish these causes for a specific failing stage and view.

For `device_index_as_view_index`, a passing case does not establish that the attachment contents were blue: registration stores `0` in `params.numViews`, and the image-validation loop uses that value rather than the runtime `m_numViews`. The counter checks still cover every physical-device-derived view.

## Case Pruning

### Requirement-based pruning

- Cases with tessellation require `tessellationShader`; cases with geometry require `geometryShader`.
- Multiview cases require `VK_KHR_multiview`, the `multiview` feature, and the associated tessellation or geometry multiview features when those stages are selected. Their view count must not exceed `maxMultiviewViewCount`.
- `ssbo_writes` requires `vertexPipelineStoresAndAtomics`.
- `device_index_as_view_index` requires `VK_KHR_device_group_creation` and `VK_KHR_device_group`.
- Every case also passes [`checkPipelineConstructionRequirements()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L443-L444) for its construction type.

### Design-based pruning

- The generator requires a vertex stage and rejects masks that contain only one of the two tessellation stages.
- It registers each write-mask subset only once through [`getWriteSubCases()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L117-L124).
- `basic` stops at two view modes. Only `ssbo_writes` includes `device_index_as_view_index` because that path needs the per-view counter observation.
- Shader-object construction skips `multiview` and `device_index_as_view_index`, so its mustpass files contain only `single_view` cases.

## Key Takeaways

- The no-position family varies interface declaration and `gl_Position` assignment independently across legal pre-rasterization stage chains.
- A checked blue attachment result verifies the attachment and readback path, but the SSBO mode supplies the family’s direct selected-stage execution signal. The `device_index_as_view_index` leaves currently skip the blue-pixel scan because its loop bound remains zero.
- The write-mask suffixes are generated identifiers: `v1_c0_e1_g0` means vertex and tessellation-evaluation write `gl_Position`, while tessellation-control and geometry do not.
- Current mustpass coverage contains `300` `no_position` cases in each monolithic, pipeline-library, fast-linked-library, and Vulkan SC monolithic file, and `120` cases in each shader-object file; the shader-object files retain only `single_view` paths.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Family registration | [`createNoPositionTests()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L1094-L1190) | Registers declaration, observation, view, stage, and write-mask paths. |
| Shader generator | [`NoPositionCase::initPrograms()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L213-L394) | Generates stage GLSL, explicit declarations, optional position assignments, and SSBO instrumentation. |
| Support gate | [`NoPositionCase::checkSupport()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L401-L445) | Checks stage features, multiview, atomics, device groups, and construction requirements. |
| Device-group setup | [`NoPositionInstance::createDeviceGroup()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L461-L611) | Creates the device-group path used by `device_index_as_view_index`. |
| Runtime and validation | [`NoPositionInstance::iterate()`](../../../modules/vulkan/pipeline/vktPipelineNoPositionTests.cpp#L684-L1089) | Creates resources, records draws, copies the image, and checks pixels and SSBO counters. |
| Pipeline-category attachment | [`createChildren()`](../../../modules/vulkan/pipeline/vktPipelineTests.cpp#L171-L175) | Attaches `no_position` under each pipeline construction variant. |
| Mustpass coverage | [`monolithic.txt`](../../../mustpass/main/vk-default/pipeline/monolithic/monolithic.txt), [`pipeline-library.txt`](../../../mustpass/main/vk-default/pipeline/pipeline-library.txt), [`shader-object-linked-spirv.txt`](../../../mustpass/main/vk-default/pipeline/shader-object-linked-spirv.txt) | Provide representative standard, library, and shader-object registrations for the counts above. |
