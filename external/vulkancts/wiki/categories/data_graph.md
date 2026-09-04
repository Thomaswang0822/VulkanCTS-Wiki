## Overview

The `data_graph` category covers creation, execution, pipeline-cache behavior, and property queries for Vulkan data graph pipelines backed by tensor resources.

## Background Knowledge

- **Data graph pipeline:** A data graph pipeline packages a graph description and executable operations. Its session and tensor resources provide the state needed for dispatch.
- **Provider-backed graph:** The CTS generates the observed graph cases through the TOSA provider. The provider supplies graph structure, resources, and reference results while Vulkan tests exercise the API boundary.
- **Pipeline cache and properties:** Cache tests check whether creation reuses or requires compilation. Property tests use the two-call query pattern in which one call determines a count and a later call retrieves data.

## Category Structure

```text
data_graph
├── basic
├── cache
└── properties
```

The dispatcher is documented on [DataGraph](../testfiles/data_graph/DataGraph.md). The three direct families each have a separate implementation-bearing page.

## How the Families Fit Together

- Read [Basic](../testfiles/data_graph/Basic.md) for graph-pipeline and session creation, dispatch, tensor resources, reference comparison, and pruning.
- Read [PipelineCache](../testfiles/data_graph/PipelineCache.md) for cache fill, hit, miss, and compile-required behavior.
- Read [Properties](../testfiles/data_graph/Properties.md) for available-property enumeration, property-data retrieval, complete and incomplete results, and failure meaning.
- The dispatcher page documents root registration and routing. Each child page owns its own execution and failure interpretation.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| Category dispatcher | [DataGraph](../testfiles/data_graph/DataGraph.md) | Root registration and routing to `basic`, `cache`, and `properties`. |
| `basic` | [Basic](../testfiles/data_graph/Basic.md) | Pipeline and session creation, graph dispatch, tensor resources, reference comparison, and pruning. |
| `cache` | [PipelineCache](../testfiles/data_graph/PipelineCache.md) | Cache creation, fill and hit behavior, compile-required results, and dispatch. |
| `properties` | [Properties](../testfiles/data_graph/Properties.md) | Available-property enumeration, property-data retrieval, complete and incomplete results, and failure meaning. |

## Category Notes

The dispatcher page uses `DataGraph`, while the cache family uses `PipelineCache`. These names omit the `vkt` prefix and trailing `Tests` suffix while preserving source responsibilities.
