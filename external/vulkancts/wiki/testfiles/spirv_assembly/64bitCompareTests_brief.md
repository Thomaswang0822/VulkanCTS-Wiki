# Understanding Brief: `64bitCompareTests`

## One-Sentence Test Purpose

This test checks that SPIR-V comparison instructions produce the correct Boolean result for 64-bit floating-point, signed-integer, and unsigned-integer operands in compute, vertex, and fragment shaders, including the defined ordered/unordered behavior when an FP64 operand is NaN.

## Background Knowledge

### Ordered and unordered FP64 comparisons

An **ordered** floating-point comparison (`OpFOrd*`) returns false if either operand is NaN. An **unordered** comparison (`OpFUnord*`) returns true if either operand is NaN; otherwise both families apply the indicated relation such as equal, less-than, or greater-than.

Why it matters here:
- The double operand table has 20 pairs, including three pairs with at least one NaN; it distinguishes ordered from unordered instructions.
- `nonan` cases contain those operands but deliberately do not fail a NaN-position mismatch, because no preservation guarantee was requested. `withnan` cases require the `SignedZeroInfNanPreserve 64` execution mode and check all positions.

### Signed and unsigned integer relations

`OpIEqual` and `OpINotEqual` work for both integer signednesses. Ordering operations encode their interpretation in the opcode: `OpSLessThan`/`OpSGreaterThan*` interpret 64-bit values as signed, while `OpULessThan`/`OpUGreaterThan*` interpret them as unsigned. The unsigned table includes `UINT64_MAX` boundary pairs to make that distinction observable.

### CTS-authored SPIR-V templates

The source specializes SPIR-V assembly templates held in C++ `tcu::StringTemplate` objects. The generated module declares `Float64` or `Int64`, loads two operands from storage buffers at bindings 0 and 1, executes one comparison, converts the resulting Boolean (or Boolean vector) to 32-bit `0`/`1` through `OpSelect`, and stores it at binding 2. The assembly is the authoritative shader source; the comments showing GLSL are explanatory only.

## One Concrete Example

`dEQP-VK.spirv_assembly.instruction.compute.64bit_compare.double.comp_opfordequal_withnan_single` compares the 20 scalar FP64 pairs with `OpFOrdEqual`. The module includes `OpCapability Float64`, `OpCapability SignedZeroInfNanPreserve`, `OpExtension "SPV_KHR_float_controls"`, and `OpExecutionMode %main SignedZeroInfNanPreserve 64`. For every index, it loads the two `double` values, performs `OpFOrdEqual`, and writes `1` or `0`:

```llvm
%40 = OpFOrdEqual %bool %32 %39
%42 = OpSelect %int %40 %int_1 %int_0
OpStore %44 %42
```

The C++ oracle applies the same ordered rule: a NaN operand yields false. Because this is `withnan`, every result, including the NaN positions, must equal that oracle result.

## End-to-End Test Flow

```text
[host] select scalar/vector shape, comparison opcode, type family, stage, and (for FP64) nonan/withnan mode
[host] specialize the matching CTS-authored SPIR-V assembly template
[host] allocate three host-visible storage buffers and fill input bindings 0 and 1 with fixed operand pairs
[host] initialize output binding 2 to -9, flush host writes, and create the compute or graphics pipeline
[device] load each pair, execute one comparison, select integer 1 or 0, and store the result
[host] apply shader-to-host visibility, invalidate the output allocation, and read it back
[host] recompute every expected Boolean with CompareOperation::run()
[host] fail on a checked output value that differs from its expected 0/1 result
```

Fragment cases add a simple GLSL passthrough vertex shader so the authored fragment assembly can run. Vertex cases rasterizer-discard; fragment cases draw a single point through a 1-by-1 render pass with no color attachment because the observable result is the storage-buffer write.

## Generated Test Artifacts and Bound Resources

### Generated program artifacts

- Compute uses one scalar or `vec4` SPIR-V template with `LocalSize 1 1 1`.
- Vertex and fragment use corresponding scalar or `vec4` SPIR-V templates. Fragment cases also compile the fixed `VertShaderPassThrough` GLSL source.
- `Float64` is emitted for `double`; `Int64` for both integer groups. The FP64 `withnan` variant additionally emits the float-controls capability, extension, and execution mode.

### Bound resources

| Resource | Host setup | Device use | Host readback | Purpose |
|----------|------------|------------|---------------|---------|
| Input 1 SSBO, binding 0 | Filled with the left operands | Read | No | First side of each comparison. |
| Input 2 SSBO, binding 1 | Filled with the right operands | Read | No | Second side of each comparison. |
| Output SSBO, binding 2 | Initialized to `-9` | Written as 32-bit `0`/`1` values | Yes | Carries comparison results to the oracle. |
| Fragment passthrough vertex shader | Built only for fragment cases | Runs once | No | Makes the fragment stage executable. |

## What Is Checked

- The scalar shader loops once per operand pair: 20 FP64 pairs, 16 signed-integer pairs, or 12 unsigned-integer pairs.
- The vector shader processes the same flat input in groups of four, yielding a Boolean `vec4` that is selected into an `ivec4`; the host still verifies one integer result per original pair.
- The host calls the operation's C++ `run(left, right)` for each expected result. A checked mismatch produces the failing index and expected/actual `0`/`1` values.
- `nonan` FP64 cases ignore mismatches only at positions involving NaN. `withnan`, signed, and unsigned cases verify every position.

## Behavior Parameter Identification

> **Behavior parameter:** operand/type family
>
> **Candidate values:** `double`, `int64`, `uint64`

The primary distinction is the comparison semantics and operand domain. Stage, scalar-versus-vector representation, individual opcode, and FP64 NaN-preservation mode are secondary dimensions.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `double` ordered comparisons | Incorrect FP64 relation lowering, or failure to return false when either operand is NaN. |
| `double` unordered comparisons | Incorrect FP64 relation lowering, or failure to return true when either operand is NaN. |
| `double` `withnan` | `SignedZeroInfNanPreserve 64` capability/extension/execution-mode handling, NaN transport through the SSBO, or ordered/unordered NaN semantics. |
| `int64` | Signed 64-bit comparison lowering or signed operand transport, especially around negative values. |
| `uint64` | Unsigned 64-bit comparison lowering or unsigned operand transport, especially around `UINT64_MAX`. |
| Any family only in `vert` or `frag` | Stage-specific storage-buffer writes, graphics pipeline setup, or the relevant stores-and-atomics feature path. |
| Any family across stages | Shared descriptor binding, synchronization/readback, generated-template specialization, or host oracle setup. |

## Important Variations and Special Cases

- `double` registers 12 opcodes × 2 shapes × 2 NaN modes: 48 leaves per stage. `int64` and `uint64` each register 6 opcodes × 2 shapes: 12 leaves per stage.
- The compute root has one stage and therefore 72 leaves. The graphics root has vertex and fragment stages and therefore 144 leaves. The standard `vk-default/spirv-assembly.txt` and Vulkan SC `vksc-default/spirv-assembly.txt` lists each contain the resulting 216-path matrix under their respective `dEQP-VK`/`dEQP-VKSC` prefixes.
- `shaderFloat64` is required for double, while `shaderInt64` is required for both integer groups. Vertex and fragment paths additionally require their respective storage-write core features.
- Every `withnan` leaf is skipped when `shaderSignedZeroInfNanPreserveFloat64` support is unavailable through the float-controls support query; it does not merely weaken validation.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration under compute and graphics | [`vktSpvAsmInstructionTests.cpp#L21428-L21519`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21428-L21519) | Adds both roots without a Vulkan SC compile-time exclusion. |
| Template specialization and optional fragment vertex shader | [`T64bitCompareTest::initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1729-L1757) | Selects stage/type template and fills capability, opcode, and NaN slots. |
| Fixed operands | [`DOUBLE_OPERANDS`, `INT64_OPERANDS`, `UINT64_OPERANDS`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1133-L1159) | Defines the exact scalar pairs and boundary values. |
| Host execution and oracle | [`T64bitCompareTestInstance::iterate()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1197-L1638) | Binds buffers, executes, reads back, and checks results. |
| Support gates | [`T64bitCompareTest::checkSupport()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1664-L1726) | Implements type, stage-store, and NaN-preservation requirements. |
| Leaf generators | [`create*CompareTestsInGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1777-L1845) | Defines the Cartesian products and names. |
| Root construction | [`create64bitCompareGraphicsGroup()` and `create64bitCompareComputeGroup()`](../../../modules/vulkan/spirv_assembly/vktSpvAsm64bitCompareTests.cpp#L1901-L1931) | Gives the registered type groups and stages. |

## Conversion Notes for Final Wiki Rewrite

Keep the behavior-family labels and the failure-cause mapping unchanged. The detailed page should use the scalar FP64 `withnan` ordered-equality case for its representative authored-assembly walkthrough, distinguish source assembly from explanatory GLSL comments, and include the parseable 72/144 leaf inventory formula.
