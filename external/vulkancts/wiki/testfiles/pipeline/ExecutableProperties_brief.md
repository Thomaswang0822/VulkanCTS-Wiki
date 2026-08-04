# Understanding Brief: Pipeline executable properties

## The Question This Family Answers

The `executable_properties` test family asks whether an implementation can report internally compiled pipeline executables through `VK_KHR_pipeline_executable_properties` without returning malformed or cache-dependent metadata. The checks cover executable properties, optional statistics, and optional internal representations for graphics pipelines, plus compute pipelines in the monolithic construction path.

## Concepts You Need Before Reading the Test

A Vulkan pipeline can compile into one or more implementation-defined executables. The extension exposes three query entry points for an application to inspect those executables:

- `vkGetPipelineExecutablePropertiesKHR` returns the executable list and each executable's name, description, shader-stage mask, and subgroup size.
- `vkGetPipelineExecutableStatisticsKHR` returns named statistics for one executable when the pipeline was created with `VK_PIPELINE_CREATE_CAPTURE_STATISTICS_BIT_KHR`.
- `vkGetPipelineExecutableInternalRepresentationsKHR` returns named textual or binary representations when creation requested `VK_PIPELINE_CREATE_CAPTURE_INTERNAL_REPRESENTATIONS_BIT_KHR`.

The extension feature is `pipelineExecutableInfo` in `VkPhysicalDevicePipelineExecutablePropertiesFeaturesKHR`. The CTS requires the extension before constructing a test instance. See the [extension requirement metadata](../../../scripts/src/extensions/VK_KHR_pipeline_executable_properties.json#L1).

The returned content is implementation-defined, so the family does not prescribe a particular executable count, statistic value, or internal-representation payload. It instead checks structural validity and consistency between two equivalent pipeline builds: an initial build and a build using a pipeline cache.

## What the Test Varies

| Behavior parameter | Values | Why it matters |
|---|---|---|
| Pipeline family | `graphics`, `compute` | Exercises query results for graphics and compute compilation paths. |
| Shader-stage set | vertex plus fragment; vertex, geometry, and fragment; vertex, tessellation-control, tessellation-evaluation, and fragment; compute | Checks that every reported executable stage belongs to the stages supplied for the pipeline. |
| Optional query work | properties only; statistics; internal representations; both | Selects capture flags and the per-executable follow-up queries. |
| Pipeline construction | monolithic, fast linked library, pipeline library | Keeps graphics coverage across construction paths; compute is monolithic-only. |
| Pipeline-cache state | initial compilation, cached compilation | Supplies the equivalent-pipeline comparison. |

## How to Read a Result

The test first queries the executable count, then allocates and initializes returned structures before the second call fills them. It applies the same two-call pattern to statistics and internal representations. For the two pipeline builds, it compares executable identity information and the sets of statistic or internal-representation names. It logs statistic values even if they differ, because values may be non-deterministic across compilations.

For binary internal representations, the test fills the destination buffer with a sentinel pattern before the data call. A long surviving sentinel run indicates that the driver did not write the claimed payload. For textual representations, the test requires a non-empty NUL-terminated string.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | The test observed | Likely fault area |
|---|---|---|
| Any properties-only case | An invalid name or description, duplicate executable name, stage outside the supplied shader set, or disagreement between equivalent builds | Pipeline executable property query implementation or pipeline-cache compilation path |
| A statistics case | Invalid or duplicate statistic metadata, invalid Boolean format value, or a changed statistic set or metadata between equivalent builds | Statistics capture or `vkGetPipelineExecutableStatisticsKHR` implementation |
| An internal-representations case | Invalid or duplicate representation metadata, missing payload, malformed text, or a binary payload buffer left unwritten | Internal-representation capture or `vkGetPipelineExecutableInternalRepresentationsKHR` implementation |
| Graphics stage-specific case | A property reports a stage absent from the supplied graphics stage set | Stage attribution during graphics executable reporting |
| Monolithic compute case | The compute executable metadata differs between initial and cached builds | Compute executable reporting or cache interaction |

### Limits of the Result

A passing case does not require a driver to expose a fixed number of executables, statistics, or internal representations. A failing set-comparison case identifies an inconsistency between two equivalent CTS pipeline builds, but the returned metadata cannot isolate the compiler, cache, or query layer without driver investigation.

## Source Trail

- [Legacy navigation page](vktPipelineExecutablePropertiesTests.md)
- [Implementation and query checks](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L272)
- [Family registration](../../../modules/vulkan/pipeline/vktPipelineExecutablePropertiesTests.cpp#L1213)
- [Extension feature requirement](../../../scripts/src/extensions/VK_KHR_pipeline_executable_properties.json#L1)
- Mustpass lists: `pipeline/monolithic/monolithic.txt`, `pipeline/fast-linked-library.txt`, and `pipeline/pipeline-library.txt`
