# Shader Object

This page summarizes the Vulkan CTS `shader_object` category, which documents tests around `VK_EXT_shader_object` API exposure, shader creation and linkage, dynamic rendering behavior, binding and pipeline interaction, binary handling, tessellation, performance thresholds, and a broad set of state-oriented and edge-case scenarios. The category is registered from [`vktShaderObjectTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) and is organized as ten root-level branches with branch-specific support checks and verification logic.

## Registration Entry Point

The category root is created by [`createTests()`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L47-L63) in [`vktShaderObjectTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L1). That function creates the category group from the caller-provided name and directly registers ten child branches via `addChild()` calls at [`vktShaderObjectTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L51-L60).

## Subgroup Structure

The root registration file directly registers these verified root-level groups:

```text
shader_object
+-- api
+-- create
+-- link
+-- tessellation
+-- binary
+-- pipeline_interaction
+-- binding
+-- performance
+-- rendering
+-- misc
```

The displayed group names above are verified from each implementation file's `TestCaseGroup` construction, not inferred only from factory symbol names. Root evidence is in [`vktShaderObjectTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTests.cpp#L51-L60), and the branch names are verified in the branch factory ranges referenced below.

## File Inventory

| File | Role | Verified group / purpose |
|---|---|---|
| [`vktShaderObjectTests.cpp`](../testfiles/shader_object/vktShaderObjectTests.md) | Root registration file | Category dispatcher for `shader_object` |
| [`vktShaderObjectApiTests.cpp`](../testfiles/shader_object/vktShaderObjectApiTests.md) | Implementation file | `api` |
| [`vktShaderObjectCreateTests.cpp`](../testfiles/shader_object/vktShaderObjectCreateTests.md) | Implementation file | `create` |
| [`vktShaderObjectLinkTests.cpp`](../testfiles/shader_object/vktShaderObjectLinkTests.md) | Implementation file | `link` |
| [`vktShaderObjectTessellationTests.cpp`](../testfiles/shader_object/vktShaderObjectTessellationTests.md) | Implementation file | `tessellation` |
| [`vktShaderObjectBinaryTests.cpp`](../testfiles/shader_object/vktShaderObjectBinaryTests.md) | Implementation file | `binary` |
| [`vktShaderObjectPipelineInteractionTests.cpp`](../testfiles/shader_object/vktShaderObjectPipelineInteractionTests.md) | Implementation file | `pipeline_interaction` |
| [`vktShaderObjectBindingTests.cpp`](../testfiles/shader_object/vktShaderObjectBindingTests.md) | Implementation file | `binding` |
| [`vktShaderObjectPerformanceTests.cpp`](../testfiles/shader_object/vktShaderObjectPerformanceTests.md) | Implementation file | `performance` |
| [`vktShaderObjectRenderingTests.cpp`](../testfiles/shader_object/vktShaderObjectRenderingTests.md) | Implementation file | `rendering` |
| [`vktShaderObjectMiscTests.cpp`](../testfiles/shader_object/vktShaderObjectMiscTests.md) | Implementation file | `misc` |
| [`vktShaderObjectCreateUtil.cpp`](../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L1) / [`vktShaderObjectCreateUtil.hpp`](../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1) | Utility-only files | Shared shader-object creation helpers; not a separately registered branch |

The source inventory in [`CMakeLists.txt`](../../modules/vulkan/shader_object/CMakeLists.txt#L6-L44) supports treating [`vktShaderObjectCreateUtil.cpp`](../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.cpp#L1) and [`vktShaderObjectCreateUtil.hpp`](../../modules/vulkan/shader_object/vktShaderObjectCreateUtil.hpp#L1) as utility-only files rather than separate Level-3 registration units.

## Cross-File Test Themes

### API exposure and basic capability validation

The [`api`](../testfiles/shader_object/vktShaderObjectApiTests.md) branch checks device-proc-address lookup, extension-version expectations, dynamic-rendering availability for older Vulkan versions, and nonzero `shaderBinaryUUID` behavior at [`vktShaderObjectApiTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L215-L315) and [`vktShaderObjectApiTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L354-L374). This branch establishes API-level preconditions that other branches assume.

### Shader lifecycle: creation, linkage, and binaries

Several branches focus on different stages of the shader-object lifecycle:
- [`create`](../testfiles/shader_object/vktShaderObjectCreateTests.md) registers multiple-object creation plus per-stage success/failure matrices at [`vktShaderObjectCreateTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L829-L878).
- [`link`](../testfiles/shader_object/vktShaderObjectLinkTests.md) varies linked versus unlinked stage combinations, bind modes, ordering, next-stage chains, and mesh/task combinations at [`vktShaderObjectLinkTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1351-L1650).
- [`binary`](../testfiles/shader_object/vktShaderObjectBinaryTests.md) covers shader-binary query, recreation, incompatible binary modes, and device-feature-bit variation at [`vktShaderObjectBinaryTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L838-L947).

### Dynamic rendering, binding, and interaction with pipelines

The category contains several execution-oriented branches:
- [`rendering`](../testfiles/shader_object/vktShaderObjectRenderingTests.md) stresses dynamic rendering across attachment-count, output-placement, bind-timing, format, and depth-output variations at [`vktShaderObjectRenderingTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1201-L1395).
- [`binding`](../testfiles/shader_object/vktShaderObjectBindingTests.md) covers swap cases, disabled-stage cases, draw/dispatch interleaving, mesh-stage swaps, binding lists, and final unbind families at [`vktShaderObjectBindingTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L2074-L2200).
- [`pipeline_interaction`](../testfiles/shader_object/vktShaderObjectPipelineInteractionTests.md) checks switching boundaries between shader objects and graphics or compute pipelines, including render-pass pipeline mixes and stage-binding subsets at [`vktShaderObjectPipelineInteractionTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1506-L1552).

### Specialized behavior families

Other branches isolate narrower behavior families:
- [`tessellation`](../testfiles/shader_object/vktShaderObjectTessellationTests.md) varies source language, tessellation mode, and rebinding behavior at [`vktShaderObjectTessellationTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L929-L975).
- [`performance`](../testfiles/shader_object/vktShaderObjectPerformanceTests.md) measures relative draw, dispatch, and binary-operation cost using explicit fail and quality-warning thresholds at [`vktShaderObjectPerformanceTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L790-L866), [`vktShaderObjectPerformanceTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1070-L1080), and [`vktShaderObjectPerformanceTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1210-L1225).
- [`misc`](../testfiles/shader_object/vktShaderObjectMiscTests.md) collects broad edge cases including state comparisons, unused-variable behavior, tessellation patch mismatch, and push constants at [`vktShaderObjectMiscTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3498-L4080).

## Cross-File Parameter Dimensions

Recurring parameter dimensions observed across the category include:

| Dimension | Observed recurring usage |
|---|---|
| Shader stage selection | Appears in [`create`](../testfiles/shader_object/vktShaderObjectCreateTests.md), [`link`](../testfiles/shader_object/vktShaderObjectLinkTests.md), [`binary`](../testfiles/shader_object/vktShaderObjectBinaryTests.md), [`binding`](../testfiles/shader_object/vktShaderObjectBindingTests.md), and [`misc`](../testfiles/shader_object/vktShaderObjectMiscTests.md) across classic graphics, compute, tessellation, geometry, task, and mesh stage variants |
| Linked vs. unlinked behavior | Central in [`link`](../testfiles/shader_object/vktShaderObjectLinkTests.md) and [`binary`](../testfiles/shader_object/vktShaderObjectBinaryTests.md), and also appears in [`misc`](../testfiles/shader_object/vktShaderObjectMiscTests.md) unused-variable cases |
| Ordering / rebinding / bind timing | Appears in [`link`](../testfiles/shader_object/vktShaderObjectLinkTests.md) (`default`, `random_order`, `separate_link`), [`tessellation`](../testfiles/shader_object/vktShaderObjectTessellationTests.md) (`_rebind` variants), [`binding`](../testfiles/shader_object/vktShaderObjectBindingTests.md), and [`rendering`](../testfiles/shader_object/vktShaderObjectRenderingTests.md) (`before` / `after` shader binding) |
| Source-language variant | [`tessellation`](../testfiles/shader_object/vktShaderObjectTessellationTests.md) distinguishes GLSL and HLSL registration paths at [`vktShaderObjectTessellationTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L933-L940) |
| Format and attachment configuration | Prominent in [`rendering`](../testfiles/shader_object/vktShaderObjectRenderingTests.md), including color-attachment count, output-array format, dummy render-pass mode, and optional depth use |
| Performance comparison mode | [`performance`](../testfiles/shader_object/vktShaderObjectPerformanceTests.md) compares shader objects against static pipelines, dynamic pipelines, linked shaders, binary shaders, compute pipelines, SPIR-V creation, and memcpy baselines |
| Pipeline mode vs. shader-object mode | [`misc`](../testfiles/shader_object/vktShaderObjectMiscTests.md) `state` subtree explicitly compares `shaders` and `pipeline` modes at [`vktShaderObjectMiscTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L3554-L3561) |

## Cross-File Support Requirements and Feature Gates

The category does not gate root registration on support, but branch implementations consistently use per-case support checks.

- `VK_EXT_shader_object` is the common baseline requirement across all inspected implementation branches, including [`api`](../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L192-L195), [`create`](../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L338-L341), [`link`](../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L742-L745), [`tessellation`](../../modules/vulkan/shader_object/vktShaderObjectTessellationTests.cpp#L415-L418), [`binary`](../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L421-L429), [`pipeline_interaction`](../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L954-L960), [`binding`](../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L677-L689), [`performance`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L894-L897), [`rendering`](../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1093-L1100), and [`misc`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L436-L439).
- Tessellation and geometry core features recur in multiple branches. Most branch checks require them only when selected parameters use those stages, including [`create`](../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L698-L702), [`binary`](../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L421-L429), [`pipeline_interaction`](../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L1324-L1333), and [`misc`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2569-L2574). The `link` branch's graphics-case check requires both tessellation and geometry support for the inspected graphics link cases due to the current `nextStages` expressions at [`vktShaderObjectLinkTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L746-L753).
- Mesh/task support recurs in branches that cover mesh or task shaders, including [`create`](../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L695-L706), [`link`](../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1323-L1328), and [`binding`](../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1293-L1301).
- Some branches add branch-specific support gates: optional extension/version checks in [`api`](../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L343-L350), attachment-limit and format support checks in [`rendering`](../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1101-L1110), and large state-feature matrices in [`misc`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L2026-L2180).

## Cross-File Verification Methods

Observed verification methods vary by branch, but several recurring patterns appear:

| Verification pattern | Evidence |
|---|---|
| Image or pixel comparison | Used in [`pipeline_interaction`](../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L740-L817), [`binding`](../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L600-L652), [`rendering`](../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1009-L1067), and [`misc`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L390-L410) |
| Buffer readback / side-effect checks | Used in [`pipeline_interaction`](../../modules/vulkan/shader_object/vktShaderObjectPipelineInteractionTests.cpp#L763-L777), [`binding`](../../modules/vulkan/shader_object/vktShaderObjectBindingTests.cpp#L1240-L1267), and [`misc`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1778-L2002) |
| Timing-threshold comparison | Used in [`performance`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L790-L866), [`vktShaderObjectPerformanceTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1070-L1080), and [`vktShaderObjectPerformanceTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectPerformanceTests.cpp#L1210-L1225) |
| API/property validation and fail-on-mismatch checks | Used in [`api`](../../modules/vulkan/shader_object/vktShaderObjectApiTests.cpp#L239-L313) |
| Reference-versus-generated binary behavior comparison | Used in [`create`](../../modules/vulkan/shader_object/vktShaderObjectCreateTests.cpp#L300-L312) and binary-focused cases in [`binary`](../../modules/vulkan/shader_object/vktShaderObjectBinaryTests.cpp#L458) |

## Level-3 Pages

- [`vktShaderObjectTests.cpp`](../testfiles/shader_object/vktShaderObjectTests.md)
- [`vktShaderObjectApiTests.cpp`](../testfiles/shader_object/vktShaderObjectApiTests.md)
- [`vktShaderObjectCreateTests.cpp`](../testfiles/shader_object/vktShaderObjectCreateTests.md)
- [`vktShaderObjectLinkTests.cpp`](../testfiles/shader_object/vktShaderObjectLinkTests.md)
- [`vktShaderObjectTessellationTests.cpp`](../testfiles/shader_object/vktShaderObjectTessellationTests.md)
- [`vktShaderObjectBinaryTests.cpp`](../testfiles/shader_object/vktShaderObjectBinaryTests.md)
- [`vktShaderObjectPipelineInteractionTests.cpp`](../testfiles/shader_object/vktShaderObjectPipelineInteractionTests.md)
- [`vktShaderObjectBindingTests.cpp`](../testfiles/shader_object/vktShaderObjectBindingTests.md)
- [`vktShaderObjectPerformanceTests.cpp`](../testfiles/shader_object/vktShaderObjectPerformanceTests.md)
- [`vktShaderObjectRenderingTests.cpp`](../testfiles/shader_object/vktShaderObjectRenderingTests.md)
- [`vktShaderObjectMiscTests.cpp`](../testfiles/shader_object/vktShaderObjectMiscTests.md)

## Notes / Uncertainties

- The `performance` branch is source-registered but intentionally excluded from mustpass by [`excluded-tests.txt`](../../mustpass/main/src/excluded-tests.txt#L67), so it is part of the documentation scope but not part of mustpass-backed registration-path verification output.
- Some large implementation files, especially [`vktShaderObjectLinkTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectLinkTests.cpp#L1), [`vktShaderObjectRenderingTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectRenderingTests.cpp#L1), and [`vktShaderObjectMiscTests.cpp`](../../modules/vulkan/shader_object/vktShaderObjectMiscTests.cpp#L1), were summarized at meaningful family granularity rather than expanded to every generated leaf case.
