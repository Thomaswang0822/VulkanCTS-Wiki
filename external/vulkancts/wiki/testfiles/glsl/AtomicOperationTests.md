## Overview

[`vktAtomicOperationTests.cpp`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1) implements `glsl.atomic_operations`, a generated GLSL 4.50 test group for atomic operations on storage-buffer data, workgroup-shared data, task payload, and buffer-reference storage. Each case generates a shader for one operation, data type, shader stage, and memory mode; executes it through the shader-executor framework; then validates the modified atomic value and returned values against host-side legal outcomes.

The factory creates an `atomic_operations` group and the Vulkan test package adds it directly below `glsl` ([factory](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1589-L1592), [package registration](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1278)). The group has a flat set of generated leaves, rather than operation or stage subgroups.

## Source Code

- Implementation and factory: [`vktAtomicOperationTests.cpp`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1)
- Public declaration: [`vktAtomicOperationTests.hpp`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.hpp#L23-L35)
- GLSL-package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1274-L1278)
- Generated-case registration: [`addAtomicOperationTests()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1468-L1585)

## Registration Hierarchy

```text
glsl.atomic_operations
```

Every direct child follows this grammar; the registration loop adds each permitted combination directly to `atomic_operations` ([name construction and insertion](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1537-L1580)). For example, `add_signed_compute_shared` denotes integer `atomicAdd` in a compute shader using workgroup-shared storage, and `exchange_float32_fragment_reference` denotes float exchange in a fragment shader using a buffer reference.

## Test Matrix

| Dimension | Registered values / constraints |
|---|---|
| Operation | `exchange`, `comp_swap`, `add`, `min`, `max`, `and`, `or`, and `xor` ([operation table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1524-L1535)). |
| Data type | `signed`, `unsigned`, `float32`, `signed64bit`, `unsigned64bit`, and `float64`; non-Vulkan-SC builds additionally register `float16`, `f16vec2`, and `f16vec4` ([type table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1498-L1522)). Generated GLSL names include `int`, `uint`, `float`, `int64_t`, `uint64_t`, and `double` ([mapping](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L225-L246)). |
| Shader stage | `vertex`, `fragment`, `geometry`, `tess_ctrl`, `tess_eval`, `compute`, `task`, and `mesh` ([stage table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1472-L1485)). |
| Memory suffix | No suffix is descriptor-backed buffer storage; `_shared` is workgroup storage; `_reference` is buffer-reference storage; `_payload` is task payload ([memory table](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1487-L1496)). |
| Shared-memory restriction | `_shared` leaves exist only for compute, task, and mesh stages ([filter](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1559-L1566)). |
| Payload restriction | `_payload` leaves exist only for task shaders; mesh-shader task payload is read-only ([filter](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1568-L1571)). |
| Floating-point operations | Floating-point types register `add` and `exchange`; non-Vulkan-SC builds also register `min` and `max`. Compare-swap and bitwise atomics are excluded ([filter](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1543-L1557)). |

The source intentionally does not form an unrestricted Cartesian product: the floating-point, shared-memory, and payload filters run before each child is created. In Vulkan SC, the 16-bit floating-point entries and floating-point min/max registration guarded by `#ifndef CTS_USES_VULKANSC` are absent.

## Operation Families

- **`exchange_*`** tests atomic exchange for every eligible integer and floating-point type. The oracle accepts either possible order of the two overlapping operations ([integer oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L596-L600)).
- **`comp_swap_*`** is integer-only. Its initializer arranges compare values so exactly one of the overlapping operations can match, alternating by element parity ([initialization](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L301-L319)); the reference constructs the matching parity-dependent outcomes ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L603-L615)).
- **`add_*`, `min_*`, and `max_*`** cover integer operations and their permitted floating-point variants. Integer min/max use the host `de::min()`/`de::max()` reference operations ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L550-L593)).
- **`and_*`, `or_*`, and `xor_*`** are integer-only and use exact bitwise host reference calculations ([oracle](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L557-L576)).

## Support / Feature Requirements

| Requirement | Scope |
|---|---|
| `VK_KHR_shader_atomic_int64` | Required for signed/unsigned 64-bit integer leaves. Buffer/reference modes require `shaderBufferInt64Atomics`; shared-like modes require `shaderSharedInt64Atomics` ([checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1058-L1077)). |
| `VK_EXT_shader_atomic_float2` | Required for scalar float16. Operation- and memory-class-specific Float16 add, min/max, or general-atomic feature bits are checked outside Vulkan SC ([checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1079-L1143)). |
| `VK_NV_shader_atomic_float16_vector` | Required for `f16vec2`/`f16vec4`, together with `shaderFloat16VectorAtomics`; these leaves are non-Vulkan-SC only ([checks](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1145-L1154)). |
| `VK_EXT_shader_atomic_float` | Required for float32 and float64 leaves. Add and exchange select the matching buffer/shared feature bits ([float32](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1156-L1221), [float64](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1223-L1288)). |
| Float min/max | float32/float64 min/max additionally require `VK_EXT_shader_atomic_float2` and the applicable buffer/shared min-max feature bit; these cases are not compiled for Vulkan SC ([float32](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1178-L1200), [float64](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1245-L1267)). |
| `VK_KHR_buffer_device_address` | Required only for `_reference` leaves ([check](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1290-L1293)). |
| Selected shader stage | Every concrete case calls the shared `checkSupportShader()` stage check after its data/memory checks ([call](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1295-L1296)). |

Missing per-case capabilities produce a not-supported result during support checking; they do not change the source-defined registration matrix. Mesh/task cases build with SPIR-V 1.4, while other stages use SPIR-V 1.0 ([build options](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1019-L1028)).

## Shader Generation and Execution

The generated `AtomicStruct` contains `N / 2` atomic `inoutValues`, `N` input, comparison, and output values, hit counters, and an index; `N` is 32 ([structure](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L220-L223), [shader template](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1306-L1317)). The shader declarations distinguish descriptor-backed buffers, `shared` storage, `taskPayloadSharedEXT`, and `buffer_reference`; reference mode receives the storage buffer device address through a uniform buffer ([declarations](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1320-L1357)).

Each participating invocation atomically reserves an output index and performs the selected GLSL atomic operation on `inoutValues[idx % (N / 2)]`. Fragment shaders exclude helper invocations; other non-vertex shaders use a hit counter to cap participation at `N`; vertex shaders use `gl_VertexIndex` ([generated bodies](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1375-L1413)). Shared-like modes copy data into shared/payload storage, synchronize around the atomics, and copy results back; their shader uses one workgroup with 32 local invocations ([copy and barriers](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1365-L1401), [local size](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1461-L1465)).

## Verification Methods

`iterate()` creates a typed test buffer, initializes deterministic random input with seed `0x62a15e34`, flushes it, executes the generated shader, invalidates the host mapping, and delegates pass/fail to `checkResults()` ([execution path](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L900-L1007)). Reference cases allocate the main storage buffer with shader-device-address usage and pass its device address through an auxiliary uniform buffer ([setup](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L907-L931)).

For each of the 16 `inout` elements, two invocations operate on the same location. The host oracle therefore builds two valid result triples—final atomic value plus the two returned pre-operation values—and accepts either serialization order ([model and comparison](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L524-L546), [result check](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L623-L642)). Integer results use exact byte comparisons ([`Expected::compare()`](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L327-L344)).

Floating-point verification uses a NaN-safe approximate comparator, with a `0.00001` generic tolerance and `0.01` for `deFloat16` ([comparison helpers](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L356-L378)). Its input generator includes signaling NaNs, quiet NaNs, and signed zeros, and min/max handling adds the legal exceptional-value outcomes before comparison ([data generation](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L412-L453), [min/max handling](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L646-L689)).

## Test Principles

- The group tests generated GLSL atomic semantics together with the selected pipeline stage, storage declaration, descriptor/device-address setup, synchronization, and host oracle; a failure is disagreement with that complete path, not isolated proof of one implementation layer.
- Operation names, type/stage/memory coverage, and exclusions are defined by the registration tables and loop guards, not by a hand-maintained leaf inventory.
- Extensions are emitted only for the selected data/memory variant: 64-bit integer atomics, floating-point atomics, optional NV float16 vectors, and buffer references ([extension generation](../../../modules/vulkan/shaderexecutor/vktAtomicOperationTests.cpp#L1415-L1440)).
- This page describes source-defined behavior and requirements; it does not claim that the cases were executed on the current host.
