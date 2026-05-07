# [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1)

## Overview

[`vktShaderObjectPerformanceTests.cpp`](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1) implements the `shader_object/performance` branch. The branch registers timed draw, dispatch, and binary-operation cases under `performance` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1262-L1310). Draw cases compare shader-object timing against static pipelines, dynamic pipelines, linked shaders, binary shaders, or binary binding with explicit fail and warning thresholds at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L790-L866). Dispatch and binary creation cases compare shader-object dispatch or binary creation timing against compute pipeline, SPIR-V shader creation, or memory copy baselines at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1070-L1080) and [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1210-L1225).

## Role of File

Implementation-heavy test file for the root-level `performance` branch.

## Source Code

- Primary source: [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1)
- Parent registration: [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L58)
- Shared utility include: [vktShaderObjectCreateUtil.hpp](../../../../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1)

## Related Inspected Files

- [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63)
- [CMakeLists.txt](../../../../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44)

## Registration Path

```text
shader_object
+-- performance
    +-- {draw,draw_indexed,draw_indexed_indirect,draw_indexed_indirect_count,draw_indirect,draw_indirect_count}_{static_pipeline,dynamic_pipeline,linked_shaders,binary_shaders}
    +-- binary_bind_shaders
    +-- dispatch
    +-- dispatch_base
    +-- dispatch_indirect
    +-- binary_shader_create
    +-- binary_memcpy
```

Verifier-oriented explicit path examples (dot syntax expected by `verify_registration_paths.py`):

```text
```

Mustpass coverage note: the entire performance branch is explicitly excluded from mustpass by [`excluded-tests.txt`](../../../../../mustpass/main/src/excluded-tests.txt) (glob `dEQP-VK.shader_object.performance.*`). No [`performance.txt`](../../mustpass/main/vk-default/shader-object/performance.txt) exists under [`shader-object/`](../../mustpass/main/vk-default/shader-object), while sibling branch files such as [`api.txt`](../../mustpass/main/vk-default/shader-object/api.txt), [`binding.txt`](../../mustpass/main/vk-default/shader-object/binding.txt), [`pipeline-interaction.txt`](../../mustpass/main/vk-default/shader-object/pipeline-interaction.txt), and [`rendering.txt`](../../mustpass/main/vk-default/shader-object/rendering.txt) do exist. The branch is source-registered but intentionally excluded from conformance runs.

The displayed branch name is verified from `TestCaseGroup(testCtx, "performance")` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1262-L1264). The root file registers this branch directly at [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L58).

## Test Hierarchy

```text
performance
+-- draw command form x draw comparison mode
+-- binary_bind_shaders
+-- dispatch variants
+-- binary-operation variants
```

## Test Families

### Timed draw cases

`drawTypeTests[]` registers six draw command forms at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1266-L1277), and `typeTests[]` registers four comparison modes: `static_pipeline`, `dynamic_pipeline`, `linked_shaders`, and `binary_shaders` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1279-L1288). Their cross product is registered at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1290-L1298), with `binary_bind_shaders` added separately at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1299).

### Timed dispatch cases

`dispatch`, `dispatch_base`, and `dispatch_indirect` are registered using `ShaderObjectDispatchPerformanceCase` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1301-L1304). The dispatch enum is defined at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L72-L77).

### Binary operation cases

`binary_shader_create` and `binary_memcpy` are registered using `ShaderObjectBinaryPerformanceCase` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1306-L1308). The binary enum is defined at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L56-L60).

## Parameter Dimensions

| Dimension | Observed values / evidence |
|---|---|
| Draw command form | `DRAW`, `DRAW_INDEXED`, `DRAW_INDEXED_INDIRECT`, `DRAW_INDEXED_INDIRECT_COUNT`, `DRAW_INDIRECT`, `DRAW_INDIRECT_COUNT` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L62-L70) |
| Draw comparison mode | `DRAW_STATIC_PIPELINE`, `DRAW_DYNAMIC_PIPELINE`, `DRAW_LINKED_SHADERS`, `DRAW_BINARY`, `DRAW_BINARY_BIND` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L47-L54) |
| Dispatch mode | `DISPATCH`, `DISPATCH_BASE`, `DISPATCH_INDIRECT` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L72-L77) |
| Binary operation | `BINARY_SHADER_CREATE`, `BINARY_MEMCPY` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L56-L60) |

## Support / Feature Requirements

- Draw performance cases require `VK_EXT_shader_object` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L894-L897).
- Dispatch performance cases require `VK_EXT_shader_object` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1106-L1109).
- Binary performance cases require `VK_EXT_shader_object` at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1250-L1253).
- Registration itself is unconditional once the root adds the branch factory at [vktShaderObjectTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L58).

## Verification Methods

- Timed draw cases accumulate total and maximum per-iteration timings, then compare shader-object timing with reference timings. Static-pipeline mode fails if maximum shader-object time is more than 50% slower and reports quality warnings above 25%; dynamic-pipeline mode fails above 20% maximum-time slowdown and warns above 10%; linked, binary, and binary-bind modes use 5% symmetric or maximum-time thresholds at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L790-L866).
- Dispatch cases compare shader-object dispatch time against compute pipeline dispatch time and fail when shader-object dispatch is more than 5% slower at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1070-L1080).
- Binary creation cases run 100 iterations and compare binary shader creation either against SPIR-V shader creation with a 5% threshold or against copying an equal amount of data with a 50% threshold at [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1132-L1150) and [vktShaderObjectPerformanceTests.cpp](../../../../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1210-L1225).

## Test Principles Observed

- Use relative timing thresholds rather than exact absolute performance numbers.
- Separate draw, dispatch, and binary-operation performance comparisons.
- Return `QP_TEST_RESULT_QUALITY_WARNING` for selected draw slowdowns below hard-fail thresholds.

## Notes / Uncertainties

- Performance results can vary by implementation; this page documents the code's explicit CTS thresholds rather than claiming expected real-world performance ordering.
