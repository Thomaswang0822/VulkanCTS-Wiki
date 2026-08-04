# Understanding Brief: `spirv_assembly.instruction.maint9_vectorization`

## One-Sentence Test Purpose

This test family checks that a Vulkan implementation executes `OpBitCount`, `OpBitReverse`, `OpBitFieldInsert`, `OpBitFieldSExtract`, and `OpBitFieldUExtract` correctly when their integer operands use scalar or four-component vector forms and 8-, 16-, 32-, or 64-bit widths.

## Background Knowledge

### Per-component vector integer operations

SPIR-V integer vector instructions operate on corresponding vector components. This family uses either a scalar or a four-component vector for the data operands, while `offset` and `count` remain scalar for bit-field operations.

Why it matters here:
- The same generated instruction must preserve scalar semantics and apply them independently to each of four vector components.
- `OpBitCount` permits a result type with a different width from its base type, while the other generated operations use matching result and base types.

### Physical storage-buffer addresses

The generated module places a physical address for each result or operand buffer in one storage-buffer descriptor. The shader follows those addresses to load its operands and store its result. `PhysicalStorageBufferAddresses` and `bufferDeviceAddress` support that indirection.

Why it matters here:
- The source uses separate buffers and address indirection to prevent shader compilers from scalarizing the vectorized operands on some implementations.
- The host and the generated assembly therefore agree on both data width and physical-buffer layout.

### Bit-field ranges and signed extraction

For `OpBitFieldInsert`, `OpBitFieldSExtract`, and `OpBitFieldUExtract`, `offset` selects the starting bit and `count` selects the number of bits. The host restricts them so the selected field fits in the base component width. Signed extraction sign-extends the selected field; unsigned extraction does not.

Why it matters here:
- The test can use random data without generating an out-of-range bit field.
- The host reference must mask a sign-extended result back to the selected result width before comparing it with the shader output.

## One Concrete Example

Consider `dEQP-VK.spirv_assembly.instruction.maint9_vectorization.bit_field_s_extract.result_v16i-base_v16i-offset_s32i-count_s32i`.

- The test creates a four-component signed 16-bit result and base, with scalar signed 32-bit `offset` and `count` operands.
- `initPrograms()` emits `OpTypeVector %i16scalar 4`, physical-storage-buffer pointer types, and one `OpBitFieldSExtract` instruction that loads the base vector and scalar field arguments before storing the vector result.
- The host generates 64 pseudorandom operand sets. It restricts `offset` to `0..16` and `count` to `0..(16-offset)`, applies the signed bit-field reference calculation to every vector component, and compares all 64 GPU results against that reference.

Changing this case to `result_v16u-base_v16u-offset_s32u-count_s32u` changes integer signedness, while replacing `bit_field_s_extract` with `bit_field_u_extract` changes the reference operation's sign-extension rule.

## End-to-End Test Flow

```text
[host] choose the operation and its scalar/vector, width, and signedness parameters
[host] check Vulkan version and the width- and address-related feature requirements
[host] generate SPIR-V assembly for the selected operand list
[host] create one host-visible, device-addressable buffer per result or input operand
[host] generate 64 pseudorandom operand sets; constrain bit-field offset and count when needed
[host] write the operand bytes and their device addresses to the buffers
[host] build and dispatch one 64-invocation compute workgroup
[device] each invocation follows the buffer addresses, loads its operands, executes the selected OpBit* instruction, and stores one result
[host] invalidate the result allocation, compute the CPU reference for every invocation, and compare the values
[host] fail the case after logging every mismatch, or report Pass
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- [`M9V_Case::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L325-L717) generates a SPIR-V 1.6 compute module. It conditionally emits `Int8`, `Int16`, `Int64`, storage-access capabilities, data types, array strides, and physical-storage-buffer pointer types from the selected operand list.
- [`getOperandListTestName()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L146-L153) builds each test-case leaf name from operand role, scalar/vector form, width, and signedness.
- [`createMaint9VectorizationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1415) generates the five operation families and their parameter combinations.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Result buffer | yes, one element per invocation | indirectly through the references buffer | written | yes | Buffer 0 stores the selected operation's output. |
| Operand buffers | yes, one buffer for each input role | indirectly through the references buffer | read | no | Supply `base`, optional `insert`, and optional `offset` and `count` values. |
| References buffer | yes, populated with `VkDeviceAddress` values | yes, storage-buffer descriptor binding 0 | read | no | Supplies the physical addresses of every result and operand buffer to the generated shader. |
| Descriptor set | yes | yes | read by pipeline setup | no | Contains the one storage-buffer descriptor for the references buffer. |

## What Is Checked

- [`genValuesForOp()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L907-L951) generates random integer data. For bit-field operations, it generates valid scalar `offset` and `count` values after generating the other operands.
- [`calcOpBitCount()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1001-L1015), [`calcOpBitReverse()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1017-L1031), and the three bit-field helpers calculate the expected value component by component on the host.
- [`M9V_Instance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1137-L1285) compares each result-buffer element with the host reference. A mismatch logs the invocation index, operation and operands, expected value, and observed value; any mismatch fails the test.

## Behavior Parameter Identification

> **Behavior parameter:** direct operation family under `spirv_assembly.instruction.maint9_vectorization`
>
> **Candidate values:** `bit_count`, `bit_reverse`, `bit_field_insert`, `bit_field_s_extract`, `bit_field_u_extract`

The first two families have one data operand. `bit_field_insert` combines a base and an insert value, while the two extraction families select a field from the base and differ only in signed versus unsigned extraction semantics.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `bit_count` | `OpBitCount` lowering is wrong for a selected width or scalar/vector form, or a differing result width is handled incorrectly. |
| `bit_reverse` | `OpBitReverse` reverses the wrong component width, mishandles signed or unsigned integer representation, or fails to preserve vector components. |
| `bit_field_insert` | `OpBitFieldInsert` applies `offset` or `count` incorrectly, places the inserted bits incorrectly, or mishandles scalar field arguments with a vector base. |
| `bit_field_s_extract` | `OpBitFieldSExtract` selects the wrong field or sign-extends it incorrectly for the selected base width. |
| `bit_field_u_extract` | `OpBitFieldUExtract` selects the wrong field or introduces signed-extension behavior where zero extension is required. |

## Important Variations and Special Cases

- `bit_count` iterates scalar and four-component forms, four base widths, four result widths, and signed or unsigned types. The result width can differ from the base width.
- `bit_reverse` keeps result and base type equal, then varies scalar/vector form, width, and signedness.
- `bit_field_insert` uses matching result, base, and insert types. It varies scalar/vector form and base width independently from the scalar `offset` and `count` widths and signedness.
- Both extraction families use matching result and base types, with independently selected scalar `offset` and `count` widths and signedness.
- Every selected 8-, 16-, or 64-bit operand type changes the generated capability and feature requirements. A non-32-bit base requires `VK_KHR_maintenance9`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Parameter constraints and feature checks | [`TestParams` and `M9V_Case::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L155-L323) | Defines legal operand relationships and checks Vulkan 1.3, `VK_KHR_maintenance9`, device addresses, scalar layout, and integer-width support. |
| SPIR-V generator | [`M9V_Case::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L325-L717) | Builds the selected assembly module, including physical-buffer addressing and the chosen `OpBit*` instruction. |
| Random input generation | [`genSingleOperand()` and `genValuesForOp()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L877-L951) | Generates input bytes and constrains bit-field ranges. |
| Host reference operations | [`singleBit*` and `calcOp*`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L953-L1126) | Defines the CPU oracle for all five operation families. |
| Runtime and result comparison | [`M9V_Instance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1137-L1285) | Allocates buffers, dispatches the shader, reads results, and reports mismatches. |
| Family registrations | [`createMaint9VectorizationTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmMaint9VectorizationTests.cpp#L1291-L1415) | Registers the five direct operation-family children and their generated leaves. |
| Executable leaves | [`spirv-assembly.txt#L39903-L43054`](../../../mustpass/main/vk-default/spirv-assembly.txt#L39903-L43054) | Lists the mustpass cases rooted at `maint9_vectorization`. |

## Questions / Risk Points for User Audit

- Does the operation-family behavior axis make the difference between the two extraction semantics clear enough?
- Is the selected vector signed-extraction case a useful representative of the physical-addressed vector path, with the other operation and type variants summarized rather than expanded into separate walkthroughs?
- Should the final page publish the specialized generated assembly, or does a source-linked explanation of the template better preserve the relation between the large parameter matrix and the conditional module text?

## Conversion Notes for Final Wiki Rewrite

- Use the five operation families as `## Behavior Parameters` subsections and copy the failure-cause mapping table verbatim.
- Distill only vector component semantics, physical storage-buffer addresses, and signed/unsigned extraction into final `## Background Knowledge`.
- Use one vector bit-field-extraction case to explain the generated assembly shape. The final page should state its selected operands and link to `initPrograms()` rather than hand-copying an unverified specialization.
- Keep the generator, feature checks, reference implementation, runtime loop, registrations, and mustpass range in the final source appendix.
