# Understanding Brief: SSBO layout and unsized-array tests

## One-Sentence Test Purpose

This test family checks whether Vulkan implementations agree with the CTS reference layout and runtime-array rules when compute shaders read and write shader storage buffer objects through many block, type, and descriptor configurations.

## Background Knowledge

### Storage-buffer layout is part of the shader interface

A storage buffer declaration gives the shader a structured view of bytes in a `VkBuffer`. The layout qualifier and member types determine offsets, array strides, matrix strides, and total storage size. `std140`, `std430`, scalar layout, relaxed layout, row-major matrices, and column-major matrices do not describe different buffers; they describe different valid mappings from the same structured values to bytes. Vulkan records these rules in SPIR-V decorations such as `Block`, `Offset`, `ArrayStride`, and `MatrixStride` ([Shader Interfaces](../../../vulkan-docs/src/chapters/interfaces.adoc#interfaces-resources)).

Why it matters here:
- The CTS computes a reference layout from the generated type tree, then uses that layout for initial values, expected writes, and buffer bindings.
- A mismatch in padding or stride changes which bytes the generated compute shader reads or writes.

### A runtime array length comes from the bound descriptor range

A shader runtime array has no fixed final element count in its declaration. `xs.length()` derives the count from the storage-buffer range visible through the descriptor, after any descriptor offset and range rules are applied. The test therefore varies the buffer size, descriptor offset, explicit range, `VK_WHOLE_SIZE`, variable-pointer mode, and, outside Vulkan SC, 64-bit indexing.

## One Concrete Example

The `dEQP-VK.ssbo.unsized_array_length.float_offset_whole_size` case uses two compute-stage storage-buffer bindings:

```glsl
layout(set=0, binding=0, std430) readonly buffer x { int xs[]; };
layout(set=0, binding=1, std430) writeonly buffer y { int observed_size; };
layout(local_size_x=1) in;
void main (void) { observed_size = xs.length(); }
```

The host binds the input buffer with an offset when the case requests it and writes the observed length to the second buffer. After one dispatch, the host computes `(bound length - offset) / element size` and compares that value with the shader result.

## End-to-End Test Flow

```text
[host] choose a generated layout case or an unsized-array subcase
[host] compute the reference layout and deterministic initial/write values
[host] create host-visible storage buffers and descriptor bindings
[host] generate and compile the compute shader
[host] upload initial data, bind the compute pipeline and descriptors
[host] dispatch one workgroup
[device] compare readable fields, increment the pass counter if they match, and write selected fields
[host] execute a shader-write to host-read barrier and wait for completion
[host] invalidate mapped memory and compare the pass counter and buffer bytes with reference data
[host] return pass or a specific comparison failure
```

The unsized-array-length subcases use the same timeline but compare one shader-written length value instead of a generated layout write set.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `SSBOLayoutCase::delayedInit()` computes the reference layout, creates deterministic initial and expected-write data, preserves data for fields the shader must not write, and calls `generateComputeShader()`.
- The generated layout shader declares the pass counter at binding 0 and generated blocks at later bindings. It compares initial values before writing expected values. The `phys` variant also emits a push-constant block carrying buffer addresses.
- `createUnsizedArrayLengthProgs()` emits a small GLSL compute shader. It selects `length()` or `length64()` and SPIR-V 1.0 or 1.3 according to the subcase.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Pass-counter storage buffer | yes | binding 0 | shader writes | yes | Records whether shader-side comparisons passed |
| Generated SSBO storage buffers | yes | bindings 1 onward | shader reads and writes | yes | Carries the layout-sensitive data |
| Unsized-array input buffer | yes | binding 0 | shader reads | no, contents are irrelevant | Its descriptor range defines the runtime array length |
| Unsized-array result buffer | yes | binding 1 | shader writes | yes | Carries `xs.length()` or `xs.length64()` |
| Push-constant address block in `phys` | yes, as pipeline state | push constants | shader reads | no | Transports `VkDeviceAddress` values for physical storage-buffer references |

The generated GLSL structs and arrays are descriptions in shader code. They become accesses to host-created buffers only through storage-buffer descriptors or physical buffer references.

## What Is Checked

For layout cases, the host requires both of these results:

- the shader pass counter equals one, which means its generated comparisons succeeded;
- the device-written buffer contents equal the reference write data, including preservation of fields marked unread or unwritten.

For `unsized_array_length`, the host requires the observed value to equal the descriptor-visible byte length divided by the element size. A mismatch fails the test; an allocation failure for the deliberate 64-bit stress size is reported as unsupported rather than as a layout mismatch.

## Behavior Parameter Identification

> **Behavior parameter:** layout test mode
>
> **Candidate values:** `layout` writable suite, `readonly` layout suite, `phys` physical-storage-buffer-address suite, `unsized_array_length` runtime-array-length suite

These values identify the primary behavioral axis because each mode changes the access model or the checked rule while sharing the owning source and support harness.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `layout` | Incorrect block offsets, array or matrix strides, access lowering, shader-generated comparison/write logic, descriptor binding, synchronization, or host reference-data handling |
| `readonly` | Incorrect read-only declaration or access handling, layout computation, descriptor setup, shader comparison, or result checking |
| `phys` | Incorrect buffer-device-address support, address transport through push constants, physical storage-buffer reference lowering, or the shared layout/readback path |
| `unsized_array_length` | Incorrect descriptor offset/range interpretation, `VK_WHOLE_SIZE` handling, runtime-array length calculation, 32-bit or 64-bit indexing, or host expected-value computation |

## Important Variations and Special Cases

- The writable `layout` family includes fixed examples and seeded random cases. Random feature bits select vectors, matrices, arrays, structs, nested structs, instance arrays, unused members, layout qualifiers, 8-bit and 16-bit storage, relaxed and scalar layout, descriptor indexing, and 64-bit indexing.
- The `readonly` wrapper uses the same `SSBOLayoutTests` class with `m_readonly=true`; families that require writes are omitted.
- The `phys` wrapper uses the same generated family with `m_usePhysStorageBuffer=true`; support requires buffer-device-address functionality.
- Unsized-array length cases include explicit and whole-size ranges, descriptor offsets, variable pointers, and non-Vulkan SC 64-bit cases. The nested array leaf is delegated to `vktSSBOLayoutNestedUnsizedArraysTests.cpp`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Main registration and mode wrappers | [`createTests()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L2235-L2255) | Defines the `layout`, `unsized_array_length`, `readonly`, `phys`, and delegated `corner_case` groups |
| Generated layout families | [`SSBOLayoutTests::init()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1297-L2188) | Defines fixed and random family dimensions and read-only pruning |
| Runtime-array shader | [`createUnsizedArrayLengthProgs()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1014-L1042) | Shows the generated `length()` and `length64()` program |
| Runtime-array validation | [`ssboUnsizedArrayLengthTest()`](../../../modules/vulkan/ssbo/vktSSBOLayoutTests.cpp#L1044-L1258) | Creates descriptors, dispatches, and computes the expected length |
| Reference layout and shader generation | [`delayedInit()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2756-L2777) | Establishes reference data and generated compute source |
| Layout shader generator | [`generateComputeShader()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L1529-L1645) | Declares resources, compares input, increments the counter, and emits writes |
| Host execution and comparison | [`SSBOLayoutCaseInstance::iterate()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2291-L2648) | Binds buffers, dispatches, barriers, reads back, and returns status |
| Support gates | [`SSBOLayoutCase::checkSupport()`](../../../modules/vulkan/ssbo/vktSSBOLayoutCase.cpp#L2718-L2754) | Maps layout features and device limits to CTS support decisions |
| Registration evidence | [`vk-default/ssbo.txt`](../../../mustpass/main/vk-default/ssbo.txt#L1) and [`vksc-default/ssbo.txt`](../../../mustpass/main/vksc-default/ssbo.txt#L1) | Confirms the `ssbo` direct hierarchy and default Vulkan/Vulkan SC coverage |

## Questions / Risk Points for User Audit

- Is “layout test mode” the right primary behavior axis for separating the four registered modes?
- Does the distinction between shader-generated GLSL objects and host-created buffers remain clear?
- Should the final page include a full SPIR-V listing for the runtime-array example, or is the compact generated-shader walkthrough enough for this family?
- The source and mustpass files contain a large generated leaf set. The page records direct groups and generator dimensions rather than enumerating every leaf.

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to the storage-buffer layout and descriptor-visible runtime-array concepts.
- Use the runtime-array case as the representative shader walkthrough because its generated source is short and exact.
- Carry the failure mapping table into `## Failure Meaning` unchanged.
- Explain the layout shader's compare-counter-write sequence in `## Shader Analysis` and the buffer binding and barrier sequence in `## Runtime Execution and Result Checking`.
- Keep the full registration source inventory in the appendix, with mustpass links as direct registration evidence.
