## Overview

The `graphicsfuzz` test category runs an Amber-backed corpus of GraphicsFuzz shader tests. Each registered test loads one Amber script, applies the requirements declared for that case, executes its Vulkan recipe, and reports the script's result.

## Background Knowledge

- **Amber scripts.** Amber is a small test language that describes shader inputs, pipelines, resources, commands, and expectations. The CTS parses a script into an Amber recipe before execution, so the registered name identifies a script-driven case rather than a C++ test body.
- **Shader differential testing.** GraphicsFuzz cases can preserve a reference shader or pipeline and compare it with a transformed or repaired variant. A framebuffer comparison checks that the transformation kept the observable result for the inputs selected by the script.
- **Requirement-based support.** A case may declare extensions, features, properties, image requirements, or buffer-format requirements. The runner checks these before executing the recipe; unsupported cases are pruned instead of being treated as rendering failures.

## Category Structure

```text
graphicsfuzz
├── cov-access-array-dot (580 coverage-oriented cases in total)
├── spv-access-chains (32 SPIR-V comparison cases in total)
├── stable-binarysearch-tree-false-if-discard-loop (23 stable comparison cases in total)
└── access-new-vector-inside-if-condition (122 other focused bug reproducers in total)
```

The four tree entries are representative names, not additional registered test families. The complete direct-child set has 757 generated leaves: 580 `cov-*`, 32 `spv-*`, 23 `stable-*`, and 122 other names. Their exact names are maintained in [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) and mirrored by [`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757).

## How the Families Fit Together

The name families group the corpus by test origin or comparison style rather than by separate C++ registration branches.

- `cov-*` cases target compiler and optimizer coverage points.
- `spv-*` and `stable-*` cases focus on SPIR-V or stable reference-versus-variant comparisons.
- The remaining names identify focused shader and control-flow reproducers.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| All registered GraphicsFuzz test cases | [AmberTests.md](../testfiles/graphicsfuzz/AmberTests.md) | Index-driven registration, per-case requirements, Amber execution, and script-defined checking |

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Case count | 757 direct test cases | Selects one index entry and one Amber script. | [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) |
| Index metadata | Filename, registered test name, description | Connects the registered leaf to its archived script and reader-facing case description. | [`AmberIndexFileParser::parse()`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169) |
| Optional requirements | Per-case extension, feature, property, image, and buffer requirements | Determines whether the case is supported before execution. | [`AmberIndexFileParser::parse()`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L149-L163), [`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286) |
| Corpus themes | `cov-*`, `spv-*`, `stable-*`, and direct control-flow or shader cases | Identifies common origins or comparison styles in the data; it does not create nested registered families. | [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L21-L40) |

## Behavior Parameters

The primary behavioral axis is the registered test case leaf. Each leaf selects a different Amber script and therefore a different shader transformation, control-flow shape, resource setup, or expected result. The C++ wrapper does not reinterpret these leaves as a second parameter matrix.

### `cov-*` cases: compiler and optimizer coverage

These scripts target shader-language, compiler, optimizer, or backend paths. Their expected result is whatever the individual Amber recipe declares; the `cov-` prefix is corpus metadata, not a shared pass condition.

### `spv-*` and `stable-*` cases: representation and transformation comparisons

These scripts commonly compare a reference and variant recipe or exercise SPIR-V-oriented transformations. The comparison operator and expected buffers belong to the script, so failures mean that the particular case's observable contract was not met.

### Other registered leaves: focused shader reproductions

The remaining names identify focused control-flow, arithmetic, data-flow, and shader-language reproductions. Their mechanism and expectation come from the referenced Amber file, not from a common C++ implementation branch.

## Shader Analysis

The category contains many shaders, but no single generated CTS shader path represents the corpus. The C++ wrapper passes each script to Amber, and the scripts supply the individual shader sources or SPIR-V artifacts. This page therefore does not claim a representative walkthrough for the whole category; inspect the exact Amber file named by an index entry when a single case needs shader-level analysis.

## Runtime Execution and Result Checking

- [`createGraphicsFuzzTests()`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L46-L49) creates the `graphicsfuzz` group and invokes the shared index parser. The parser constructs one `AmberTestCase` per entry and stores its script path, name, description, and optional requirements.
- The test case parses the archived Amber script into a recipe during delayed initialization. Parse failure is an internal test error, because the registered case does not have an executable recipe.
- Before execution, CTS checks the index-declared extensions, features, properties, image requirements, and buffer requirements. Amber also checks the requirements declared inside the recipe; CTS verifies that the two requirement sets agree.
- The Amber runner executes the recipe through its Vulkan engine. It supplies compiled shader binaries when the CTS build produced them, then returns pass when Amber reports success and fail when Amber reports an execution or expectation error.
- Script-level expectations determine the observable contract. Inspected cases use direct color expectations and framebuffer comparisons such as `EQ_HISTOGRAM_EMD_BUFFER`; the C++ wrapper does not replace those expectations with one category-wide image oracle.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `cov-*` case | The targeted shader/compiler behavior, Amber setup, or declared expectation produced an unexpected result. |
| `spv-*` or `stable-*` case | The reference/variant transformation or its Vulkan execution produced an observable mismatch under the script's comparator. |
| Other registered leaf | The selected Amber recipe failed to parse, execute, or satisfy its own expectation. |

A common failure cause is an inconsistent CTS-versus-Amber requirement declaration; `validateRequirements()` reports that mismatch before accepting the case's support model.

### Cause Analysis

#### Script parse or recipe construction

**Possible failure symptoms:** CTS reports that the Amber source could not be parsed or that the case has no executable recipe.

**Possible implementation causes:** The archived script may be malformed for the Amber parser, or the CTS archive may not provide the file named by the index entry. The source checks the script result in [`AmberTestCase::parse()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432).

#### Unsupported declared requirement

**Possible failure symptoms:** The case is reported unsupported before the recipe runs, or CTS detects a mismatch between its requirements and Amber's requirements.

**Possible implementation causes:** The selected physical device may lack an extension, feature, property, image capability, or buffer format required by the case. The page cannot localize a later driver defect from this pruning result; the relevant support check is [`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286).

#### Shader, pipeline, or resource expectation

**Possible failure symptoms:** Amber executes the recipe but a direct expectation or reference-versus-variant comparison fails.

**Possible implementation causes:** The failure may arise in shader compilation or lowering, resource setup, Vulkan execution, synchronization, or the specific script comparator. The exact cause depends on the selected Amber file; the runner only records Amber's success or error result in [`AmberTestInstance::iterate()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615).

## Case Pruning

### Requirement-based pruning

- The index can require instance or device extensions. CTS rejects a case when those extensions are unavailable.
- Feature, property, image, and buffer-format requirements are checked before execution. Cases that lack required support do not produce a shader correctness result.
- CTS and Amber requirement sets must agree; a mismatch is reported rather than silently widening or narrowing support.

### Design-based pruning

The index is the corpus boundary. Prefixes such as `cov-`, `spv-`, and `stable-` organize case provenance and intent, but they do not imply omitted cross-products. Each listed script is an intentional standalone case.

## Key Takeaways

- The C++ category implementation is a loader; the Amber index and scripts define the 757 executable cases.
- Requirements are checked per case, so unsupported device capabilities prune individual leaves rather than the whole category.
- Pass/fail semantics come from each script's expectations. A category-level count or wrapper result cannot replace the case-specific framebuffer, buffer, or other observable check.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Category factory | [`createGraphicsFuzzTests()`](../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L46-L49) | Creates the root and loads `index.txt`. |
| Index parser | [`createAmberTestsFromIndexFile()`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L175-L189) | Adds one registered Amber case for each parsed entry. |
| Index entry parser | [`AmberIndexFileParser::parse()`](../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169) | Reads script filename, registered name, description, and requirements. |
| Support checks | [`AmberTestCase::checkSupport()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286) | Checks extensions, features, properties, images, and buffers. |
| Requirement consistency | [`AmberTestCase::validateRequirements()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L648-L707) | Compares CTS and Amber requirement declarations. |
| Amber parsing | [`AmberTestCase::parse()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432) | Builds the executable Amber recipe. |
| Amber execution | [`AmberTestInstance::iterate()`](../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615) | Executes the recipe and maps the result to CTS pass/fail. |
| Corpus index | [`index.txt`](../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757) | Defines the registered GraphicsFuzz cases and their metadata. |
| Mustpass coverage | [`graphicsfuzz.txt`](../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) | Lists the 757 default Vulkan registered paths. |
