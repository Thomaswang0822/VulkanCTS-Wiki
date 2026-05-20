# vktRobustnessExtsTests.cpp

## Overview

This page documents the Vulkan CTS robustness extension tests implemented in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1-L23). The file registers
three top-level robustness roots: `robustness.robustness2`, `robustness.image_robustness`, and, outside Vulkan SC builds,
`robustness.pipeline_robustness`. The same generator creates a large matrix of descriptor, format, shader-stage, image
view, null-descriptor, descriptor-update, and pipeline-robustness cases, with reduced matrices for `64b_indexing` and
pipeline-robustness coverage.

The root robustness dispatcher attaches these factories to the `robustness` category in
[vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L88). The public declarations are in
[vktRobustnessExtsTests.hpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.hpp#L34-L36), and the source creates
the literal group names in
[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4358-L4372).

## Role of file

[vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp) is an implementation-heavy
registered test file with local factory functions. It owns:

- `robustness2`, built by `createRobustness2Tests()` and backed by `VK_KHR_robustness2` or `VK_EXT_robustness2`
  feature queries
  ([factory](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4311-L4322),
  [feature query](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L543-L546)).
- `image_robustness`, built by `createImageRobustnessTests()` and backed by `VK_EXT_image_robustness` feature queries
  ([factory](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4324-L4327),
  [feature query](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L540-L541)).
- `pipeline_robustness`, built only when `CTS_USES_VULKANSC` is not defined and split into nested `robustness2` and
  `image_robustness` children
  ([factory](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4329-L4345),
  [root guard](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L86-L88)).

The file creates custom singleton devices that enable the requested robustness feature set rather than relying on the
context device, because the regular context device may keep these robustness features disabled
([singleton setup](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L78-L180)).

## Source code link

- Source: [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1-L4376)
- Header declarations: [vktRobustnessExtsTests.hpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.hpp#L34-L36)
- Root dispatcher: [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L88)
- Mustpass evidence: [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L1866-L96873)

## Inspected related files

| File | Evidence used |
|------|---------------|
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L69-L180) | Robustness feature flags and singleton-device feature chaining. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L250-L336) | `Stage`, `PipelineRobustnessCase`, and `CaseDef` parameter fields used by generated cases. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L519-L738) | Main per-case support checks for robustness2, image robustness, pipeline robustness, 64-bit indexing, formats, and descriptors. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1070-L1993) | Generated GLSL source, out-of-bounds expectations, null-descriptor queries, and shader-stage variants. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2021-L3495) | Runtime descriptor, image, buffer, pipeline, dispatch/draw, copy-back, and result verification flow. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3497-L3820) | `misc.out_of_bounds_stride` tests and their support/verification logic. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4308) | Shared registration generator, parameter arrays, pruning rules, generated direct children, and `misc` group. |
| [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4311-L4372) | Top-level and nested factory functions with literal group names. |
| [vktRobustnessExtsTests.hpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.hpp#L34-L36) | Public factory declarations. |
| [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L88) | Category-level registration and the non-VulkanSC guard for `pipeline_robustness`. |
| [robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L1866-L96873) | Mustpass evidence for `image_robustness`, `pipeline_robustness`, and `robustness2` generated paths. |

## Registration Hierarchy

Because one source file registers multiple top-level roots, this section uses separate canonical one-level tree blocks for
each documented root or nested root owned by this file. Each tree expands only the direct children of that root.

### `robustness.robustness2`

```text
robustness.robustness2
├── bind
├── push (non-VulkanSC only)
├── misc
└── 64b_indexing (non-VulkanSC only)
```

The `bind` and `push` groups come from `pushCases[]`, while `misc` is added for robustness2 cases that are not
`64b_indexing`
([push cases](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3947-L3952),
[misc creation](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4294-L4308)). The non-VulkanSC
`64b_indexing` group is appended after the regular robustness2 matrix
([64-bit-indexing child](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4315-L4321)). Mustpass evidence
shows examples for `64b_indexing`, `bind`, `misc`, and `push`
([robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L15030-L15389),
[robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L15390-L61929),
[robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L61930-L96873)).

### `robustness.robustness2.64b_indexing` (non-VulkanSC only)

```text
robustness.robustness2.64b_indexing
├── bind
└── push
```

The nested `64b_indexing` group calls the same generator with `uses64BitIndexing=true` and `robustness2=true`
([64-bit-indexing generator call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4315-L4320)). Its direct
children are still generated from `pushCases[]`, but the matrix is pruned by `uses64BitIndexing` conditions
([push cases](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3947-L3952),
[64-bit pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3974-L3981),
[descriptor pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4017-L4020)).

### `robustness.image_robustness`

```text
robustness.image_robustness
├── bind
└── push (non-VulkanSC only)
```

The `image_robustness` root calls the shared generator with `robustness2=false`, `pipelineRobustness=false`, and
`uses64BitIndexing=false`
([image factory](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4324-L4327)). In this mode, the descriptor
matrix is reduced to image descriptor cases by choosing `imgDescCases[]` instead of `fullDescCases[]`
([descriptor selection](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3876-L3879),
[descriptor switch](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3999-L4002)). Mustpass examples show
`bind` and `push` paths for this root
([robustness.txt](../../../mustpass/main/vk-default/robustness.txt#L1866-L13745)).

### `robustness.pipeline_robustness` (non-VulkanSC only)

```text
robustness.pipeline_robustness
├── robustness2
└── image_robustness
```

The pipeline-robustness root is compiled outside Vulkan SC builds and creates two direct children with literal names
`robustness2` and `image_robustness`
([pipeline root factory](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4329-L4345)). The root dispatcher
also registers `pipeline_robustness` only outside Vulkan SC builds
([dispatcher guard](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L86-L88)).

### `robustness.pipeline_robustness.robustness2` (non-VulkanSC only)

```text
robustness.pipeline_robustness.robustness2
└── bind
```

The nested pipeline-robustness `robustness2` child calls the shared generator with `robustness2=true` and
`pipelineRobustness=true`
([nested robustness2 call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4334-L4338)). Although
`pushCases[]` contains `push`, the mustpass file observed for this subtask contains only `bind` as a direct child for
`robustness.pipeline_robustness.robustness2`
([mustpass range](../../../mustpass/main/vk-default/robustness.txt#L14019-L14785)).

### `robustness.pipeline_robustness.image_robustness` (non-VulkanSC only)

```text
robustness.pipeline_robustness.image_robustness
└── bind
```

The nested pipeline-robustness `image_robustness` child calls the shared generator with `robustness2=false` and
`pipelineRobustness=true`
([nested image-robustness call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4340-L4344)). The inspected
mustpass file contains only `bind` as a direct child for `robustness.pipeline_robustness.image_robustness`
([mustpass range](../../../mustpass/main/vk-default/robustness.txt#L13875-L14018)).

## Test Families

### bind

The `bind` family uses ordinary descriptor-set binding and descriptor-set updates. It is the first value in `pushCases[]`
([push cases](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3947-L3952)). Runtime descriptor setup updates
and binds a descriptor set when `pushDescriptor` is false
([descriptor updates](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2847-L2869)).

### push

The `push` family is present only outside Vulkan SC builds because `pushCases[]` adds it under the non-VulkanSC guard
([push cases](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3947-L3952)). Push-descriptor cases use
`VK_DESCRIPTOR_SET_LAYOUT_CREATE_PUSH_DESCRIPTOR_BIT_KHR` and either `cmdPushDescriptorSetWithTemplate` or
`cmdPushDescriptorSet`
([layout flag](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2101-L2106),
[template push](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2812-L2825),
[direct push](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2849-L2857)). Support is gated on
`VK_KHR_push_descriptor`
([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L706-L707)).

### misc

The `misc` child is added only for `robustness2` matrices when `uses64BitIndexing` is false
([misc guard](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4294-L4308)). It contains two
out-of-bounds-stride cases: `out_of_bounds_stride` and `out_of_bounds_stride_dynamic_stride`
([case names](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4298-L4304)). These tests verify that, with
robustBufferAccess2, a vertex attribute fully inside the buffer range is considered in-bounds even when the whole binding
stride chunk would extend past the buffer end
([test goal](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3497-L3508)).

### 64b_indexing

The `64b_indexing` child is a nested non-VulkanSC child of `robustness.robustness2`. The generator marks cases with
`uses64BitIndexing=true`, prunes the descriptor set to storage-buffer cases, and sets
`VK_PIPELINE_CREATE_2_64_BIT_INDEXING_BIT_EXT` through a `VkPipelineCreateFlags2CreateInfo` chain
([generator call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4315-L4320),
[storage-buffer-only pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4017-L4020),
[pipeline flag](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2896-L2904)). Support requires
`shader64BitIndexing`
([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L721-L722)).

### robustness2

Under `robustness.pipeline_robustness`, the `robustness2` child reuses the same robustness2 descriptor semantics but
passes `pipelineRobustness=true`
([nested call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4334-L4338)). Pipeline-robustness cases attach
`VkPipelineRobustnessCreateInfoEXT` to compute, ray tracing, monolithic graphics, or graphics-pipeline-library pipeline
creation according to the selected pipeline case
([compute pNext](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2931-L2939),
[ray-tracing pNext](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2987-L2995),
[graphics pNext/GPL](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3204-L3349)).

### image_robustness

Under `robustness.pipeline_robustness`, the `image_robustness` child reuses image robustness semantics with
`pipelineRobustness=true`
([nested call](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4340-L4344)). In image-robustness mode,
out-of-bounds image checks allow the relaxed zero-or-one alpha behavior visible in generated shader comparisons
([texel check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1614-L1619),
[normalized check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1714-L1718)).

### Generated nested descriptor and stage matrix

Below `bind` and `push`, the generator creates nested groups in this order: descriptor-update mode, format, unroll mode,
volatility mode, descriptor type, optional read/write grouping for storage buffers, format-qualifier mode, length/null
mode, sample count, image view type, and leaf tests named by shader stage plus optional pipeline-construction and queue
suffixes
([loop nest](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3964-L4291),
[leaf name](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4248-L4253)). The parseable hierarchy trees above
intentionally stop at one level below each documented root.

## Parameter dimensions and observed values

| Dimension | Observed values | Evidence |
|-----------|-----------------|----------|
| Top-level roots | `robustness2`, `image_robustness`, `pipeline_robustness` outside Vulkan SC | Factory names and dispatcher registration in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4358-L4372) and [vktRobustnessTests.cpp](../../../modules/vulkan/robustness/vktRobustnessTests.cpp#L84-L88). |
| Pipeline-robustness nested roots | `robustness2`, `image_robustness` | Nested group creation in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4334-L4344). |
| Descriptor update / direct child | `bind`, `push` outside Vulkan SC | `pushCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3947-L3952). |
| Template dimension | `notemplate`, `template` outside Vulkan SC | `tempCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3940-L3945). |
| Formats | `r32i`, `r32ui`, `r32f`, `rg32i`, `rg32ui`, `rg32f`, `rgba32i`, `rgba32ui`, `rgba32f`, `r64i`, `r64ui` | `fmtCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3850-L3862). |
| Robustness2 descriptor types | `uniform_buffer`, `storage_buffer`, `uniform_buffer_dynamic`, `storage_buffer_dynamic`, `uniform_texel_buffer`, `storage_texel_buffer`, `storage_image`, `sampled_image`, `vertex_attribute_fetch` | `fullDescCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3864-L3874). |
| Image-robustness descriptor types | `storage_image`, `sampled_image` | `imgDescCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3876-L3879). |
| Buffer/null lengths for 32-bit formats | `null_descriptor`, `img`, `len_4`, `len_8`, `len_12`, `len_16`, `len_20`, `len_31`, `len_32`, `len_33`, `len_35`, `len_36`, `len_39`, `len_41`, `len_252`, `len_256`, `len_260` | `fullLenCases32Bit[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3881-L3885). |
| Buffer/null lengths for 64-bit formats | `null_descriptor`, `img`, `len_8`, `len_16`, `len_24`, `len_32`, `len_40`, `len_62`, `len_64`, `len_66`, `len_70`, `len_72`, `len_78`, `len_80`, `len_504`, `len_512`, `len_520` | `fullLenCases64Bit[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3887-L3891). |
| Image-robustness lengths | `img` | `imgLenCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3893-L3895). |
| Image view types | `1d`, `2d`, `3d`, `cube`, `1d_array`, `2d_array`, `cube_array` | `viewCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3897-L3905). |
| Sample counts | `samples_1`, `samples_4` | `sampCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3907-L3910). |
| Shader stages / leaf prefixes | `comp`, `frag`, `vert`, `rgen` outside Vulkan SC | `stageCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3912-L3923). |
| Queue suffix | no suffix, `_compute` for compute/raygen queue variant | `queueCases[]` and queue pruning in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3925-L3928) and [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4209-L4215). |
| Volatility | `nonvolatile`, `volatile` | `volCases[]` and store-only pruning in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3930-L3933) and [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4101-L4103). |
| Loop unroll mode | `dontunroll`, `unroll` | `unrollCases[]` in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3935-L3938). |
| Format qualifier | `no_fmt_qual`, `fmt_qual` | `fmtQualCases[]` and descriptor-type pruning in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3954-L3957) and [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4050-L4054). |
| Storage-buffer access mode | `readwrite`, `readonly` | `readOnlyCases[]` and storage-buffer-only pruning in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3959-L3962) and [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4034-L4043). |
| Pipeline-robustness cases | disabled, monolithic, fast GPL, optimized GPL | `PipelineRobustnessCase` and case expansion in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L258-L273) and [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4182-L4205). |

Observed reductions:

- Pipeline-robustness and `64b_indexing` cases keep only `r32ui`, `rgba32f`, and `r64i` formats
  ([format pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3974-L3981)).
- Pipeline-robustness cases keep only `uniform_buffer`, `storage_buffer`, `sampled_image`, and `vertex_attribute_fetch`
  descriptor types
  ([descriptor pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4008-L4016)).
- `64b_indexing` cases keep only `storage_buffer` descriptor cases
  ([64-bit-indexing descriptor pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4017-L4020)).
- Pipeline-robustness cases skip multisample cases, most image view types, raygen leaf stages, null descriptors, and
  non-power-of-two or image-only robustness2 length cases
  ([sample pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4112-L4114),
  [view pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4142-L4149),
  [raygen pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4160-L4168),
  [length pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4093-L4099),
  [null pruning](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L4170-L4171)).

## Support / feature requirements

- All cases require `VK_KHR_get_physical_device_properties2` for feature/property queries
  ([main support](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L534-L555),
  [stride support](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3569-L3600)).
- Robustness2 buffer descriptor and vertex-attribute cases require `robustBufferAccess2`; robustness2 image cases require
  `robustImageAccess2`; null-descriptor cases require `nullDescriptor`
  ([robustness2 checks](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L627-L665)).
- Image-robustness cases require `robustImageAccess`
  ([image robustness check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L649-L660)).
- Pipeline-robustness cases require `pipelineRobustness`
  ([main pipeline robustness check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L717-L719),
  [stride pipeline robustness check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3605-L3608)).
- `64b_indexing` cases require `shader64BitIndexing`
  ([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L721-L722)).
- 64-bit image/texel formats require `VK_EXT_shader_image_atomic_int64` and appropriate format features
  ([R64 checks](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L557-L612)).
- Scalar buffer-layout cases require `scalarBlockLayout`
  ([scalar block layout](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L614-L616)).
- Vertex and fragment shader-store paths require `vertexPipelineStoresAndAtomics` and `fragmentStoresAndAtomics`
  ([stage store checks](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L618-L622)).
- Ray-generation cases require `VK_KHR_ray_tracing_pipeline`
  ([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L624-L625)).
- Push descriptor cases require `VK_KHR_push_descriptor`
  ([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L706-L707)).
- `out_of_bounds_stride_dynamic_stride` requires `extendedDynamicState`
  ([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3597-L3611)).
- Cases using an exclusive compute queue require such a queue to be available
  ([support check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L725-L726)).

## Verification methods

The main generated tests write shader-side success or failure into an 8 by 8 storage image. The shader accumulates any
unexpected value into `accum` and writes `(1,0,0,1)` on success or `(0,0,0,0)` on failure
([shader result write](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1853-L1860)). Runtime code clears or
initializes input resources, executes one dispatch, trace-rays call, or draw, copies the output image to a host-visible
buffer, and checks every output pixel component for the expected success value
([execution](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3405-L3443),
[copy-back](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3450-L3465),
[result loop](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3467-L3494)).

The generated shader compares in-bounds accesses against deterministic reference data and accepts only the robustness
extension's observed out-of-bounds patterns: zero or component-default vectors for robustness2, and the relaxed zero-or-one
alpha form for image robustness
([expected data](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1415-L1471),
[OOB comparison](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1607-L1673),
[image-robustness alpha relaxation](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1614-L1619)).
For robustness2 sampled images, the shader also checks out-of-bounds mip levels
([mip-level check](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1678-L1688)). Null-descriptor image and
buffer cases check size/query operations such as `textureSize`, `textureQueryLevels`, `imageSize`, `imageSamples`, and
runtime array `length()` returning zero-like results
([null descriptor checks](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1733-L1832)).

The `misc.out_of_bounds_stride*` tests render one point per pixel through a vertex buffer whose last stride chunk is
partially beyond the buffer range, copy the color attachment to a buffer, and compare every pixel against the blue
reference color
([setup](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3654-L3696),
[draw and copy](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3766-L3804),
[image comparison](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3806-L3819)).

## Test principles observed in the file

- Use a custom device with only the relevant robustness extensions enabled so the test can verify extension behavior even
  when the default context device does not enable those features
  ([singleton setup](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L78-L180)).
- Share one generator across robustness2, image robustness, pipeline robustness, and 64-bit-indexing modes, then prune the
  matrix to avoid excessive duplication in pipeline and 64-bit-indexing modes
  ([shared generator](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3840-L4308)).
- Cover both descriptor update paths: ordinary bound descriptor sets and push descriptors, including descriptor update
  templates outside Vulkan SC
  ([descriptor update paths](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L2781-L2869)).
- Exercise multiple execution domains: compute, vertex, fragment, and non-VulkanSC ray-generation shader paths
  ([shader generation](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L1862-L1945),
  [execution](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3405-L3443)).
- For pipeline robustness, apply `VkPipelineRobustnessCreateInfoEXT` at the pipeline or shader-stage/library point that
  corresponds to the tested resource category
  ([pipeline robustness info](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L472-L516),
  [graphics placement](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L3204-L3349)).

## Notes / uncertainties

- The inspected source shows `push` as a possible direct child wherever `pushCases[]` is enabled, but the inspected
  mustpass file for `robustness.pipeline_robustness.robustness2` and
  `robustness.pipeline_robustness.image_robustness` only contains `bind` paths. The nested pipeline hierarchy trees
  therefore list only `bind` as evidenced by both source generation plus mustpass coverage observed for this subtask.
- The parameter tables summarize observed arrays and pruning rules rather than enumerating every generated leaf; the
  mustpass file contains tens of thousands of leaf paths for this file's roots.
- Vulkan SC behavior is noted only where the inspected file has explicit `CTS_USES_VULKANSC` guards. This page follows the
  requested non-VulkanSC pipeline-robustness scope and does not claim complete Vulkan SC coverage.
- Helper internals from [vktRobustnessUtil.cpp](../../../modules/vulkan/robustness/vktRobustnessUtil.cpp) were not needed
  for the documented registration roots and were not used for additional factual claims beyond the directly inspected
  include relationship in [vktRobustnessExtsTests.cpp](../../../modules/vulkan/robustness/vktRobustnessExtsTests.cpp#L37-L40).
