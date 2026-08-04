# Understanding Brief: `spirv_assembly.type`

## One-Sentence Test Purpose

This test checks whether the implementation correctly executes SPIR-V integer type operations — arithmetic, GLSL.std.450 extended math, shifts, bitwise, comparisons, bit-field, and constant/initializer forms — across 8/16/32/64-bit signed and unsigned integers, in scalar and vector widths up to 12 components, when the shader text is authored directly as SPIR-V assembly and run under both compute and graphics stages.

## Background Knowledge

### SPIR-V integer types and the `OpTypeInt` width+signedness pair

SPIR-V `OpTypeInt <width> <signedness>` defines an integer type by its bit width and a 1-bit signedness flag. The type tests instantiate eight combinations: `i8`, `u8`, `i16`, `u16`, `i32`, `u32`, `i64`, `u64` (see [`InputType`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L182-L194) and the per-type constructors at [`vktSpvAsmTypeTests.cpp#L2896-L3220`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2896-L3220)). Each combination is a separate `SpvAsmTypeTests<T>` template specialization, where `T` is the host-side C++ integer type used to compute expected values.

Why it matters here:
- Width implies a Vulkan feature gate: 8-bit tests need `shaderInt8` and 8-bit storage access; 16-bit needs `shaderInt16` and 16-bit storage access; 64-bit needs `shaderInt64`. The host requests these features per case at [`vktSpvAsmTypeTests.cpp#L1841-L1867`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1841-L1867).
- Width implies a SPIR-V capability: `Int8`, `Int16`, `Int64`, plus `UniformAndStorageBuffer8BitAccess` / `UniformAndStorageBuffer16BitAccess` because inputs and outputs live in storage buffers (see [`getSpirvCapabilityStr()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L775-L813)).

### Vector widths beyond 4 and `SPV_EXT_long_vector`

Standard `OpTypeVector %scalar N` accepts `N` in 2..4. The `SPV_EXT_long_vector` extension introduces `OpTypeVectorIdEXT` and the `LongVectorEXT` capability to allow `N` of 1 or `N > 4`. The type tests exercise this path for `vec1` (a 1-component vector, distinct from a scalar) and `vec8`/`vec12`. The choice between `OpTypeVector` and `OpTypeVectorIdEXT` is made at [`vktSpvAsmTypeTests.cpp#L1886-L1916`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1886-L1916) based on the registered `VecSize`.

Why it matters here:
- `vec1` and `vec12` are non-VulkanSC only; they pull in `OpCapability LongVectorEXT` and `OpExtension "SPV_EXT_long_vector"` ([source](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1891-L1916)).
- `vec8` uses standard `OpTypeVector` (8 components in one instruction is allowed by the standard text but not by `OpTypeVector`'s 2..4 range — the type tests deliberately use `OpTypeVector` for vec8 and route only `vec1`/`vec12` through `OpTypeVectorIdEXT`). The vec8 path also enables the long-vector extension declaration.

### Result-type shape per operation family

SPIR-V integer operations differ in result type, which drives the verification logic in [`verifyResult()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2030-L2076):

- Most arithmetic, bitwise, shift, and bit-field operations return the same integer type as the inputs (`%testtype`).
- Comparison operations (`OpIEqual`, `OpUGreaterThan`, etc.) return a boolean scalar or vector. The shader converts booleans to integer 0/1 via `OpSelect` and, when needed, narrows back to the test type via `OpBitcast` or `OpSConvert` ([`finalizeFullOperation()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2753-L2796)).
- 16-bit multiply/shift operations also produce a `_test_high_part_zero` variant that zero-extends the 16-bit result to 32 bits, shifts right by 16, and narrows back, exercising the high-part-zero rule for `OpIMul`/`OpShiftLeftLogical` on `int16`/`uint16` ([`finalizeFullOperation()` returnHighPart path](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2758-L2772)).

### Vec3 padding rule

A three-component vector with component size N has base alignment 4N in std140/std430 layout. The type tests inject a zero padding entry after every three real entries when `m_vectorSize == 3` ([`combine()` padding loop](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1298-L1316)) and skip those padding slots at verification time via [`verifyVec3Result()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2086-L2091) using `skip = 4`. This is the only vector width that requires padding.

## One Concrete Example

A representative case is `spirv_assembly.type.scalar.i32.add_comp`. The compute shader is built from the template at [`computeShaderTemplate`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1705-L1736) with the test-type fragment set to `i32` (`OpTypeInt 32 1`). The host calls `getDataset()` to populate a 10-element `int32` input dataset seeded with `0`, `INT32_MIN+1`, `INT32_MAX`, three switch cases, and random values ([`SpvAsmTypeInt32Tests::getDataset()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L3007-L3024)). The `combine()` overload for binary operations generates a 10×10 = 100-element input/output pair by applying the host's `add()` function to every `(a, b)` pair, with no filter (all pairs are legal). The shader text becomes:

```llvm
%input0 = OpVariable %bufptr Uniform
%input1 = OpVariable %bufptr Uniform
%output = OpVariable %bufptr Uniform

%test_code = OpFunction %v4f32 None %v4f32_v4f32_function
%param    = OpFunctionParameter %v4f32
%entry    = OpLabel
%counter  = OpVariable %fp_i32 Function
OpStore %counter %c_i32_0
OpBranch %loop

%loop = OpLabel
%counter_val = OpLoad %i32 %counter
%lt = OpSLessThan %bool %counter_val %c_i32_100
OpLoopMerge %exit %inc None
OpBranchConditional %lt %write %exit

%write = OpLabel
%output_loc   = OpAccessChain %up_testtype %output %c_i32_0 %counter_val
%input0_loc   = OpAccessChain %up_testtype %input0 %c_i32_0 %counter_val
%input1_loc   = OpAccessChain %up_testtype %input1 %c_i32_0 %counter_val
%input0_val   = OpLoad %i32 %input0_loc
%input1_val   = OpLoad %i32 %input1_loc
%op_result    = OpIAdd %i32 %input0_val %input1_val
OpStore %output_loc %op_result
OpBranch %inc
...
```

The host dispatches `compute 1 1 1` (a single workgroup with one invocation), the shader iterates the input buffers element by element via an `OpLoopMerge`/`OpBranchConditional` loop, applies `OpIAdd` per element, writes the result to the output SSBO, and `verifyDefaultResult()` compares the output buffer element-by-element against the host-computed expected buffer ([`verifyResult()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2030-L2076)).

## End-to-End Test Flow

```text
[host] select (inputType, vectorSize, operation, filter, inputRange, inputWidth, stage)
[host] construct SpvAsmTypeTests<T> with T = host C++ integer type matching inputType
[host] defer createTests() parameters until ::init()
[host] ::init() iterates deferred params and calls doCreateTests() per operation
[host] doCreateTests() calls getDataset() to populate input values with seed cases
[host] combine() generates input0/input1/.../inputsN and outputs by applying host op() to every (filtered) tuple
[host] build SPIR-V assembly text from StringTemplate fragments (computeShaderTemplate or per-stage graphics templates)
[host] set spirvExtensions / spirvCapabilities based on inputType, inputWidth, vectorSize
[host] request Vulkan features: shaderInt8/16/64, 8/16-bit storage, vertexPipelineStoresAndAtomics, fragmentStoresAndAtomics
[host] register test case as <op>_<stage> under <typeSubgroup> under <vecSize> subgroup
[host/device] build pipeline with the assembled SPIR-V (no GLSL frontend in the loop)
[device] execute the test_code function: loop over input buffers, apply the SPIR-V op, write outputs
[host] copy back the output SSBO
[host] verifyResult() compares element-by-element against expected buffer (with vec3 padding skip when needed)
[host] pass iff every non-padding element matches; mismatch logs (inputs, expected, obtained) triple
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- Inline SPIR-V assembly text built from `tcu::StringTemplate` fragments at test construction time. The compute template is [`computeShaderTemplate`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1705-L1736); the graphics per-stage templates live in [`vktSpvAsmGraphicsShaderTestUtil.cpp`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp). The shared `SPIRV_ASSEMBLY_TYPES` / `SPIRV_ASSEMBLY_CONSTANTS` / `SPIRV_ASSEMBLY_ARRAYS` macros ([`vktSpvAsmUtils.hpp#L45-L126`](../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.hpp#L45-L126)) provide the common types and constants.
- Per-test fragments injected via the `${decoration}`, `${pre_main}`, `${testfun}`, `${extension}`, `${capability}` slots. The `${testfun}` body always wraps the operation in an `OpLoopMerge` loop that iterates `numElements` times, so each case is a one-shot dispatch that scans the entire input/output buffer.
- Switch-test variant (scalar only): a different `computeShaderSwitchTemplate` ([`vktSpvAsmTypeTests.cpp#L2509-L2559`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2509-L2559)) that returns `(0.5, 0.5, 0.5, 1.0)` on mismatch and writes a single `int32` 0/1 flag to a binding-2 SSBO.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `input0` (Uniform storage buffer, binding 0) | yes — `Int8Buffer`/`Int16Buffer`/`Int32Buffer`/`Int64Buffer` of `inputs0` | yes | read by `OpLoad` in `test_code` | no (comparison is on the output) | First operand stream |
| `input1` (binding 1) | yes — same pattern | yes | read | no | Second operand stream for binary/ternary/quaternary ops |
| `input2`, `input3` (bindings 2, 3) | yes, when op arity needs them | yes | read | no | Additional operands (bit-field `Offset`/`Count`, `BitFieldInsert`'s `Insert`/`Offset`/`Count`) |
| `output` (binding = numInputs) | yes — same buffer type, holds expected outputs | yes | written by `OpStore` | yes — `verifyResult()` reads it back | Holds shader-computed results; compared against host-computed expected buffer |
| `block` (binding 2, switch tests only) | yes — single `int32` initialized to 0 | yes | written by `OpStore` | yes — `verifyComputeSwitchResult()` checks `== 1` | Switch-test success flag |
| `BP_in_color` / `BP_out_color` (Function storage) | no — shader-local `OpVariable %fp_v4f32 Function` | n/a (shader-local) | n/a | n/a | Plumbing for the graphics-stage wrapper that calls `test_code`; the color itself is irrelevant to verification |

The buffer types and their descriptor kind are produced by the per-type `pushResource()` overrides (e.g. [`SpvAsmTypeInt32Tests::pushResource()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L3026-L3028) using `VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`).

## What Is Checked

- For each generated `(operation, inputType, vectorSize, stage)` tuple, the host computes the expected output buffer by applying the host C++ equivalent of the SPIR-V operation to every (filtered) input tuple.
- The device runs the assembled SPIR-V shader and writes the output SSBO.
- The host reads back the output SSBO and compares it element-by-element against the expected buffer ([`verifyResult()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2030-L2076)).
- For `vec3`, every 4th element is treated as padding and skipped (`verifyVec3Result()` with `skip = 4`).
- For switch tests (scalar only), the host checks a single `int32` flag in the binding-2 SSBO equals 1 ([`verifyComputeSwitchResult()`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L122-L144)).
- The check is exact-equality (no epsilon). Mismatch logs the `(inputs)` triple, `expected`, and `obtained` for the first failing element.
- Each case is checked independently; results are not aggregated across cases.

## Behavior Parameter Identification

> **Behavior parameter:** operation family (behavioral group)
>
> **Candidate values:** arithmetic (incl. GLSL.std.450 extended math), mul-div combined, shift (with bit-width postfix), bitwise logical, comparison (boolean result), bit-field (with offset/count postfix), constant/initializer.

The page-scope test family is `spirv_assembly.type`. Below it sit the vector-width intermediate nodes (`scalar`, `vec1`, `vec2`, `vec3`, `vec4`, `vec8`, `vec12`), each containing eight type subgroups (`i8`/`i16`/`i32`/`i64`/`u8`/`u16`/`u32`/`u64`). Each type subgroup contains one test case leaf per `(operation, stage)` pair, where `stage` ∈ {`_comp`, `_vert`, `_tessc`, `_tesse`, `_geom`, `_frag`}. The operation family is the primary behavioral axis because each family exercises a distinct SPIR-V instruction category with distinct result-type handling, distinct filter rules, and distinct failure semantics.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| Arithmetic (`negate`, `add`, `sub`, `mul`, `div`, `rem`, `mod`, `abs`, `sign`, `min`, `max`, `clamp`) | Wrong result for the SPIR-V integer op or its GLSL.std.450 extended form; width-specific storage buffer load/store mismatch; INT_MIN / divide-by-zero / signed-overflow edge case mishandled despite the host filter |
| Mul-div combined (`mul_sdiv`, `mul_udiv`) | `OpIMul` → `OpSDiv`/`OpUDiv` chain lowered incorrectly; intermediate width handling wrong; signed vs unsigned division selected wrong |
| Shift (`shift_right_logical`, `shift_right_arithmetic`, `shift_left_logical`, with `_shift8`/`_shift16`/`_shift32`/`_shift64` postfix) | Wrong shift semantics (logical vs arithmetic right shift); shift count not masked to bit width; cross-width `OpSConvert` of the shift operand wrong; `_test_high_part_zero` 16-bit high-part extraction wrong |
| Bitwise logical (`bitwise_or`, `bitwise_xor`, `bitwise_and`, `not`) | Wrong bitwise op selection for the signedness; width-mismatched operand conversion (`OpSConvert`) wrong |
| Comparison (`iequal`, `inotequal`, `ugreaterthan`, `sgreaterthan`, `ugreaterthanequal`, `sgreaterthanequal`, `ulessthan`, `slessthan`, `ulessthanequal`, `slessthanequal`) | Signed vs unsigned comparison opcode selected wrong; boolean→integer `OpSelect` conversion wrong; `OpBitcast`/`OpSConvert` narrowing back to test type wrong; vector boolean result type wrong |
| Bit-field (`bit_field_insert`, `bit_field_s_extract`, `bit_field_u_extract`, `bit_reverse`, `bit_count`, with `_offset{8,16,32,64}_count{8,16,32,64}` postfix) | Offset/count width conversion (`OpSConvert`) wrong; bit-field insertion/extraction semantics wrong for the offset+count combination; `OpBitReverse`/`OpBitCount` lowering wrong; non-32-bit type requires `VK_KHR_maintenance9` and the device lacks it or miscompiles |
| Constant/initializer (`constant`, `constant_composite`, `constant_null`, `variable_initializer`, `spec_constant_initializer`, `spec_constant_composite_initializer`) | `OpConstant`/`OpConstantComposite`/`OpConstantNull` literal value or composite assembly wrong; `OpVariable` initializer not honored; specialization constant not wired from host; `OpSpecConstantComposite` constituent mismatch |

Shared infrastructure causes that affect every value:

- The compute/graphics stage wrapper (descriptor binding layout, `OpFunctionCall %test_code`, loop structure) is shared, so a wrapper-level bug would surface across multiple operation families and types simultaneously.
- The `verifyResult()` host comparison is shared; a buffer-stride or element-size mismatch in `pushResource()` (e.g. `Int8Buffer` vs `Int16Buffer` for `int16`) would mismatch every element of every operation in that type subgroup.

## Important Variations and Special Cases

- **`_test_high_part_zero` 16-bit variant**: For 16-bit signed/unsigned types, the multiply and shift families additionally register a `<op>_test_high_part_zero_<stage>` variant that zero-extends the 16-bit result to 32 bits via `OpUConvert`, shifts right by 16 via `OpShiftRightLogical`, and narrows back via `OpSConvert`/`OpUConvert`. This tests the SPIR-V rule that `OpIMul`/`OpShiftLeftLogical` on a 16-bit type produces a 16-bit result whose high part is implementation-defined; the variant explicitly checks the high part is zero. Generated by the `MAKE_TEST_SV_I_8136`/`MAKE_TEST_SV_U_8136` macros with `returnHighPart = true` ([`finalizeFullOperation()` returnHighPart branch](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2758-L2772)).
- **Vec3 padding**: Only `vec3` injects a zero padding entry after every three real entries and skips those slots at verification. Other vector widths have no padding.
- **Switch tests (scalar only)**: `createSwitchTests()` ([`vktSpvAsmTypeTests.cpp#L2485-L2748`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2485-L2748)) registers an additional `<typeSubgroup>` switch test that uses a different compute template writing a single `int32` flag, exercising `OpSwitch` against three case constants plus a default. Vector subgroups do not get this variant.
- **Non-VulkanSC vector widths**: `vec1`, `vec8`, `vec12` are registered only when `CTS_USES_VULKANSC` is not defined. VulkanSC builds keep `scalar`, `vec2`, `vec3`, `vec4`. `vec1` and `vec12` go through `OpTypeVectorIdEXT`; `vec8` uses standard `OpTypeVector` but still declares `SPV_EXT_long_vector` because 8 components exceed the 4-component limit of the standard's `OpTypeVector`.
- **Bit-field input widths**: `bit_field_insert`/`bit_field_s_extract`/`bit_field_u_extract` register 16 width combinations per type per vector size (`_offset{8,16,32,64}_count{8,16,32,64}`), exercising `OpSConvert` between the test type width and the offset/count operand widths. `bit_reverse` and `bit_count` do not take width postfixes.
- **Shift input widths**: shift operations register 4 width postfixes per type per vector size (`_shift8`/`_shift16`/`_shift32`/`_shift64`), exercising `OpSConvert` between the test type width and the shift-count operand width. The shift count is masked to `m_typeSize - 1` in the host (`RANGE_BIT_WIDTH`) to keep it within the type's bit width.
- **Non-32-bit bit-field on VulkanSC**: VulkanSC uses the `MAKE_TEST_SV_*_3_W` reduced macro path for bit-field operations, generating only `i32`/`u32` variants; non-VulkanSC uses the broader `MAKE_TEST_SV_*_8136_WN` set covering 8/16/32/64-bit types. Non-32-bit bit-field operations on non-VulkanSC additionally require `VK_KHR_maintenance9` because SPIR-V restricts `OpBitField*` operands to 32-bit unless `VK_KHR_maintenance9` is enabled ([`vktSpvAsmTypeTests.cpp#L1869-L1874`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1869-L1874)).
- **GLSL.std.450 extended operations**: `abs`, `sign`, `min`, `max`, `clamp`, `find_lsb`, `find_msb` are not raw SPIR-V ops; they go through `OpExtInst` against the imported `GLSL.std.450` extended instruction set. The assembly imports the set via `%ext1 = OpExtInstImport "GLSL.std.450"` and the operation text uses `OpExtInst %<resultType> %ext1 <GLSLstd450Op> <operands>` ([`doCreateTests()` OpExtInst branch](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2349-L2353)).

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| `SpvAsmTypeTests<T>` template class | [`vktSpvAsmTypeTests.cpp#L919-L1193`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L919-L1193) | Owns the createTests()/doCreateTests() API, deferred-parameter init, and the host verification callbacks |
| Compute shader template | [`vktSpvAsmTypeTests.cpp#L1705-L1736`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1705-L1736) | The SPIR-V assembly text the type tests specialize per case |
| `combine()` binary overload | [`vktSpvAsmTypeTests.cpp#L1339-L1422`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1339-L1422) | Generates input0/input1/output triples with optional vec3 padding and `RANGE_BIT_WIDTH` shift masking |
| `verifyResult()` | [`vktSpvAsmTypeTests.cpp#L2030-L2076`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2030-L2076) | Element-by-element output comparison with vec3 padding skip |
| `finalizeFullOperation()` | [`vktSpvAsmTypeTests.cpp#L2753-L2796`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2753-L2796) | Appends boolean-result `OpSelect` conversion or `_test_high_part_zero` high-part extraction |
| `getSpirvCapabilityStr()` | [`vktSpvAsmTypeTests.cpp#L775-L813`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L775-L813) | Emits `OpCapability Int8/Int16/Int64/LongVectorEXT` and storage-buffer 8/16-bit access capabilities |
| Operation macros (MAKE_TEST_*) | [`vktSpvAsmTypeTests.cpp#L4042-L4276`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4042-L4276) | Macro-expanded registration of every operation across types, vector sizes, and width postfixes |
| `createTypeTests()` | [`vktSpvAsmTypeTests.cpp#L4278-L4456`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L4278-L4456) | Root registration: builds `scalar`/`vecN` containers and attaches the eight type subgroups |
| Switch tests | [`vktSpvAsmTypeTests.cpp#L2485-L2748`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2485-L2748) | Scalar-only `OpSwitch` variant with a different compute template and binding-2 flag SSBO |
| VecSize enum and `OpTypeVectorIdEXT` routing | [`vktSpvAsmTypeTests.cpp#L85-L109`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L85-L109), [`vktSpvAsmTypeTests.cpp#L1886-L1916`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L1886-L1916) | Decides whether to emit `OpTypeVector` or `OpTypeVectorIdEXT` for `vec1`/`vec8`/`vec12` |
| Per-type concrete classes | [`vktSpvAsmTypeTests.cpp#L2896-L3220`](../../modules/vulkan/spirv_assembly/vktSpvAsmTypeTests.cpp#L2896-L3220) | `SpvAsmTypeInt8Tests` ... `SpvAsmTypeUint64Tests`; each sets the SPIR-V type string, capability, feature, and dataset |
| `SPIRV_ASSEMBLY_TYPES` / `CONSTANTS` / `ARRAYS` macros | [`vktSpvAsmUtils.hpp#L45-L126`](../../modules/vulkan/spirv_assembly/vktSpvAsmUtils.hpp#L45-L126) | Shared SPIR-V preamble types and constants inlined into every type-test shader |
| `createTestsForAllStages()` | [`vktSpvAsmGraphicsShaderTestUtil.cpp#L4902-L4928`](../../modules/vulkan/spirv_assembly/vktSpvAsmGraphicsShaderTestUtil.cpp#L4902-L4928) | Registers the `_vert`/`_tessc`/`_tesse`/`_geom`/`_frag` stage variants for each case |

## Questions / Risk Points for User Audit

- Is the behavioral-axis choice (operation family as behavioral group, with type and vector size as secondary configuration axes) the right framing, or should the type/width be treated as the primary axis instead?
- The shader walkthrough is necessarily one representative case; is the `scalar.i32.add_comp` representative the right pick, or should the walkthrough cover a comparison case (boolean result) or a bit-field case (offset/count width conversion) to show the more interesting `finalizeFullOperation()` paths?
- Should the page treat the 6 stage suffixes (`_comp`/`_vert`/`_tessc`/`_tesse`/`_geom`/`_frag`) as a behavior parameter or as a pure configuration detail that doesn't change what's being tested?
- The non-32-bit bit-field operations require `VK_KHR_maintenance9`; is the failure-mode analysis for "device lacks maintenance9" (skip vs fail) correct, given the source only requests the feature and does not gate registration?

## Conversion Notes for Final Wiki Rewrite

- Distill Background Knowledge to: (1) `OpTypeInt` width+signedness pair and the implied feature/capability gates; (2) the `SPV_EXT_long_vector` / `OpTypeVectorIdEXT` path for `vec1`/`vec12`; (3) the result-type-per-family distinction (boolean for comparisons, high-part-zero for 16-bit mul/shift); (4) the vec3 padding rule. Drop the detailed `OpTypeInt` example, since the per-type constructors are visible in the source appendix.
- Use `scalar.i32.add_comp` as the representative walkthrough because it is the simplest case that shows the full compute template shape. Add a brief contrast paragraph for a comparison case (boolean result via `OpSelect`) and a bit-field case (offset/count width conversion) without separate walkthroughs.
- Carry the `### Failure Cause Mapping` table verbatim into the final page.
- Write `### Cause Analysis` fresh during the rewrite, with one `####` subsection per failure cause family.
- Move the detailed macro inventory and per-type constructor table to `## Source Reference Appendix` rather than the page body.
- Keep the registration tree at `spirv_assembly.type` showing only the vector-width intermediate nodes (with `(non-VulkanSC only)` markers on `vec1`/`vec8`/`vec12`); do not expand the type subgroups or operation leaves in the tree.
- The brief's `### Failure Cause Mapping` table is the canonical version copied into the final page.
