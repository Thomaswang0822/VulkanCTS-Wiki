# Dynamic Offset Tests

Checks dynamic descriptor offset behavior, including Amber shader-reuse tests and push-constant-driven two-pipeline scenarios.

## Source

- [`vktBindingDynamicOffsetTests.cpp`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp)

## Registration Hierarchy

```text
binding_model.dynamic_offset
├── shader_reuse_differing_layout_compute
├── shader_reuse_differing_layout_graphics
├── two_pipelines
├── two_pipelines_different_sets
├── two_pipelines_pc_first
├── two_pipelines_pc_first_different_sets
├── two_pipelines_pc_first_single_layout
├── two_pipelines_separate_offsets
├── two_pipelines_separate_offsets_different_sets
├── two_pipelines_separate_offsets_pc_first
├── two_pipelines_separate_offsets_pc_first_different_sets
├── two_pipelines_separate_offsets_pc_first_single_layout
├── two_pipelines_separate_offsets_single_layout
└── two_pipelines_single_layout
```

## Test Families

### shader_reuse_differing_layout_compute — Amber compute shader-reuse test

Amber test verifying dynamic offset behavior when a compute shader is reused with a differing descriptor layout. Registered at [`vktBindingDynamicOffsetTests.cpp:392`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L392). Amber source: `binding_model/dynamic_offset/shader_reuse_differing_layout_compute.amber`.

### shader_reuse_differing_layout_graphics — Amber graphics shader-reuse test

Amber test verifying dynamic offset behavior when a graphics shader is reused with a differing descriptor layout. Registered at [`vktBindingDynamicOffsetTests.cpp:395`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L395). Amber source: `binding_model/dynamic_offset/shader_reuse_differing_layout_graphics.amber`.

### two_pipelines — Two-pipeline push-constant dynamic-offset matrix

Generated family of 12 test cases exercising two-pipeline scenarios with push-constant-driven dynamic offsets. Each variant is constructed from a 4-dimensional boolean parameter matrix, with the combination `singleLayout=true && differentSets=true` excluded as invalid. Evidence starts at [`vktBindingDynamicOffsetTests.cpp:399`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L399) and continues through [`vktBindingDynamicOffsetTests.cpp:418`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L418).

**Parameter dimensions:**

| Dimension | Values | Effect on test name |
|-----------|--------|-------------------|
| `separateOffsets` | `false`, `true` | Appends `_separate_offsets` when `true` |
| `pcFirst` | `false`, `true` | Appends `_pc_first` when `true` |
| `singleLayout` | `false`, `true` | Appends `_single_layout` when `true` |
| `differentSets` | `false`, `true` | Appends `_different_sets` when `true` |

**Generated test names and parameter combinations:**

| Test name | separateOffsets | pcFirst | singleLayout | differentSets |
|-----------|:-:|:-:|:-:|:-:|
| `two_pipelines` | F | F | F | F |
| `two_pipelines_different_sets` | F | F | F | T |
| `two_pipelines_single_layout` | F | F | T | F |
| `two_pipelines_pc_first` | F | T | F | F |
| `two_pipelines_pc_first_different_sets` | F | T | F | T |
| `two_pipelines_pc_first_single_layout` | F | T | T | F |
| `two_pipelines_separate_offsets` | T | F | F | F |
| `two_pipelines_separate_offsets_different_sets` | T | F | F | T |
| `two_pipelines_separate_offsets_single_layout` | T | F | T | F |
| `two_pipelines_separate_offsets_pc_first` | T | T | F | F |
| `two_pipelines_separate_offsets_pc_first_different_sets` | T | T | F | T |
| `two_pipelines_separate_offsets_pc_first_single_layout` | T | T | T | F |

The 4 combinations where `singleLayout=true && differentSets=true` are skipped (see [`vktBindingDynamicOffsetTests.cpp:405`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L405)).

## Parameter Dimensions

| Dimension | Observed values / source |
|-----------|--------------------------|
| Group construction | Verified by [`vktBindingDynamicOffsetTests.cpp:425`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L425) |
| Generated families | Derived from arrays, loops, or child additions near [`vktBindingDynamicOffsetTests.cpp:392`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L392) |
| Build availability | VK only; not guarded by `CTS_USES_VULKANSC` at the group level |

## Support / Feature Requirements

The `DynamicOffsetPCCase::checkSupport` override at [`vktBindingDynamicOffsetTests.cpp:86`](../../../modules/vulkan/binding_model/vktBindingDynamicOffsetTests.cpp#L86) is a no-op (`DE_UNREF(context)`). No explicit feature or extension gates are enforced at the test-case level for the generated two-pipeline family. Amber tests may carry their own requirements in the Amber source files.

## Verification Methods

Cases validate that dynamic offsets select the intended buffer regions across pipeline reuse patterns. The `DynamicOffsetPCInstance::iterate` method executes the two-pipeline scenario and compares output buffer contents against expected values.

## Test Principles

- Keep descriptor binding/update behavior observable through shader execution or explicit API success checks.
- Vary one or more binding-model dimensions while preserving traceable generated names.
- Use feature/support gates to skip extension-dependent scenarios rather than broadening unsupported coverage.

## Notes

- This Level-3 page documents a registered test file. Helper-only files are not given separate pages.
