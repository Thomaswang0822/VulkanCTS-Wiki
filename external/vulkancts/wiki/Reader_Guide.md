# Vulkan CTS Wiki Reader Guide

This guide explains how to read the Vulkan CTS wiki efficiently. It focuses on how the wiki pages are organized, what each
recurring section is meant to answer, and how to move from category-level navigation to source-backed technical details.

For background on Vulkan CTS itself, including registration, execution, verification, result codes, mustpass files, and Vulkan SC,
read [CTS_Framework.md](CTS_Framework.md). This guide is about how to use the wiki
pages.

## What This Wiki Is For

The wiki is a source-backed reading layer over Vulkan CTS tests. It is designed to help readers understand:

- what a Vulkan CTS test category or test family verifies;
- how test cases are registered and named;
- which parameter dimensions, generated variants, or intermediate nodes matter;
- how execution, resource setup, shader behavior, and result checking work;
- what a failure usually means;
- where to inspect source and mustpass evidence after understanding the explanation.

The intended reading path is explanation first, source evidence second. Source links remain important, but they should support the
technical explanation rather than replace it.

## Page Types and Reading Flow

| Page type | Where it lives | What it answers | When to read it |
|-----------|----------------|-----------------|-----------------|
| Entry page | [README.md](README.md) | What top-level categories and wiki areas exist? | Start here when you do not know the target category. |
| Reader guide | [Reader_Guide.md](Reader_Guide.md) | How should the rewritten wiki pages be used? | Read when you want the page structure and terminology contract. |
| Framework background | [CTS_Framework.md](CTS_Framework.md) | How does Vulkan CTS registration, execution, and result reporting work? | Read when CTS internals are unfamiliar. |
| Level-2 category pages | [categories/](categories/) | What does one top-level test category cover, and which Level-3 page should I open? | Read when you know the category name. |
| Level-3 testfile pages | [testfiles/](testfiles/) | What do specific test families, generated cases, parameters, resources, shaders, and checks do? | Read when you need technical test behavior. |
| Source and mustpass links | Inline links and appendices | Which repository evidence supports the explanation? | Use for audit, debugging, or source-level follow-up. |

Typical reading flow:

```text
README
  -> Level-2 category page
     -> Level-3 testfile page
        -> Source Reference Appendix
           -> source or mustpass evidence
```

## If You Have a Specific Goal

| Reader goal | Start here | Then read |
|-------------|------------|-----------|
| Understand what a category covers | Level-2 `Overview` | `How the Families Fit Together` |
| Find which page explains a test family | Level-2 `Category Structure` | `Level-3 Pages Navigation` |
| Understand what one test family verifies | Level-3 `Overview` | `Behavior Parameters` |
| Decode a generated test path | Level-3 `Registration Hierarchy` | `Parameter Dimensions and Observed Values` |
| Understand generated shader behavior | Level-3 `Shader Analysis` | `Runtime Execution and Result Checking` |
| Understand host-side execution and pass/fail logic | Level-3 `Runtime Execution and Result Checking` | `Key Takeaways` |
| Understand what a failure means and what could cause it | Level-3 `Failure Meaning` | `Cause Analysis` subsections within it |
| Understand why cases are unsupported, skipped, or absent | Level-3 `Case Pruning` | Source links in that section or the appendix |
| Audit a wiki claim against source | Nearby inline source link | `Source Reference Appendix` |

## How to Read Level-2 Category Pages

Level-2 pages under [categories/](categories/) are compact category gateways. They are not intended to duplicate all technical
details from Level-3 pages.

| Section | What readers get from it |
|---------|--------------------------|
| `Overview` | The shared testing theme of the category. |
| `Category Structure` | The direct registered test families under the category. |
| `How the Families Fit Together` | A short comparison of why the families belong together and how they differ. |
| `Level-3 Pages Navigation` | A routing table from registered families, intermediate nodes, or conceptual areas to Level-3 pages. |
| `Category Notes` | Optional category-level caveats, such as unusual naming or page mapping. |

Use a Level-2 page when you need to decide where to go next. For example, [memory_model.md](categories/memory_model.md) explains
that `message_passing`, `write_after_read`, and `transitive` are covered by
[vktMemoryModelMessagePassing.md](testfiles/memory_model/vktMemoryModelMessagePassing.md), while `padding` and `shared` have their
own Level-3 pages.

## How to Read Level-3 Testfile Pages

Level-3 pages under [testfiles/](testfiles/) provide the technical explanation for one implementation-bearing source file, one test
family, or a closely related set of test families.

| Section | What readers get from it |
|---------|--------------------------|
| `Overview` | The core correctness question and page scope. |
| `Background Knowledge` | Only the prerequisite concepts needed for this page. |
| `Registration Hierarchy` | Where the documented behavior sits in CTS registered paths. |
| `Parameter Dimensions and Observed Values` | What important path components or generated values change in behavior. |
| `Behavior Parameters` | The primary behavioral axis — which registered parameter most directly controls test behavior, and how each value changes what is tested. |
| `Shader Analysis` | Representative generated shader structure, data flow, synchronization, important variants, and collapsed SPIR-V assembly generated from the reconstructed GLSL when a walkthrough is present. |
| `Runtime Execution and Result Checking` | Host-side setup, dispatch/draw/submit behavior, readback, and pass/fail decision. |
| `Failure Meaning` | What a failure of this test means: a mapping from behavior parameter values to possible failure causes, and a detailed analysis of each cause. |
| `Case Pruning` | Why possible cases are unsupported, invalid, redundant, or intentionally not generated. |
| `Key Takeaways` | Page-specific conclusions about what the test proves and which design choices are central. |
| `Source Reference Appendix` | Source and mustpass entry points for audit or deeper study. |

Not every page expands every section equally. Shader-heavy pages should have stronger shader analysis; resource-heavy pages should
explain buffers, images, descriptors, memory bindings, attachments, or copyback paths; simple fixed-case pages may keep several
sections short. When a representative shader walkthrough is present, its `SPIR-V` subsection is a collapsed audit artifact: read it
when you need compiler-produced assembly evidence, not as the primary explanation path.

## Requesting Additional Shader Analysis

Each Level-3 page includes at most three representative shader walkthroughs. If you need a walkthrough for a different CTS case
or shader stage not covered by the page, you can request one. The `shader-analyzer` skill reconstructs the exact generated GLSL or
HLSL for any registered CTS path by walking the source-controlled shader generator, and the `shader-disassembler` skill compiles,
validates, and disassembles the result into SPIR-V assembly.

Requested walkthroughs are written to a sidecar file next to the Level-3 page:

```text
external/vulkancts/wiki/testfiles/<category>/<Level3Page>_shader_analysis.md
```

To request a walkthrough, provide the exact CTS path and the target Level-3 page. For example (replace [contents] accordingly):

```text
Apply `shader-analyzer` skill on [dEQP-VK.memory_model.message_passing.ext.u32.noncoherent.atomic_atomic.atomicwrite.subgroup.payload_nonlocal.buffer.guard_nonlocal.buffer.comp].

Write the walkthrough to the sidecar for [testfiles/memory_model/MessagePassing.md].
```
 
The analysis follows the same output contract as the walkthroughs already embedded in wiki pages: parameter values, purpose,
structural design, annotated shader code, variation summary, and collapsed SPIR-V assembly.

## Terminology Used by This Wiki

The wiki uses hierarchy terms consistently so that source-code framework terminology does not obscure reader-facing structure.

| Term | Meaning | Example |
|------|---------|---------|
| `test category` | A Level-2 top-level registered path component. | `memory_model` |
| `test family` | A Level-3 page-scope or direct category child. | `message_passing`, `shared`, `padding` |
| `intermediate node` | A registered path component below a test family. | `16bit`, `arrays_of_arrays` |
| `test case leaf` | The final executable CTS path component. | `3` in `memory_model.shared.16bit.arrays_of_arrays.3` |
| `mustpass path` | A concrete CTS path listed in mustpass files. | `dEQP-VK.memory_model.padding.test` |
| `source evidence` | Code or mustpass links used to support a wiki claim. | Links in inline citations and source appendices. |

Use `node` only for intermediate path components below a test family. Do not read `node` as a synonym for a top-level test category
or a Level-3 test family. CTS source code may use broad framework terms such as test group recursively; wiki prose avoids that term
unless it is quoting or explaining framework internals.

## How to Use Source Links

Source links serve different purposes depending on where they appear. Readers usually do not need to open these files for normal
use; the wiki page should summarize the relevant behavior. The links are primarily an audit trail for readers who need to verify
or update a claim.

| Evidence Kind | Repository Location | Meaning |
|---------------|---------------------|---------|
| Vulkan CTS source implementation | [`external/vulkancts/modules/`](../modules/) | C++, shader-generation, and helper code that implements the tests. |
| Default Vulkan mustpass lists | [`external/vulkancts/mustpass/main/vk-default/`](../mustpass/main/vk-default/) | Registered `dEQP-VK...` paths used by default Vulkan conformance runs. |

Use source and mustpass links as follows:

- Inline source links support the local claim being made in the sentence or bullet.
- Section tables use source links to show where parameters, generated values, support checks, or validation logic come from.
- `Source Reference Appendix` links provide entry points after the reader already understands the test behavior.
- Mustpass links show concrete registered test paths used by conformance runs.

When wiki prose and source evidence appear to disagree, current source and mustpass evidence are authoritative. The wiki should be
updated to match the repository evidence.

## Reading Example: `memory_model`

Suppose you need to understand a particular test case with path:

```text
dEQP-VK.memory_model.message_passing.ext.u32.noncoherent.atomic_atomic.atomicwrite.subgroup.payload_nonlocal.buffer.guard_nonlocal.buffer.comp
```

A practical reading path is:

1. Open [memory_model.md](categories/memory_model.md) to identify the category theme and the relevant Level-3 page.
2. Follow the navigation row for `message_passing`, `write_after_read`, and `transitive` to
   [vktMemoryModelMessagePassing.md](testfiles/memory_model/vktMemoryModelMessagePassing.md).
3. Read the Level-3 `Overview` and `Behavior Parameters` sections to understand how `message_passing`, `write_after_read`, and `transitive` differ.
4. Use `Parameter Dimensions and Observed Values` to decode path components such as `ext`, `noncoherent`, `atomic_atomic`,
   `subgroup`, payload storage, guard storage, and shader stage.
5. Read `Shader Analysis` for the representative payload/guard protocol, variant summary, and collapsed SPIR-V evidence if needed.
6. Read `Runtime Execution and Result Checking` to understand how shader-detected failures become CTS failures.
7. Use `Source Reference Appendix` only when you need implementation entry points for audit or debugging.

## What This Wiki Does Not Do

- It does not replace the Vulkan specification.
- It does not replace source-code audit when exact implementation behavior matters.
- It does not provide a full walkthrough for every generated case when a representative example plus variation summary is clearer.
- It does not list every helper object, wrapper, or boilerplate source location.
- It does not treat source-file inventory as the main reading path.
