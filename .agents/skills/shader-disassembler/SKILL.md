---
name: shader-disassembler
description: Compiles one reconstructed Vulkan CTS GLSL or HLSL shader with glslangValidator for a deterministic CTS SPIR-V target version, validates the resulting SPIR-V with spirv-val using the same SPIR-V environment, disassembles it with spirv-dis, and returns wiki-ready full SPIR-V assembly in a collapsed details block. This skill should be used by shader-analyzer after reconstructed shader source, source language, shader stage, target SPIR-V environment, and output destination are known.
---

# Shader Disassembler

Generate deterministic, compiler-produced SPIR-V assembly from one reconstructed GLSL or HLSL shader using the CCVDO workflow:

```text
Check -> Compile -> Validate -> Disassemble -> Output
```

Keep the scope narrow. Use only these tools:

- `glslangValidator`
- `spirv-val`
- `spirv-dis`

Do not use alternative compilers, online tools, CTS-internal build products, LLM-generated SPIR-V, hand-written SPIR-V, or selected manual assembly excerpts.

## When To Use This Skill

Use this skill when a wiki workflow needs SPIR-V assembly for a reconstructed GLSL or HLSL shader, especially when called by
`shader-analyzer` for the final `#### SPIR-V` subsection of a Representative Shader Walkthrough.

Require the caller to provide:

- the exact reconstructed shader source;
- the shader source language: `GLSL` or `HLSL`;
- the shader stage for `glslangValidator -S`, such as `comp`, `vert`, `frag`, `geom`, `tesc`, or `tese`;
- the CTS target SPIR-V environment, such as `spirv1.0`, `spirv1.3`, `spirv1.4`, `spirv1.5`, or `spirv1.6`;
- the intended `#### SPIR-V` output destination or enough context to return a markdown block to the caller.

## Output Contract

This skill owns the complete `#### SPIR-V` subsection. The caller must insert the returned subsection unchanged.

The shapes in step 5 are exact. Do not rename, reorder, add, or replace fields with prose. Do not add build commands, validation
commands, header summaries, `Bound`, or CTS enum notes. Successful output always contains the full unmodified disassembly.

## CCVDO Workflow

### 1. Check

Check that all three required tools are available before generating any artifact:

```bash
glslangValidator -v
spirv-val --version
spirv-dis --version
```

If any tool is missing:

- stop immediately;
- report `Status: skipped`;
- state that `glslangValidator`, `spirv-val`, and `spirv-dis` are required;
- give minimal install guidance:

```txt
At least one of `glslangValidator`, `spirv-val`, and `spirv-dis` is not available.
For most platforms, install the official Vulkan SDK from <https://vulkan.lunarg.com/sdk/home>
For AIBook (ARM64) with Vulkan SDK tarball unavailable, use `sudo apt install glslang-tools spirv-tools`.
```

### 2. Compile

Write the shader source to a temporary file only when a physical file is needed by `glslangValidator`.

Use `glslangValidator` with explicit stage and target SPIR-V environment.

For GLSL:

```bash
glslangValidator -V --target-env <spirv-env> -S <stage> -o <temp>.spv <temp>.<stage>
```

For HLSL:

```bash
glslangValidator -D -V --target-env <spirv-env> -S <stage> -e <entrypoint> -o <temp>.spv <temp>.<stage>.hlsl
```

Filename and stage conventions:

- `glslangValidator` recognizes bare stage suffixes such as `.vert`, `.geom`, `.frag`, and `.comp` for GLSL-style stage
  classification. Using `<temp>.<stage>` is the simple GLSL convention used by this workflow.
- `glslangValidator` also recognizes compound HLSL suffixes such as `.vert.hlsl`, `.geom.hlsl`, `.frag.hlsl`, and `.comp.hlsl`.
  The final `.hlsl` suffix identifies the source language, while the preceding stage suffix identifies the shader stage.
- For reconstructed HLSL, prefer a compound temporary filename `<temp>.<stage>.hlsl`. This lets the filename itself document both
  source language and stage, and it matches the convention shown by `glslangValidator --help`.
- Still pass `-D` and `-S <stage>` explicitly for deterministic workflow behavior. `-D` makes HLSL input explicit even if the file
  suffix is changed later, and `-S <stage>` prevents accidental stage inference from a nonstandard temporary filename.
- Pass `-e main` unless CTS source or the reconstructed shader proves a different entry point.
- Use HLSL source as reconstructed from CTS, without translating it to GLSL.

Common rules:

- derive `<stage>` from the provided shader stage, not from guesswork;
- derive `<spirv-env>` from the CTS source-controlled shader build options supplied by `shader-analyzer`;
- use a SPIR-V environment such as `spirv1.0` or `spirv1.3`, not a Vulkan environment such as `vulkan1.1`;
- preserve the shader source exactly as provided;
- do not strip `///` comments before compile; GLSL and HLSL line comments are legal and harmless;
- capture compiler diagnostics.

If compilation fails:

- stop before validation/disassembly;
- report `Status: failed`;
- include concise diagnostics;
- remove any temporary files created;
- do not synthesize SPIR-V output.

### 3. Validate

Validate the generated SPIR-V binary with `spirv-val` using the matching SPIR-V validation environment:

```bash
spirv-val --target-env <spv-env> <temp>.spv
```

Rules:

- map the compile environment spelling to the `spirv-val` spelling, for example `spirv1.0` -> `spv1.0` and `spirv1.3` -> `spv1.3`;
- do not introduce a Vulkan target environment for validation unless the caller explicitly asks for a separate diagnostic run;
- the normal wiki output is generated from the deterministic SPIR-V target environment only.

If validation fails:

- report `Status: failed`;
- include concise validation diagnostics;
- remove temporary files after capturing diagnostics;
- do not emit disassembly as valid wiki output unless explicitly asked for debugging.

### 4. Disassemble

Disassemble only a successfully validated SPIR-V binary:

```bash
spirv-dis <temp>.spv -o <temp>.spvasm
```

Preserve the full output exactly. Do not annotate or edit instructions, IDs, headers, capabilities, decorations, or comments.

Require the assembly `; Version:` header to match `<spirv-env>`. On mismatch, report `Status: failed`; do not edit the header or
present the assembly as successful output.

### 5. Output

Return exactly one of these complete `#### SPIR-V` shapes.

Generated output shape:

````markdown
#### SPIR-V

- Status: generated and validated
- Source: reconstructed `<GLSL or HLSL>` from this walkthrough
- Stage: `<stage>`
- Target SPIRV version: `<spirv-env>`

<details>
<summary>Click to expand SPIRV asm code</summary>

```llvm
<full spirv-dis output>
```

</details>
````

Failure output shape:

```markdown
#### SPIR-V

- Status: failed
- Source: reconstructed `<GLSL or HLSL>` from this walkthrough
- Stage: `<stage>`
- Target SPIRV version: `<spirv-env>`
- Diagnostics: `<concise compiler or validator diagnostic>`
```

Skipped output shape for missing tools:

```markdown
#### SPIR-V

- Status: skipped
- Required tools: `glslangValidator`, `spirv-val`, `spirv-dis`
- Install: install the official Vulkan SDK from LunarG/Khronos; on AIBook / ARM64, use `sudo apt install glslang-tools spirv-tools`.
```

## Artifact Cleanup

Remove temporary generation artifacts after output is captured:

- temporary shader source file created for compilation;
- `.spv` binary;
- `.spvasm` disassembly file;
- temporary logs created to track command status.

Do not delete source wiki pages, committed examples, or user-provided shader files.

## TEMP-SPIRV-ASSEMBLY: spirv_assembly Category Deviation

> **TEMPORARY, category-scoped deviation. Revert before merging spirv_assembly to vkcts-wiki.**

For the `spirv_assembly` category only, the input is authored SPIR-V assembly text (extracted from C++ string templates by `shader-analyzer`), not reconstructed GLSL/HLSL. Apply this deviation instead of the GLSL/HLSL compile path:

### Assemble instead of compile

Replace the `glslangValidator` compile step with `spirv-as` (assembly text → SPIR-V binary):

```bash
spirv-as --target-env <spirv-env> -o <temp>.spv <temp>.spvasm
```

Rules:
- input is the extracted SPIR-V assembly text from `shader-analyzer`;
- derive `<spirv-env>` from the CTS source-controlled shader build options (same rule as the GLSL/HLSL path);
- use a SPIR-V environment such as `spirv1.0` or `spirv1.3`, not a Vulkan environment such as `vulkan1.1`;
- preserve the assembly text exactly as provided;
- capture assembler diagnostics.

If assembly fails:
- stop before validation/disassembly;
- report `Status: failed`;
- include concise diagnostics;
- remove any temporary files created;
- do not synthesize SPIR-V output.

### Validation gate, not published output

Continue with `spirv-val` and `spirv-dis` as in the standard CCVDO workflow. The round-trip (`spirv-as` → `spirv-val` → `spirv-dis`) serves as a **generation-time validation gate** on the LLM-extracted assembly (Decision 1):
- `spirv-as` catches syntax/transcription errors;
- `spirv-val` catches semantic violations against the target SPIR-V environment;
- if either fails, `shader-analyzer` must re-extract before the page ships.

The disassembled output is **NOT** published as a `#### SPIR-V` subsection (Decision 2). The extracted SPIR-V assembly is placed once under `#### Source Code` by `shader-analyzer`. The `#### SPIR-V` subsection is omitted for this category. Do not return the standard `#### SPIR-V` output shape; return only a pass/fail validation result to `shader-analyzer`.

### Amber-backed pages (Batch 9) — not this skill

Amber-backed pages in Batch 9 do not invoke this skill. Their SPIR-V assembly is literal CTS test data extracted verbatim from Amber scripts; no `spirv-as` validation gate applies.

## Boundary With Shader Analyzer

Let `shader-analyzer` reconstruct the shader and choose the CTS target. This skill compiles, validates, disassembles, and returns the
canonical SPIR-V subsection. Do not reinterpret test semantics or the target environment.
