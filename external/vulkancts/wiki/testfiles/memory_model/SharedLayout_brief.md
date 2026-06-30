# vktMemoryModelSharedLayout Understanding Brief

This brief prepares the `memory_model.shared` wiki rewrite. It is intentionally more beginner-friendly than the final wiki page and focuses on the mental model that must be correct before writing formal documentation.

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation correctly stores, synchronizes, reads, and compares complex GLSL `shared` memory layouts inside a compute shader.

In the simplest form, the test asks:

> Can generated GLSL `shared` objects with scalar, vector, matrix, array, nested-struct, 8-bit, and 16-bit fields preserve the values written by the shader itself?

## Background Knowledge

### GLSL `shared` memory

GLSL `shared` variables are stored in workgroup shared memory. This means they are shared by invocations in the same compute workgroup, similar to a CUDA thread block's `__shared__` memory.

They are not shared across all GPU threads, across all workgroups, across queues, or across the whole device. Each workgroup has its own instance of the `shared` variables declared by the shader.

For this test, that distinction matters in two ways:

- The generated objects such as `shared S1 s1` are device-side workgroup shared-memory objects, not descriptor-bound buffers created by the host.
- The current test dispatches one workgroup with `vkCmdDispatch(1, 1, 1)` and uses `layout(local_size_x = 1)`, so it effectively runs one shader invocation. It tests shared-memory layout, addressing, read/write, and barrier behavior, but it does not meaningfully test data exchange between multiple invocations in the same workgroup.

So even though the memory class is called `shared`, the key focus here is not multi-thread communication. The key focus is whether complex GLSL `shared` memory layouts preserve values correctly when the shader writes and reads them.

## One Concrete Example

Forget the full random generator for a moment. Imagine the host generates this simplified shader fragment:

```glsl
struct S1 {
    int a;
    vec2 b;
    int c[2];
};
shared S1 s1;
```

If you know CUDA, this is conceptually similar to:

```cpp
__shared__ S1 s1;
```

The important point is that `s1` is not a host-created buffer. It is a GLSL `shared` object that lives in device workgroup shared memory while the compute shader executes.

Now imagine the generated test chooses these expected values:

| Field | Expected value |
|-------|----------------|
| `s1.a` | `3` |
| `s1.b.x` | `4.0` |
| `s1.b.y` | `-1.0` |
| `s1.c[0]` | `-2` |
| `s1.c[1]` | `5` |

The generated shader conceptually behaves like this:

```glsl
struct S1 {
    int a;
    vec2 b;
    int c[2];
};
shared S1 s1;
layout(std140, binding = 0) buffer block { highp uint passed; };

void main() {
    s1.a    = 3;
    s1.b    = vec2(4.0, -1.0);
    s1.c[0] = -2;
    s1.c[1] = 5;

    barrier();
    memoryBarrier();

    bool allOk = true;
    allOk = compare_int(3, s1.a) && allOk;
    allOk = compare_float(4.0, s1.b.x) && allOk;
    allOk = compare_float(-1.0, s1.b.y) && allOk;
    allOk = compare_int(-2, s1.c[0]) && allOk;
    allOk = compare_int(5, s1.c[1]) && allOk;

    if (allOk)
        passed++;
}
```

This is the mental model for the whole test. The real cases are randomly generated and may contain more complicated layouts, but the basic write-barrier-read-compare pattern stays the same.

## End-to-End Test Flow

The real test flow is time-ordered like this. Notice that this is a single-workgroup, single-invocation dispatch, so the barriers are part of the generated shared-memory access pattern but are not being used to coordinate multiple shader invocations in this pilot mental model.

```text
[host] choose a deterministic random seed for one case
[host] generate one to three GLSL shared-memory objects
[host] generate nested member types such as scalars, vectors, matrices, arrays, and structs
[host] flatten each generated object into leaf fields that can be checked individually
[host] generate small hard-coded expected values for those leaf fields
[host] generate a compute shader source string containing the shared objects, writes, barriers, compares, and result counter update
[host] create one 4-byte storage buffer for the `passed` counter
[host] bind that buffer at descriptor binding `0`
[host] create a compute pipeline from the generated shader
[host] dispatch one workgroup with `vkCmdDispatch(1, 1, 1)`
[device] execute assignments into GLSL `shared` memory
[device] execute `barrier()` and `memoryBarrier()`
[device] read the shared-memory fields back and compare them against expected values
[device] increment `passed` if every comparison succeeds
[host] wait for execution and read back the `passed` buffer
[host] require `passed == 1`
```

The host does not inspect every shared-memory field directly. The device reduces all field checks into one storage-buffer counter named `passed`, and the host only reads that final counter.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The main generated artifact is an inline GLSL compute shader source string.

For each random case, the host generates:

| Generated item | Example | Why it matters |
|----------------|---------|----------------|
| Struct declarations | `struct S1 { int a; vec2 b; int c[2]; };` | Defines the layout shape being tested. |
| Shared object declarations | `shared S1 s1;` | Places the generated data object in GLSL workgroup shared memory. |
| Hard-coded values | `3`, `7u`, `-2`, `4.0`, `true`, `vec2(4.0, -1.0)` | Provide known values that should survive shared-memory write/read. |
| Assignment statements | `s1.c[1] = 5;` | Writes expected values into shared memory on the device. |
| Compare helper functions | `compare_int`, `compare_float`, narrow-type helpers | Define equality checks, including promotion behavior for narrow types. |
| Compare statements | `allOk = compare_int(5, s1.c[1]) && allOk;` | Reads shared memory back and verifies each flattened leaf. |
| Optional extensions | 8-bit / 16-bit shader extensions | Enable special subfamilies when narrow types are used. |
| Compute pipeline | generated shader module + compute pipeline | Executes the generated shader for the case. |

The values are **hard-coded values written directly into the generated shader code string**. The host is not uploading an array of expected values to be copied into `shared` memory. Instead, it emits shader source text that contains assignments and comparisons using those values.

### Bound resources and memory objects

This test has a deliberately small real resource picture. Most of the interesting data is inside GLSL `shared` memory, not in host-created buffers or images.

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| GLSL `shared` objects such as `s1` | No host-side GPU resource is created for them | No descriptor binding | Written and read by the compute shader | No | This is the actual tested memory space and layout. |
| `passed` storage buffer | Yes | Yes, descriptor binding `0` | Device increments it when all checks pass | Yes | This is the only result channel the host reads. |
| Generated compute shader module/pipeline | Yes | Used as pipeline state | Device executes it | No | Contains the generated layout, writes, barriers, and compares. |
| Images, samplers, sampled images, storage images, attachments | No | No | No | No | They are not part of this test's resource model. |
| Uniform/constant buffers containing expected values | No | No | No | No | Expected values are embedded in shader code, not uploaded through a buffer. |

The most important beginner trap is this:

```text
[host] choose hard-coded values
[host] place them into a generated shader code string
[host] do NOT create/bind GPU shared-memory resources for `s1`
[device] execute assignments into GLSL shared memory
[device] read GLSL shared memory back
[host] read only the final `passed` counter buffer
```

Except for the result-checking buffer holding `passed`, the host does not create a real GPU-side resource corresponding to the generated shared-memory object.

## What Is Checked

The device checks that every generated shared-memory leaf field reads back the expected value after the shader writes the value and executes synchronization.

For the simple example, the conceptual flattened checklist is:

| Leaf path | Expected value |
|----------|----------------|
| `s1.a` | `3` |
| `s1.b.x` | `4.0` |
| `s1.b.y` | `-1.0` |
| `s1.c[0]` | `-2` |
| `s1.c[1]` | `5` |

The test cannot compare `s1` as one opaque block. It must compare final leaf values individually. In implementation terms, “flattening” converts a nested layout into a linear checklist of fields that can each receive generated write and compare code.

For arrays and structs, flattening behaves like this:

- a basic type becomes one check entry;
- an array of a basic type becomes one entry carrying the array size;
- an array of complex types recurses into each element;
- a struct recurses into each member.

For our example, flattening produces checks for:

```text
s1.a
s1.b.x
s1.b.y
s1.c[0]
s1.c[1]
```

The final host-side pass condition is:

```text
passed == 1
```

## What Failure Means

A failure means the generated shader did not observe the expected values after writing to GLSL `shared` memory and synchronizing.

Possible bug categories include:

- incorrect layout or offset calculation for GLSL `shared` structs;
- wrong addressing for arrays, nested arrays, or nested structs;
- incorrect vector or matrix component placement;
- incorrect handling of 8-bit or 16-bit fields;
- incorrect type promotion in generated comparison logic;
- incorrect shader compiler lowering for shared-memory accesses;
- broken workgroup shared-memory read/write behavior;
- missing or incorrect synchronization effect around `barrier()` / `memoryBarrier()`;
- incorrect result-buffer writeback if `passed` is not updated or observed correctly.

The test is therefore not just a compile test. It checks that layout generation, addressing, writing, synchronization, reading, comparison, and result readback all work together.

## Important Variations and Special Cases

### Test tree shape

The visible direct tree is:

```text
memory_model.shared
├── scalar_types
├── vector_types
├── basic_types
├── basic_arrays
├── arrays_of_arrays
├── nested_structs
├── nested_structs_arrays
├── 16bit
└── 8bit
```

The first 7 entries are the base layout families:

```text
scalar_types
vector_types
basic_types
basic_arrays
arrays_of_arrays
nested_structs
nested_structs_arrays
```

The `16bit` and `8bit` entries are real child groups, not just attributes on those base cases. Each subgroup repeats the same first 7 base families, but enables extra type candidates:

- `memory_model.shared` contains 7 base families;
- `memory_model.shared.16bit` contains those same 7 families again, with 16-bit candidates allowed;
- `memory_model.shared.8bit` contains those same 7 families again, with 8-bit candidates allowed.

Because each family gets 10 numbered random cases, the concrete count is:

| Area | Families | Cases per family | Total cases |
|------|----------|------------------|-------------|
| base `memory_model.shared` | 7 | 10 | 70 |
| `memory_model.shared.16bit` | 7 | 10 | 70 |
| `memory_model.shared.8bit` | 7 | 10 | 70 |
| Total | 21 | 10 | 210 |

| Pass | Parent group | Extra feature bit | Result |
|------|--------------|-------------------|--------|
| `i == 0` | `memory_model.shared` | none | first 7 base families |
| `i == 1` | `memory_model.shared.16bit` | `FEATURE_16BIT_TYPES` | same 7 families again with 16-bit candidates |
| `i == 2` | `memory_model.shared.8bit` | `FEATURE_8BIT_TYPES` | same 7 families again with 8-bit candidates |

### Layout family intent

Think of the families as increasing shape complexity:

| Family | Main idea |
|--------|-----------|
| `scalar_types` | simple scalar fields |
| `vector_types` | vector fields |
| `basic_types` | vectors and matrices |
| `basic_arrays` | arrays |
| `arrays_of_arrays` | nested arrays |
| `nested_structs` | nested structures |
| `nested_structs_arrays` | nested structures combined with arrays |
| `16bit/...` | same families with 16-bit types allowed |
| `8bit/...` | same families with 8-bit types allowed |

### 8-bit and 16-bit compare behavior

Narrow types need special compare behavior because the helper code promotes them before comparison. Examples include:

- `uint8_t -> uint`
- `int8_t -> int`
- `uint16_t -> uint`
- `int16_t -> int`
- `float16_t -> float`

So generated compare code can conceptually look like:

```glsl
allOk = compare_uint(uint(7u), uint(someUint8Field)) && allOk;
```

These subfamilies test not only shared-memory layout, but also correct readback and comparison behavior for narrow fields.

### Support checks

The relevant support rules are:

- if 8-bit or 16-bit types are enabled, require `VK_KHR_shader_float16_int8`;
- if 16-bit types are enabled, require Vulkan 1.2 `shaderFloat16`;
- if 8-bit types are enabled, require Vulkan 1.2 `shaderInt8`.

The base shared-layout families do not show an explicit Vulkan memory-model feature gate in the inspected shared-layout support function.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `shared` group attached under `memory_model` | [`vktMemoryModelMessagePassing.cpp`](../../../modules/vulkan/memory_model/vktMemoryModelMessagePassing.cpp#L2410-L2413) | Shows that `shared` is delegated from the memory-model root file. |
| Shared-layout group creation | [`createSharedMemoryLayoutTests()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L287-L330) | Builds base, `16bit`, and `8bit` shared-layout groups. |
| Random case group size and seeds | [`createRandomCaseGroup()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L94-L105) | Creates the numbered random cases for each family. |
| Random case construction | [`RandomSharedLayoutCase::RandomSharedLayoutCase()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L108-L124) | Initializes deterministic generation for one case. |
| Random shared object generation | [`generateSharedMemoryObject()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L134-L160) | Creates `S1` / `s1`-style objects and members. |
| Random recursive type generation | [`generateType()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayout.cpp#L162-L285) | Chooses basic types, arrays, and nested structs. |
| Shared-layout data structures | [`vktMemoryModelSharedLayoutCase.hpp`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.hpp#L43-L181) | Defines generated shared objects, entries, structures, and shader interface data. |
| Layout flattening | [`computeReferenceLayout()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L55-L88) | Converts nested layouts into checkable entries. |
| Hard-coded value generation | [`generateValue()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L90-L139) | Produces the values embedded into generated shader code. |
| Assignment and compare emission | [`generateSharedMemoryWrites()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L197-L269) | Emits shared-memory writes and generated compare code. |
| Compute shader assembly | [`generateComputeShader()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L271-L345) | Wraps declarations, helpers, shared objects, barriers, compares, and `passed++`. |
| Support checks | [`SharedLayoutCase::checkSupport()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L347-L358) | Gates 8-bit and 16-bit cases. |
| Runtime execution and readback | [`SharedLayoutCaseInstance::iterate()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L360-L489) | Creates the result buffer, dispatches, waits, and checks `passed == 1`. |
| Deferred shader-interface setup | [`SharedLayoutCase::delayedInit()`](../../../modules/vulkan/memory_model/vktMemoryModelSharedLayoutCase.cpp#L502-L519) | Computes flattened layout and stores generated values before shader generation. |
| Compare helper generation and promotion | [`vktTypeComparisonUtil.cpp`](../../../modules/vulkan/util/vktTypeComparisonUtil.cpp#L34-L248) | Generates comparison helpers and narrow-type promotion rules. |

## Questions / Risk Points for User Audit

Use these questions to check whether the mental model is ready for the final wiki rewrite:

- Is it clear that GLSL `shared` objects such as `s1` are not host-created or descriptor-bound resources?
- Is it clear that the host embeds expected values into the generated shader source string instead of uploading them through a buffer?
- Is the role of the real `passed` storage buffer clear?
- Is the flattening idea clear enough to explain nested structs and arrays?
- Is the end-to-end timeline clear without splitting the explanation into disconnected host-only and device-only sections?
- Are the `16bit` and `8bit` groups understandable as repeated layout families with extra type support?
- Should the final wiki page keep the concrete `S1` example, or should it use a more source-faithful generated example?

## Conversion Notes for Final Wiki Rewrite

For the final [`SharedLayout.md`](SharedLayout.md) rewrite:

- Keep the explanation-first mental model: generated shared objects, hard-coded values, flattening, shader-side compare, host-side `passed` readback.
- Preserve a compact concrete example, but shorten beginner analogies such as the CUDA comparison.
- Move detailed source navigation into a source-reference appendix.
- Keep a resource table or short resource paragraph because the distinction between GLSL `shared` memory and the real `passed` storage buffer is central.
- Explain `16bit` and `8bit` as important variations, not as a separate core mechanism.
- Avoid presenting this as a generic Vulkan memory-model synchronization test; its practical focus is shared-memory layout correctness plus shader-side read/write/compare behavior.
