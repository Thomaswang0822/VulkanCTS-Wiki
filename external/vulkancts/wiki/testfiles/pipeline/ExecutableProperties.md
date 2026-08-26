## Overview

**Core question:** Does `VK_KHR_pipeline_executable_properties` return well-formed and cache-consistent executable metadata for graphics and monolithic compute pipelines?

[`vktPipelineExecutablePropertiesTests.cpp`](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1) builds equivalent pipelines twice, first with an empty pipeline cache and then with the same, potentially populated cache. It queries both pipelines' executable properties and, when selected by the test case, their statistics. Internal representations are queried only for the second pipeline. The implementation-defined payload does not need to match a CTS reference value. The test instead checks returned structures and strings, compares property and statistic metadata between the two builds, and checks the second pipeline's internal-representation metadata and text payloads.

The family requires `VK_KHR_pipeline_executable_properties` and the `pipelineExecutableInfo` feature described in the [extension requirement metadata](../../../scripts/src/extensions/VK_KHR_pipeline_executable_properties.json#L1). Geometry and tessellation graphics cases also require their corresponding core device features. The source excludes Vulkan SC through `CTS_USES_VULKANSC` guards.

## Background Knowledge

For the shared concept pipeline construction type, see [Background Knowledge](../../categories/pipeline.md#background-knowledge) of the `pipeline` page.

A pipeline executable is an implementation-defined compiled unit associated with a Vulkan pipeline. The extension offers property, statistic, and internal-representation queries. Applications request optional capture with `VK_PIPELINE_CREATE_CAPTURE_STATISTICS_BIT_KHR` and `VK_PIPELINE_CREATE_CAPTURE_INTERNAL_REPRESENTATIONS_BIT_KHR` when creating the pipeline.

The reported data can differ across vendors and can include values that vary across compilations. Therefore, this family treats the initial and cached builds as equivalent structural observations for executable properties and statistics. It requires the same executable names, descriptions, stage masks, subgroup sizes, and statistic identities, while logging different statistic values as non-deterministic rather than failing them. Internal representations are not compared across builds because only the second pipeline requests their capture and is queried for them.

## Registration Hierarchy

```text
pipeline.monolithic.executable_properties
├── graphics
└── compute
```

The test family registers `graphics` for each supported pipeline construction type. It registers `compute` only for `PIPELINE_CONSTRUCTION_TYPE_MONOLITHIC` in [the registration function](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1213). Mustpass coverage contains 16 monolithic leaves, 12 fast-linked-library leaves, and 12 pipeline-library leaves. The 40 total leaves consist of four query selections for each stage-set combination: three graphics sets in each construction type, plus one compute set for monolithic pipelines.

## Parameter Dimensions and Observed Values

| Parameter | Registered or source values | Effect on the observation |
|---|---|---|
| Intermediate node | `graphics`, `compute` | Selects the pipeline builder and supplied shader-stage set. |
| Graphics shader-stage set | vertex plus fragment; vertex, geometry, and fragment; vertex, tessellation-control, tessellation-evaluation, and fragment | Determines which stage bits may appear in returned executable properties. |
| Compute shader-stage set | compute | Exercises the compute builder in monolithic pipelines. |
| Statistics selection | absent, present | Enables `VK_PIPELINE_CREATE_CAPTURE_STATISTICS_BIT_KHR` and requests per-executable statistics. |
| Internal-representation selection | absent, present | Enables `VK_PIPELINE_CREATE_CAPTURE_INTERNAL_REPRESENTATIONS_BIT_KHR` for the cached pipeline and requests representations. |
| Pipeline construction | monolithic, fast linked library, pipeline library | Selects a graphics construction path. Compute is not repeated for library paths. |
| Compilation state | initial, cached | Provides two equivalent pipelines for consistency checks. |

## Behavior Parameters

The primary behavioral axis is the direct intermediate node because `graphics` and `compute` select distinct pipeline construction code and shader inputs. The leaf suffix adds shader-stage and query selections.

### graphics: graphics-pipeline executable metadata

The graphics cases create two graphics pipelines with the selected stage set. The second wrapper receives a pipeline cache and, when selected, the internal-representation capture flag. Geometry cases require `geometryShader`; tessellation cases require `tessellationShader`. Each stage set runs properties-only, statistics, internal-representations, and combined query leaves.

### compute: monolithic compute-pipeline executable metadata

The compute cases create two compute pipelines with the compute stage. The registration function deliberately limits this intermediate node to the monolithic construction type. The four leaves use the same query-selection product as graphics.

## Shader Analysis

The shaders provide valid graphics or compute pipelines so the implementation can expose executable metadata. The test does not submit commands, render, dispatch, or compare shader-produced data. Shader execution behavior is outside the assertion boundary; the tested behavior starts after pipeline construction at the executable query calls.

## Runtime Execution and Result Checking

1. Each test instance creates a pipeline cache and builds two equivalent pipelines. The initial pipeline uses the cache object without cached content; the second build observes the resulting cache state. Statistics capture applies to both pipeline builds when requested. Internal-representation capture applies to the second build when requested, so the test can detect a cache-related capture failure.
2. `verifyTestResult()` queries each pipeline with `vkGetPipelineExecutablePropertiesKHR` first for a count and then for initialized `VkPipelineExecutablePropertiesKHR` structures. Each executable name and description must be non-empty and NUL-terminated. Names must be unique within a pipeline, and every reported stage bit must belong to the selected stage set.
3. The implementation compares the two property lists by executable name. They must have equal counts, matching descriptions, identical stage masks, and identical subgroup sizes. A zero executable count passes because the extension may expose no executables for that pipeline.
4. For leaves selecting statistics, `verifyStatistics()` uses the two-call count-and-data pattern with `vkGetPipelineExecutableStatisticsKHR` for each executable in both pipelines. It checks strings, uniqueness, Boolean values, and agreement of the statistic set, descriptions, and formats. It logs numeric or Boolean value differences as non-deterministic instead of failing them.
5. For leaves selecting internal representations, `verifyInternalRepresentations()` queries only the cached pipeline. It validates unique non-empty names and descriptions, and requires nonzero `dataSize`. Text data must be a non-empty NUL-terminated string. The current source initializes the sentinel sequence only when `isText` is true, but searches for that sequence only when `isText` is false. Consequently, the intended binary-buffer completeness check has no seeded sentinel to inspect and does not establish that the implementation wrote the whole binary payload.
6. The CTS logs properties, statistics, and representations, then returns the first detected failure or passes.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | The test observed | Likely fault area |
|---|---|---|
| Any properties-only case | An invalid name or description, duplicate executable name, stage outside the supplied shader set, or disagreement between equivalent builds | Pipeline executable property query implementation or pipeline-cache compilation path |
| A statistics case | Invalid or duplicate statistic metadata, invalid Boolean format value, or a changed statistic set or metadata between equivalent builds | Statistics capture or `vkGetPipelineExecutableStatisticsKHR` implementation |
| An internal-representations case | Invalid or duplicate representation metadata, zero `dataSize`, or malformed text; the current sentinel logic does not reliably detect an incompletely written binary payload | Internal-representation capture or `vkGetPipelineExecutableInternalRepresentationsKHR` implementation; binary write completeness is not localized by this test |
| Graphics stage-specific case | A property reports a stage absent from the supplied graphics stage set | Stage attribution during graphics executable reporting |
| Monolithic compute case | The compute executable metadata differs between initial and cached builds | Compute executable reporting or cache interaction |

### Cause Analysis

#### Malformed property metadata

**Possible failure symptoms:** The test reports an invalid executable name or description, a duplicate executable name, an unprovided stage, or different property metadata for the two pipelines.

**Possible implementation causes:** The property-query path may omit NUL termination, duplicate an executable identity, associate an executable with the wrong shader-stage mask, or derive different metadata from cache-backed compilation. The source-level comparison isolates the difference to equivalent CTS pipeline builds, but driver investigation is needed to identify the compiler or query component.

#### Inconsistent statistics metadata

**Possible failure symptoms:** The test reports invalid statistic strings, duplicate statistic names, a Boolean that is neither `VK_TRUE` nor `VK_FALSE`, or a mismatch in statistic count, identity, description, or format.

**Possible implementation causes:** The capture-statistics flag may not reach a compilation path, or the statistics query may serialize metadata inconsistently between initial and cached builds. The test does not fail on differing statistic values, so a failure points to metadata structure rather than permitted value variation.

#### Invalid internal-representation delivery

**Possible failure symptoms:** The test reports invalid representation text or metadata or zero-sized data. Although the source contains a binary destination-buffer sentinel check, its sentinel is initialized only for text representations, so that check does not provide reliable binary write-completeness evidence.

**Possible implementation causes:** The cached compilation path may fail to retain requested internal representations, the representation query may report an incorrect size, or the text-copy path may return malformed string data. The current CTS logic cannot reliably attribute a failure to partially unwritten binary data because the binary buffer is not seeded with the pattern that the later check searches for.

## Case Pruning

### Requirement-based pruning

The source guards out Vulkan SC.

### Design-based pruning

The implementation omits `compute` outside monolithic construction because the source comment says not to repeat compute tests for graphics pipeline library paths. The registered graphics coverage remains present in monolithic, fast-linked-library, and pipeline-library mustpass lists. Shader-object construction is excluded by the surrounding pipeline registration architecture.

## Key Takeaways

- The family validates implementation-provided executable-query contracts, not fixed compiler output.
- It compares an initial and cached compilation to test stable executable and metadata identity.
- Statistics values may differ without failure; their names, descriptions, and formats must remain consistent.
- Internal representations must report valid metadata, nonzero sizes, and valid text payloads. The current sentinel placement does not reliably verify complete writes of binary payloads.
- Graphics covers three stage sets across three construction paths; compute remains monolithic-only.

## Source Reference Appendix

- [Legacy navigation page](vktPipelineExecutablePropertiesTests.md)
- [Implementation file](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1)
- [Properties, statistics, and representation verification](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L297)
- [Graphics support and pipeline setup](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L857)
- [Family registration](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1213)
- [Extension feature requirement](../../../scripts/src/extensions/VK_KHR_pipeline_executable_properties.json#L1)
- Mustpass files: `external/vulkancts/mustpass/main/vk-default/pipeline/monolithic/monolithic.txt`, `external/vulkancts/mustpass/main/vk-default/pipeline/fast-linked-library.txt`, and `external/vulkancts/mustpass/main/vk-default/pipeline/pipeline-library.txt`
