# Understanding Brief: `SpirvVersionTests`

## One-Sentence Test Purpose

This family checks that CTS can request SPIR-V versions `1.0` through `1.6` for a compute or selected graphics stage, that every compiled module reports exactly that version, and that the resulting shader still completes its ordinary compute or graphics check.

## Background Knowledge

### SPIR-V module version and shader build options

A SPIR-V binary begins with a header whose version word identifies the SPIR-V version. CTS creates `SpirVAsmBuildOptions` with the requested `SpirvVersion`; `extractSpirvVersion()` reads the compiled binary back. Comparing those two values checks the build path, rather than accepting merely a version that the device can otherwise consume.

### A graphics-stage test requires a complete pipeline

The selected graphics stage supplies the test arithmetic, but it runs in a complete graphics pipeline. Vertex and fragment choices use vertex-plus-fragment stages; either tessellation choice uses vertex, tessellation-control, tessellation-evaluation, and fragment stages; geometry uses vertex, geometry, and fragment stages. The `testfun` fragment doubles then subtracts the first component of its input, leaving that component unchanged before the common graphics helper verifies the pipeline result.

### CTS-authored SPIR-V assembly

The source builds assembly text directly. It is the authoritative shader source, not a GLSL reconstruction. The compute program loads each input float, negates it with `OpFNegate`, and stores it to an output buffer. For versions above `1.3`, it uses `StorageBuffer` and `Block`; `1.3` and earlier use `Uniform` and the legacy `BufferBlock` form.

## One Concrete Example

`dEQP-VK.spirv_assembly.instruction.compute.spirv_version.1_4_compute` requests SPIR-V `1.4`. CTS adds the authored compute assembly with `SpirVAsmBuildOptions(..., SPIRV_VERSION_1_4)`, supplies 100 positive random floats and their negatives as expected outputs, then dispatches 100 one-invocation workgroups. Before accepting the numerical output, `isSpirVersionsAsRequested()` extracts the version from every binary in the collection and requires `1.4` for each one.

## End-to-End Test Flow

```text
[registration] choose one version and either compute or one graphics operation
[program setup] attach CTS-authored assembly with build options for that requested version
[compile] CTS produces one compute module or the modules needed by the selected graphics pipeline
[version check] extract the version from every compiled binary and compare it to the request
[execute] compute negates 100 floats, or graphics runs the common default pipeline verifier
[result] fail immediately on a version mismatch; otherwise return the ordinary execution result
```

## Generated Test Artifacts and Bound Resources

### Generated program artifacts

- The generator forms `1_0` through `1_6` from the `SpirvVersion` enumeration and appends an operation name.
- Compute uses one authored assembly string with `%indata` at set 0/binding 0 and `%outdata` at set 0/binding 1.
- A graphics case uses the common graphics assembly builders. The selected stage receives the custom `testfun`; the other stages provide the pipeline context needed to execute it.
- The source changes the compute buffer storage/decorations at the `1.3`/`1.4` boundary and supplies `GL_entrypoint` to the graphics builder above `1.3`.

### Bound resources

| Resource or artifact | Host setup | Device use | Host check | Purpose |
|----------------------|------------|------------|------------|---------|
| Compute input buffer | 100 deterministic positive floats | Read at binding 0 | No | Supplies values for `OpFNegate`. |
| Compute output buffer | Expected negative floats | Written at binding 1 | Yes | Lets the common compute harness verify arithmetic execution. |
| Graphics pipeline stages | Common helper creates the required stage set | Executes selected custom stage | Yes, through common verifier | Makes the selected graphics-stage module executable. |
| `BinaryCollection` | Filled by CTS compilation | Not a device resource | Yes | Supplies every compiled module for the version-header check. |

## What Is Checked

- `isSpirVersionsAsRequested()` requires a non-empty binary collection and compares the extracted version of **every** binary to the requested version.
- Compute cases perform that comparison, then delegate to `SpvAsmComputeShaderInstance::iterate()`, whose expected output is the negation of each of the 100 inputs.
- Graphics cases perform the same comparison, then delegate to `runAndVerifyDefaultPipeline()`; this source does not implement a separate graphics oracle.
- A version mismatch returns `"Binary SPIR-V version is different from requested"` before the ordinary execution check.

## Behavior Parameter Identification

> **Behavior parameter:** requested SPIR-V version
>
> **Candidate values:** `1_0`, `1_1`, `1_2`, `1_3`, `1_4`, `1_5`, `1_6`

The version is the primary behavioral axis: it is passed directly to `SpirVAsmBuildOptions` and is the value checked in every compiled binary. Operation/stage is a secondary dimension that chooses compute versus a graphics-stage execution path.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `1_0`, `1_1`, `1_2`, or `1_3` | Requested-version propagation or SPIR-V-header generation is wrong; the legacy compute buffer declaration path may also be implicated for compute. |
| `1_4`, `1_5`, or `1_6` | Requested-version propagation or SPIR-V-header generation is wrong; the newer compute storage-buffer/interface path may also be implicated for compute. |
| Any version only for `compute` | Compute assembly construction, binary collection contents, or the common compute execution path is wrong. |
| Any version only for one graphics operation | The selected graphics-stage builder, its pipeline composition, or the common graphics verifier is wrong. |
| Many versions and operations | Shared assembly compilation/build-option propagation or version extraction is wrong. |

## Important Variations and Special Cases

- The registration loop has 7 versions. The compute root selects one operation, so it has `7 × 1 = 7` leaves. The graphics root selects five non-compute operations, so it has `7 × 5 = 35` leaves. Each `vk-default/spirv-assembly.txt` and `vksc-default/spirv-assembly.txt` list contains all 42 corresponding paths under its own prefix.
- Tessellation-control and tessellation-evaluation leaves are not supported without `tessellationShader`; geometry leaves are not supported without `geometryShader`.
- Any requested version higher than `getMaxSpirvVersionForAsm(context.getUsedApiVersion())` is not supported. This is a runtime support decision, not removal from the registered matrix.
- Registration is not wrapped in a `CTS_USES_VULKANSC` exclusion. The observed standard and Vulkan SC mustpass lists both include the 7 compute and 35 graphics leaves.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Root registration | [`vktSpvAsmInstructionTests.cpp#L21319-L21320` and `#L21452-L21453`](../../../modules/vulkan/spirv_assembly/vktSpvAsmInstructionTests.cpp#L21319-L21320) | Adds the family below compute and graphics instruction roots. |
| Authored compute assembly | [`getComputeSourceCode()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L118-L154) | Shows the version-dependent buffer declarations and `OpFNegate` program. |
| Version comparison | [`isSpirVersionsAsRequested()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L182-L198) | Reads and compares every compiled binary version. |
| Runtime and support handling | [`iterate()`, `checkSupport()`, and `initPrograms()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L217-L355) | Establishes check ordering, support gates, and version-specific build options. |
| Leaf generator | [`createSpivVersionCheckTests()`](../../../modules/vulkan/spirv_assembly/vktSpvAsmSpirvVersionTests.cpp#L376-L403) | Defines all exact version/operation names. |
| Compute helper semantics | [`vktSpvAsmComputeShaderTestUtil.cpp#L33-L61`](../../../modules/vulkan/spirv_assembly/vktSpvAsmComputeShaderTestUtil.cpp#L33-L61) | Defines the epsilon-based float output comparison used by the common compute harness. |

## Conversion Notes for Final Wiki Rewrite

Preserve the behavior labels and the failure-cause mapping table exactly. The final page should use `1_4_compute` as the representative CTS-authored assembly, retain the source's `tesselation_*` identifiers, distinguish binary-version checking from the follow-on arithmetic/pipeline check, and reconcile the `7 + 35 = 42` mustpass matrix.
