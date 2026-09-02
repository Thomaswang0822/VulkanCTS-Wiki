## Overview

The `descriptor_indexing` test category checks non-uniform descriptor-array access, runtime descriptor arrays, update-after-bind, partially populated descriptors, and selected fixed-array and minimum-`NonUniform` shader forms.

## Background Knowledge

- **Descriptor array indexing.** A descriptor set can expose resources through an array binding, and shader code selects an element with a runtime index. A non-uniform index may select different descriptors for different invocations.
- **Runtime descriptor arrays.** A runtime array gets its usable length from descriptor-set layout and descriptor updates rather than from a fixed shader array length.
- **Update-after-bind.** With the corresponding binding flags and feature enabled, an application can update a descriptor set after binding it to a command buffer.

## Category Structure

```text
descriptor_indexing
```

The category has many direct generated test-case leaves rather than a small named family tree. The complete ownership boundaries are documented by the two rewritten Level-3 pages below.

## How the Families Fit Together

- The main page covers descriptor-type and suffix combinations, runtime-array and fixed-array forms, minimum-`NonUniform` cases, and `non_uniform_atomics`.
- The misc page covers four direct sampled-image-array compute cases.
- The dispatcher page is registration-only and is folded into this category gateway.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| Main descriptor-type matrix, suffix variants, runtime-array forms, minimum-`NonUniform`, and `non_uniform_atomics` | [DescriptorSetsIndexing.md](../testfiles/descriptor_indexing/DescriptorSetsIndexing.md) | Descriptor classes, shader generation, update timing, execution, and result checking |
| `misc_common_nonuniform_index_arraysize_*` cases | [Misc.md](../testfiles/descriptor_indexing/Misc.md) | Sampled-image arrays, compute dispatch, and CPU reference checking |

## Category Notes

The default Vulkan mustpass contains 114 executable leaves. The two rewritten Level-3 pages preserve separate ownership for the main implementation and the misc implementation.
