# Shader Analyzer Annotation Examples and Review Cues

## Declaration annotation examples

Place compact resource facts near declarations after reconstructing the complete shader or stage set.

```glsl
/// Binding 0 is an r32ui storage image whose extent matches the generated invocation grid; each texel stores
/// one payload value that must become visible through the selected synchronization chain.
layout(set=0, binding=0, r32ui) uniform nonprivate uimage2D payload;
```

```glsl
/// Binding 0 is the only host-created GPU resource in this case: a std140 storage buffer containing one uint
/// pass counter. The shader increments it only if every generated shared-memory field check succeeds.
layout(std140, binding = 0) buffer block { highp uint passed; };
```

```glsl
/// These generated shared objects live in workgroup shared memory. Their nested structs, arrays, and 16-bit
/// fields are the layout/access data being tested.
shared sG s1;
shared sN s2;
shared sAL s3;
```

## Annotation review cues

Keep comments compact and source-grounded. Before finalizing the walkthrough, verify that comments expose the facts a reader
cannot safely infer from syntax alone:

- execution shape and runtime knobs;
- shader-visible interface and resource roles;
- host-created resource versus shader-local status;
- binding, location, format or type, and size or extent rules;
- data layout, addressing, or stage-to-stage mapping;
- synchronization, ordering, availability, visibility, and scope semantics;
- validation and failure recording;
- generated-code artifacts or variant-sensitive branches.

Preserve source-generated `//` comments. Add concise wiki-authored `///` comments only after the full shader structure is known.

## Additional Info filter

Use `#### Additional Info` only for facts needed to interpret the exact reconstructed case that do not fit naturally in the parameter,
structural-design, inline-comment, variation-summary, or page-level runtime/pruning content. Strong candidates include:

- evidence for a non-obvious generator branch;
- a nonlocal host/runtime fact needed to interpret the shader;
- an exact-case feature assumption or caveat;
- a deterministic-generation or readability-normalization note;
- the required role/variation note for each non-primary shader in a multi-shader walkthrough.

Do not repeat parameter meanings, declaration comments, source inventory, generic CTS mechanics, or SPIR-V generation details.

## Reconstruction failure audit

When the owning workflow routes a `shader-disassembler` failure back to reconstruction, compare the reconstructed GLSL or HLSL
against actual generator behavior. Recheck:

- non-local helpers and generated-code/declaration printers;
- source-language flags and entry points;
- declarations, extensions, and extension emission;
- type aliases and precision qualifiers;
- feature gates and variant branches;
- literal generation and casts;
- comparison and generated validation helpers.

Do not accept the failure as final until this source-grounded audit is complete.
