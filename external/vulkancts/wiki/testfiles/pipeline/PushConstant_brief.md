# Pipeline push constants — brief

## What this test family answers

Does a pipeline read the intended push-constant bytes after range declaration, command updates, stage selection, layout changes, and repeated writes?

`push_constant` has three registered groups:

```text
pipeline.<construction>.push_constant
├── graphics_pipeline
├── compute_pipeline          (monolithic construction only)
└── lifetime
```

The default pipeline mustpass split contains five non-monolithic construction lists. Each list has 62 leaves: 53 `graphics_pipeline` leaves and 9 `lifetime` leaves. `compute_pipeline` is registered only for monolithic construction and is consequently absent from those five lists.

## Behavior groups

| Group | What varies | Result check |
|---|---|---|
| Graphics ranges | Disjoint or overlapping ranges; 4, 16, 128, 256, and device-maximum bytes; 1–5 graphics stages; partial, repeated, dynamic-index, and unused declarations | Integer render result against the reference renderer |
| Graphics overwrite | Four successive draws write separate storage-image pixels after several push updates | Each pixel equals `baseColor * multiplier + colorOffsets + transparentGreen` |
| Compute (monolithic) | Simple read, uninitialized read, and overwrite | Eight `Vec4(1,0,0,1)` outputs for simple; survival only for uninitialized; per-pixel overwrite check |
| Lifetime | Nine command sequences that bind layouts/pipelines and push compatible or overlapping ranges | Reference image and/or eight expected compute-buffer values |

`_command2` graphics leaves use `vkCmdPushConstants2KHR`; they require `VK_KHR_maintenance6` and are compiled out in Vulkan SC. Long-vector leaves additionally require `VK_EXT_shader_long_vector` support. Geometry and tessellation configurations require their corresponding core features. Range sizes exceeding `maxPushConstantsSize` are not supported.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| Disjoint size/count/update/dynamic-index graphics | Push command byte interval, `VkPushConstantRange` stage/offset/size, shader-stage generation, and reference-render comparison. |
| Overlap or unused graphics | Overlap handling and whether declarations not consumed by a shader incorrectly affect values used by another stage. |
| `_command2` only | `VK_KHR_maintenance6` enablement and `vkCmdPushConstants2KHR` command path. |
| Long-vector only | `VK_EXT_shader_long_vector` feature path and long-vector shader lowering. |
| Graphics or compute overwrite | Repeated command updates and the storage-image output calculation/readback. |
| Compute simple | Compute push range, dispatch, output-buffer write, and host invalidation. |
| Compute uninitialized | This is a no-crash/survival case; first check maintenance4 support and undefined-value handling rather than an expected value. |
| Lifetime | Push-constant layout compatibility, command ordering, and graphics/compute bind-point state. |
| Broad failures | Pipeline construction requirements, command submission, generated shader interface, synchronization, or host result readback. |

For registration, source navigation, exact support gates, and detailed execution behavior, see [PushConstant.md](PushConstant.md).
