# Understanding Brief: spirv_assembly pointer_parameter

## One-Sentence Test Purpose

This test checks whether a Vulkan implementation honors SPIR-V pointers passed as function parameters across the `Function`, `Private`, `StorageBuffer`, and `Workgroup` storage classes, including `Aliased` parameter semantics, `VariablePointers`/`VariablePointersStorageBuffer` capabilities, and `WorkgroupMemoryExplicitLayoutKHR`.

## Background Knowledge

### SPIR-V pointers as function parameters

SPIR-V allows a function to declare parameters whose type is `OpTypePointer` to some storage class. A call passes an existing pointer (for example the result of `OpAccessChain` or a variable address) to the callee, which then dereferences it with `OpLoad`/`OpStore`. This is the SPIR-V analog of passing a pointer argument in C: the callee operates on the caller's storage through the parameter.

Why it matters here:
- The whole test family exists to exercise this parameter-passing path; if the compiler or driver mis-handles a pointer parameter, the callee writes to or reads from the wrong storage and the output buffer mismatches.
- SPIR-V also constrains *which* storage classes may be pointed at by a parameter and *which* pointer operations are allowed without extra capabilities. Plain `Function` and `Private` pointers are always allowed; `StorageBuffer` and `Workgroup` pointers require variable-pointer support.

### Aliased and Restrict pointer decoration

SPIR-V `OpDecorate` with `Aliased` (the default) tells the compiler that a function parameter *may* alias other parameters or variables, so writes through one pointer must remain visible through another. `Restrict` asserts no aliasing and would permit the compiler to reorder or eliminate redundant loads/stores. The test deliberately uses `Aliased` and then calls the function twice — once with both parameters pointing at the same variable, once with distinct variables — so the result is only correct if the compiler preserved aliasing semantics.

Why it matters here:
- The expected output (`7.0f`) is the sum of two function calls. The first call (`func(&a, &a)`) only returns `2.0` if the write through `f` to the aliased variable is visible through the subsequent read of `g`. If a compiler incorrectly applied restrict-style forwarding, the call would return the stale `5.0` and the test would fail.

### Variable pointers and storage-class capability gating

`VariablePointersStorageBuffer` permits pointer expressions (including function parameters and `OpAccessChain` results) that point into the `StorageBuffer` storage class. `VariablePointers` is the broader capability that also permits pointers into the `Workgroup` storage class. Both are exposed through `VK_KHR_variable_pointers` (or Vulkan 1.1+ core). The SPIR-V extensions `SPV_KHR_variable_pointers` and `SPV_KHR_storage_buffer_storage_class` declare the assembly-level support.

Why it matters here:
- `buffer_memory`/`buffer_memory_variable_pointers` pass `StorageBuffer` array pointers to functions and require `VariablePointersStorageBuffer`.
- `workgroup_memory_variable_pointers` passes `Workgroup` array pointers to functions and requires the full `VariablePointers` capability, plus `WorkgroupMemoryExplicitLayoutKHR` so the workgroup variable can be decorated with explicit member layout.

### Workgroup explicit layout and cross-invocation sharing

`SPV_KHR_workgroup_memory_explicit_layout` lets a `Workgroup` variable be decorated with member offsets and array strides, mirroring a block layout. The workgroup-memory case uses a `Workgroup` struct of two arrays, has each invocation write one slot per array through pointer parameters, synchronizes with `OpControlBarrier`, then reads a *shuffled* partner slot written by a different invocation. The expected output is computed on the host from the shuffle formula `((idx + 1) mod 16)`.

Why it matters here:
- This is the only family that crosses invocation boundaries through shared memory, so it exercises both pointer-parameter semantics and workgroup synchronization. A barrier or visibility bug here produces a different failure shape than the aliasing cases.

## One Concrete Example

A faithful, simplified extract of the compute `param_to_param` shader ([vktSpvAsmPointerParameterTests.cpp#L68-L129](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L68-L129)):

```llvm
                          OpDecorate %f Aliased
                          OpDecorate %g Aliased
            %func0_decl = OpTypeFunction %float %_ptr_Function_float %_ptr_Function_float
                  %func = OpFunction %float None %func0_decl
                     %f = OpFunctionParameter %_ptr_Function_float
                     %g = OpFunctionParameter %_ptr_Function_float
            %func_entry = OpLabel
                          OpStore %g %float_5
                          OpStore %f %float_2
                   %ret = OpLoad %float %g
                          OpReturnValue %ret
                          OpFunctionEnd
; caller:
                  %ret0 = OpFunctionCall %float %func %a %a   ; aliasing call, returns 2.0
                  %ret1 = OpFunctionCall %float %func %a %b   ; non-aliasing call, returns 5.0
```

Each compute invocation writes `ret0 + ret1 = 7.0` into its slot of a 128-element output buffer. The shader is authored directly as SPIR-V assembly in the C++ source; there is no GLSL or HLSL source.

## End-to-End Test Flow

```text
[host] choose test family and pipeline (compute or graphics) and required features
[host] build the SPIR-V assembly string for the selected family
[host] create the output storage buffer and (for graphics) input color attachments
[host] set descriptor set 0 / binding 0 to the output buffer; pass specialization dims where needed
[host] submit compute dispatch or graphics draw
[device] entry/main calls helper function(s) through OpFunctionCall with pointer parameters
[device] helper functions write through the pointer parameters to function/private/storage/workgroup storage
[device] (workgroup case only) OpControlBarrier, then each invocation reads a shuffled partner slot
[device] result is written to the bound output storage buffer
[host] read back the output buffer and compare against a CPU-computed expected sequence
[host] pass iff every element matches the expected value
```

Compute and graphics share the same pointer-parameter idea but use different factories: `createPointerParameterComputeGroup` registers five single-shader compute cases; `createPointerParameterGraphicsGroup` registers four base families, each expanded by `createTestsForAllStages` into `vert`, `frag`, `geom`, `tessc`, and `tesse` stage-suffixed cases.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- **Authored SPIR-V assembly strings**, one per compute family, embedded directly in the C++ source as `const string shaderSource`. There is no GLSL/HLSL source and no Amber script; the assembly is the source of truth. Graphics families supply the same kind of assembly through `fragments["pre_main"]`, `fragments["decoration"]`, `fragments["testfun"]`, and optionally `fragments["extension"]`/`fragments["capability"]`, which the graphics test harness stitches into a per-stage shader template.
- The assembly declares its own capabilities and extensions inline (`OpCapability VariablePointersStorageBuffer`, `OpExtension "SPV_KHR_variable_pointers"`, etc.).

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Output storage buffer (`dataOutput`) | yes | yes, descriptor set 0 binding 0 | written by shader | yes | Holds the per-invocation result that the host compares against the expected sequence. |
| `Function`/`Private` variables (`a`, `b`, `o`) | no — shader-local | n/a (shader-local) | read/written by shader | no | The aliased pointer targets in `param_to_param`/`param_to_global`; their storage class is the tested property. |
| `Workgroup` variable (`sharedData`) | no — shader-local | n/a (shader-local) | read/written by shader | no | Cross-invocation shared storage for the workgroup-memory case; requires `VariablePointers` and explicit layout. |
| Graphics input/output color attachments | yes | yes | read/written by fixed function + shader | yes (compared) | Drive the graphics pipeline so the per-stage `test_code` runs once. |

## What Is Checked

- The host compares the read-back output buffer element-by-element against a CPU-computed expected sequence. There is no tolerance; every float must match.
- Expected sequences:
  - `param_to_param`, `param_to_global`, and the graphics `global_to_param`/`param_to_global`: 128 (or 1 per stage for graphics) elements of `7.0f`.
  - `buffer_memory` and `buffer_memory_variable_pointers`: first half `5.0f`, second half `2.0f` (16 `vec4`s of each constant).
  - `workgroup_memory_variable_pointers`: a shuffled pattern computed from `((idx + 1) mod 16)`, with the first output array holding `shuffleIdx + 5` and the second holding `shuffleIdx`, each replicated four times per `vec4`.
- The check is host-side; the shader only writes results. A mismatch means the pointer-parameter writes did not land where the test expected.

## Behavior Parameter Identification

> **Behavior parameter:** test family (the registered family name), because each family selects a distinct combination of pointer storage class, capability, and synchronization shape.
>
> **Candidate values:** `param_to_param` / `global_to_param`, `param_to_global`, `buffer_memory`, `buffer_memory_variable_pointers`, `workgroup_memory_variable_pointers`.

A secondary axis is the **pipeline** (`compute` vs `graphics`): the graphics path reuses four of the five compute behaviors under stage-suffixed names and does not add a new pointer-storage-class behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `param_to_param` / `global_to_param` | Aliased pointer parameter semantics not preserved: a write through one parameter not visible through an aliasing parameter read, or function-call argument wiring dropped the aliasing relationship. |
| `param_to_global` | Cross-storage-class pointer parameter handling broken for `Private` or `Function` targets, or aliased global/parameter interaction mis-compiled. |
| `buffer_memory` | `StorageBuffer` pointer parameter dereference or `VariablePointersStorageBuffer` capability handling incorrect; pointer arithmetic / `OpAccessChain` into a runtime or fixed array mis-lowered. |
| `buffer_memory_variable_pointers` | Same storage-buffer pointer causes as `buffer_memory`; the separately registered case is otherwise near-identical in the inspected source (it still emits `VariablePointersStorageBuffer`, not full `VariablePointers`). |
| `workgroup_memory_variable_pointers` | `Workgroup` pointer parameter handling under full `VariablePointers` broken, `WorkgroupMemoryExplicitLayoutKHR` layout mis-handled, or `OpControlBarrier` did not make partner writes visible before the shuffled read. |

All families share the same final host comparison: any element of the output buffer that differs from the CPU-computed expected value fails the case.

## Important Variations and Special Cases

- **Naming asymmetry.** Compute `param_to_param` corresponds to graphics `global_to_param`. Both test aliased `Function`-storage-class pointers as function parameters; the graphics variant is just stage-suffixed and built from fragments. This is a naming difference, not a behavioral difference.
- **`buffer_memory_variable_pointers` is near-identical to `buffer_memory` in the inspected source.** Despite its name suggesting full `VariablePointers`, it emits `OpCapability VariablePointersStorageBuffer` and requests `VK_KHR_variable_pointers` with `variablePointersStorageBuffer = true`, exactly like `buffer_memory`. The only assembly-level difference is the order of the two `OpExtension` lines. A reader should not assume this family exercises a stronger capability than `buffer_memory` based on its name alone.
- **`workgroup_memory_variable_pointers` is compute-only.** It is the only family that requires SPIR-V 1.4 (`spec.spirvVersion = SPIRV_VERSION_1_4`), the full `VariablePointers` capability, and `WorkgroupMemoryExplicitLayoutKHR`. Graphics has no equivalent.
- **Graphics stage expansion.** Each graphics base family becomes five cases (`_vert`, `_frag`, `_geom`, `_tessc`, `_tesse`) through `createTestsForAllStages`. The per-stage shader is assembled by injecting `pre_main`/`decoration`/`testfun` (and `extension`/`capability` for the buffer families) into a stage template; the pointer-parameter logic itself does not change across stages.
- **Output storage class differs by factory.** Compute `param_to_param`/`param_to_global` and the graphics `global_to_param`/`param_to_global` use the `Uniform` storage class with `BufferBlock` for the output. The `buffer_memory` families use `StorageBuffer` with `Block` and `SPV_KHR_storage_buffer_storage_class`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Compute `param_to_param` builder + assembly | [vktSpvAsmPointerParameterTests.cpp#L45-L141](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L45-L141) | Aliased `Function` pointer parameters; expected `7.0f`. |
| Compute `param_to_global` builder + assembly | [vktSpvAsmPointerParameterTests.cpp#L143-L257](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L143-L257) | `Private` + `Function` pointer parameters; expected `7.0f`. |
| Compute `buffer_memory` builder + assembly | [vktSpvAsmPointerParameterTests.cpp#L259-L386](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L259-L386) | `StorageBuffer` array pointer parameters; `VariablePointersStorageBuffer`. |
| Compute `buffer_memory_variable_pointers` builder | [vktSpvAsmPointerParameterTests.cpp#L388-L514](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L388-L514) | Near-identical to `buffer_memory`; still emits `VariablePointersStorageBuffer`. |
| Compute `workgroup_memory_variable_pointers` builder | [vktSpvAsmPointerParameterTests.cpp#L516-L690](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L516-L690) | `Workgroup` pointer parameters; `VariablePointers`; SPIR-V 1.4; shuffled output. |
| Graphics `global_to_param` (aliasing) builder | [vktSpvAsmPointerParameterTests.cpp#L692-L767](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L692-L767) | Graphics counterpart of compute `param_to_param`. |
| Graphics `param_to_global` builder | [vktSpvAsmPointerParameterTests.cpp#L769-L862](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L769-L862) | Graphics counterpart of compute `param_to_global`. |
| Graphics `buffer_memory` builder | [vktSpvAsmPointerParameterTests.cpp#L864-L970](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L864-L970) | Graphics storage-buffer pointer parameters across all stages. |
| Graphics `buffer_memory_variable_pointers` builder | [vktSpvAsmPointerParameterTests.cpp#L972-L1078](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L972-L1078) | Graphics counterpart of compute `buffer_memory_variable_pointers`. |
| Compute group factory | [vktSpvAsmPointerParameterTests.cpp#L1082-L1093](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1082-L1093) | Registers the five compute cases under `pointer_parameter`. |
| Graphics group factory | [vktSpvAsmPointerParameterTests.cpp#L1095-L1105](../../../modules/vulkan/spirv_assembly/vktSpvAsmPointerParameterTests.cpp#L1095-L1105) | Registers the four graphics base families under `pointer_parameter`. |

## Questions / Risk Points for User Audit

- Is the behavior-parameter axis (test family) the right primary axis, or should the page lead with pointer storage class instead? The brief treats them as equivalent because each family maps to exactly one storage class + capability combination.
- Is it acceptable to call out that `buffer_memory_variable_pointers` does *not* actually exercise full `VariablePointers` in the inspected source, or should that be softened to avoid implying a CTS defect?
- The graphics families are stage-suffixed variants of compute behaviors 1–4. Is two compute walkthroughs (`param_to_param` and `workgroup_memory_variable_pointers`) the right representative depth, with graphics described in prose only?
- Should the page treat the `Uniform`/`BufferBlock` output of the aliasing tests as a notable variation, or as boilerplate not worth foregrounding?

## Conversion Notes for Final Wiki Rewrite

- Distill the Background Knowledge into a short bullet list: pointer-as-function-parameter, `Aliased` vs `Restrict`, variable-pointer capability gating, and workgroup explicit layout. Drop the longer teaching scaffolding.
- Use two representative shader walkthroughs: compute `param_to_param` (simplest aliased `Function` pointer case) and compute `workgroup_memory_variable_pointers` (most behavior-rich, `Workgroup` + `VariablePointers` + barrier + shuffle). Under the TEMP-SPIRV-ASSEMBLY deviation, `#### Source Code` holds the extracted SPIR-V assembly verbatim from the C++ string templates; the `#### SPIR-V` subsection is omitted.
- Carry the `### Failure Cause Mapping` table directly into the final page.
- Move the source-mapping table into the Source Reference Appendix.
- Foreground the naming asymmetry (`param_to_param` ↔ `global_to_param`) and the `buffer_memory_variable_pointers` capability caveat in `Behavior Parameters` and `Key Takeaways`.
- The relevant Vulkan spec chapters were not present locally under `external/vulkan-docs/`; the brief is grounded in the inspected SPIR-V assembly and the capability/extension declarations visible in the C++ source, which are authoritative for this test.
