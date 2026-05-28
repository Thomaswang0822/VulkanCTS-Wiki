# vktRayQueryNonUniformArgsTests

Non-uniform ray-query arguments. The registered hierarchy comes from `createNonUniformArgsTests()` in [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L375-L388).

## Source Files

| Role | Link |
|------|------|
| Implementation and registration | [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp) |

## Registration Hierarchy

```text
ray_query.non_uniform_args
├── no_miss
├── miss_cause_1
└── miss_cause_2
```

## Test Families

### no_miss — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### miss_cause_1 — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

### miss_cause_2 — Registered child

This direct child is listed in the registration hierarchy and is covered by the parameter evidence below.

## Parameter Dimensions

The file iterates `MissCause` values and registers `no_miss` plus numbered `miss_cause_*` leaves [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L375-L388).

## Support / Feature Requirements

The cases require acceleration-structure and ray-query functionality [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L104-L108).

## Verification Methods

The test reads one output value and expects `1` for no miss and `0` for miss causes [vktRayQueryNonUniformArgsTests.cpp](../../../modules/vulkan/ray_query/vktRayQueryNonUniformArgsTests.cpp#L355-L370).

## Test Principles

The file varies the registered dimensions while comparing shader-produced ray-query results against explicit CPU-side references or expected scalar/vector values.
