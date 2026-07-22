# Rewritten-Page Professor Review Protocol

Load this reference when auditing rewritten Level-2 or Level-3 Vulkan CTS wiki pages.

## Review Objective

Reduce human review burden. Find and correct meaningful technical or explanatory defects without turning the audit into another rewrite or presenting the reviewer’s full reasoning to the user.

Treat existing rewritten pages as generally strong. Do not optimize prose merely because an alternative is possible.

## Target Reader

Review for a graphics/GPU-literate technical reader who:

- understands general graphics and compute pipeline concepts, GPU execution, shaders, buffers, images, and synchronization at a conceptual level;
- knows Vulkan is an explicit graphics and compute API, but may have little or no experience writing substantial raw Vulkan programs;
- does not necessarily know Vulkan-specific objects, commands, flags, feature gates, memory and synchronization semantics, extension behavior, or CTS framework conventions;
- can follow a brief, page-specific explanation of an unfamiliar Vulkan concept without needing a general Vulkan tutorial.

Do not target a reader who has never encountered graphics APIs. Do not assume a Vulkan expert who will open the specification or source code to supply missing explanations.

Require the page to explain Vulkan-specific concepts that are necessary to understand what the test does, what changes across cases, how results are checked, or what failure means. Keep those explanations local and proportional; do not expand the page into a general introduction to Vulkan.

## Professor Model

Act as a technically expert professor reviewing an explanation-first technical paper.

Use all relevant expertise and repository evidence. Do not pretend to forget domain knowledge. Instead, distinguish:

- what is technically true and supported; and
- what the page itself explains clearly enough for the target reader defined above.

Never treat the ability to reconstruct the author’s intended meaning as proof that the author explained it.

For each load-bearing point, apply two internal tests:

1. **Truth test:** Is the point correct, properly scoped, and supported by source, registration, mustpass, validation logic, or Vulkan specification semantics as appropriate?
2. **Exposition test:** Does the page establish the point and its significance for the target reader without requiring raw-Vulkan experience, implementation-specific inference from source links, or familiarity with CTS naming patterns?

Keep these judgments internal unless needed to explain an unresolved finding.

## Meaningful-Defect Threshold

Edit or report a point only when at least one condition holds:

- a claim is false, unsupported, overstated, or incorrectly conditional;
- behavior, validation, registration, pruning, or failure meaning is materially inaccurate;
- a prerequisite needed to understand the page's core mechanism is absent or lacks the brief relevance needed to support later
  reasoning;
- Background Knowledge crosses into substantial concrete test narration or conclusions and blurs section responsibility;
- a missing causal link requires implementation-specific knowledge from outside the page;
- wording creates a plausible wrong mental model;
- a representative walkthrough misstates or obscures its coverage boundary;
- important sections conflict;
- a concrete clarity defect can be corrected without bloating the page.

Do not report or edit:

- merely non-optimal wording;
- background additions unrelated to a demonstrated prerequisite gap;
- alternative organization preferences;
- harmless repetition;
- speculative concerns without evidence;
- minor style issues already handled by language workers.

## Internal Review Worksheet

Use this worksheet transiently. Do not copy it into the audit summary.

### 1. Evidence-derived reference model

Derive a compact answer key from authoritative evidence:

```text
Test purpose:
Registered scope:
Required knowledge prerequisites:
Primary behavioral axis or groups:
Representative mechanism:
Resources and generated artifacts:
Host/device execution:
Observable result:
Pass condition:
Important variants and pruning:
Failure localization limits:
Representative walkthrough coverage boundary:
```

Scale the fields to the page. Omit irrelevant fields rather than inventing content.

### 2. Load-bearing claims

Inspect claims whose failure would change the reader’s understanding, especially:

- core purpose and scope;
- behavior parameter identification;
- parameter-to-mechanism relationships;
- resources and generated artifacts;
- execution sequence;
- validation and comparison strength;
- support requirements and pruning;
- failure symptoms and possible implementation causes;
- representative walkthrough selection and coverage.

Do not verify every sentence equally.

### 3. Knowledge prerequisite and responsibility-boundary audit

For a category audit with a rewritten Level-2 page, audit the Level-2 `## Background Knowledge` section before judging Level-3 BGK
sections. The Level-2 section is the owner for repeated category-shared prerequisites. It must either explain those shared concepts
or use the canonical Level-2 no-common-concepts sentence when no category-level prerequisite explanation is needed. When the
no-common-concepts sentence is used, Level-3 pages have no upward link and their local sufficiency is judged from the Level-3 page
alone. When shared concepts are explained, each affected Level-3 section begins with a standalone upward-link sentence naming the
shared concept; local prerequisite bullets follow that sentence, and sufficiency is judged from the Level-3 page plus the linked
Level-2 BGK. The sentence should follow the recommended canonical shape, but natural page-specific and translated wording is valid.

Derive the concepts a reader must understand before the page's behavior, walkthrough, runtime, validation, pruning, or failure
explanation becomes meaningful. Compare those prerequisites with the target-reader baseline before judging the existing
`## Background Knowledge` content.

For each prerequisite outside that baseline, verify that the page answers both:

1. **What is it?** Give the minimum accurate concept or relationship.
2. **Why is it needed?** Briefly connect the concept to the later reasoning that depends on it, without continuing into the concrete
   CTS setup, parameter values, execution, expected result, correctness contract, conclusion, or failure meaning.

An API declaration or syntax example alone does not discharge the prerequisite when its runtime consequence remains unstated. For
example, saying that a geometry shader declares `invocations = N` is insufficient for an instancing test unless the page also
explains that each input primitive launches `N` separately indexed geometry-shader executions. The concrete invocation counts,
output pattern, and image oracle for this test belong in later sections.

Classify each existing Background Knowledge item internally:

| Classification | Required action |
|---|---|
| Necessary prerequisite concept | Keep; tighten only when needed. |
| Necessary concept with brief relevance | Keep when the relevance stops before concrete case narration. |
| Repeated category-shared prerequisite | Consolidate into Level-2 BGK; add a standalone upward-link sentence at the beginning of the affected Level-3 section. |
| Mixed shared concept plus page-local prerequisite consequence | Move or remove the shared explanation, add the standalone upward-link sentence, and preserve the local prerequisite consequence as a bullet after it. |
| Definitely page-local prerequisite | Preserve the bullet title and wording unless a confirmed meaningful defect requires a minimal edit. |
| Helpful realistic example or analogy | Keep when technically faithful, concise, clearly illustrative, and materially clearer than an abstract definition alone; preserve shared examples once in Level-2 when they clarify a category-wide prerequisite. |
| Necessary ordinary-use versus unconventional-test-use contrast | Keep only the unusual relationship and interpretive consequence needed to prevent a wrong mental model. |
| Concrete test application | Remove from Background Knowledge; preserve or relocate it only when the correct later section does not already explain it. |
| Overview, correctness-contract, or conclusion material | Remove from Background Knowledge; `## Overview`, the page body, or `## Key Takeaways` owns it. |
| General tutorial material unused later | Remove. |
| Duplicate prerequisite explanation | Consolidate. |

Compare Background Knowledge explicitly with `## Overview` and `## Key Takeaways`. Overview and Key Takeaways intentionally overlap
as preview and retrospective views of the test. Background Knowledge instead supplies conceptual tools and should have minimal
substantive overlap with either. Do not treat a shared term or a short relevance bridge as a defect; correct repeated setup,
constants, mechanisms, validation contracts, or conclusions when they blur section responsibility or increase maintenance risk.

For a realistic example, verify that it clarifies a necessary prerequisite, is technically faithful, and is clearly illustrative
rather than the actual CTS setup. For a test-specific contrast, verify that ordinary use would otherwise create a plausible wrong
mental model and that the text stops after identifying the unconventional relationship and its interpretive consequence. Do not
reject an item merely because it uses an example or briefly mentions this test.

When correcting overreach:

- retain the conceptual portion of a mixed item only when it remains a page-local prerequisite;
- when shared content was consolidated, replace its in-bullet routing with the standalone upward-link sentence before all bullets;
- delete concrete application already explained adequately in the correct section;
- relocate unique necessary application detail to the appropriate later section;
- preserve definitely page-local bullets by default during shared-BGK cleanup;
- do not rename bullet titles merely for stylistic consistency;
- do not rewrite a Level-3 `## Background Knowledge` section wholesale;
- do not expand Background Knowledge or broadly restructure the page;
- reread affected sections to avoid creating gaps or contradictions.

Use `## Background Knowledge` as the primary home for prerequisite explanations. Place a concept near first use instead when that
produces a clearer local explanation, but do not duplicate it. Keep the heading mandatory. When no prerequisite remains after the
target-reader comparison, use the canonical no-prerequisite sentence from the Level-3 template.

Do not add prerequisites that are merely helpful, broadly educational, or unused by the page's core reasoning. Stop when the target
reader can follow the causal chain from test setup to expected result without consulting source code or a general Vulkan tutorial.

### 4. Explanation obligations

Check obligations created by introduced concepts:

| Introduced concept | Required explanation |
|---|---|
| Behavioral parameter | What changes in mechanism or validation |
| Resource | Who creates, binds, reads, writes, and validates it, as relevant |
| Generated artifact | What generates it and what behavior it controls |
| Synchronization operation | What becomes ordered, available, or visible |
| Shader operation or built-in | What it produces in this test and how that result is checked |
| Tolerance or mask | What is compared and how acceptance differs from exact comparison |
| Pruning rule | Whether it is requirement-based or design-based |
| Failure cause | Observable symptom plus a grounded possible cause |
| Representative case | Why it represents the chosen mechanism and what it does not cover |

### 5. Cross-section invariants

Verify that:

- behavior values align with failure mapping;
- failure symptoms trace to validation logic;
- validation inputs are produced by documented execution;
- shader/device outputs connect to host checking;
- parameter dimensions say what aspect they change;
- background concepts are used later;
- takeaways are established earlier;
- the source appendix supports rather than introduces behavior.

## Editing Policy

Edit confirmed meaningful defects directly in the rewritten target page.

- Preserve protected technical content and exact identifiers.
- Prefer the smallest correction that restores accuracy or clarity.
- Do not broaden page scope.
- Do not add teaching material unless required to close a demonstrated explanatory gap.
- Do not edit an uncertain point. Report it as unresolved after inspecting the relevant evidence.
- Keep obsolete navigation-style originals untouched.

### Generated shader boundary

Treat a shader walkthrough and its generated artifacts as an owned unit rather than ordinary editable prose. For generated SPIR-V,
`shader-disassembler` owns the exact subsection shape; auditors preserve it or replace the complete subsection through that skill.

| Confirmed defect | Required action |
|---|---|
| Explanation only; shader source and SPIR-V are correct | Edit only the explanatory prose. |
| Reconstructed GLSL/HLSL is wrong, whether or not its SPIR-V faithfully reflects it | Reinvoke `shader-analyzer` for the exact CTS case and replace the complete walkthrough output. |
| Reconstructed GLSL/HLSL is correct, but its SPIR-V subsection has wrong format, metadata, or assembly | Invoke `shader-disassembler` with the exact source, stage, and target; replace the complete subsection with its unchanged output. |
| CTS-authored SPIR-V path is wrong or inconsistently represented | Inspect the authoritative CTS artifact and rerun the applicable complete shader workflow; do not reconstruct or patch instructions manually. |
| Required workflow cannot complete or evidence remains inconsistent | Leave the generated artifact unchanged and report an unresolved finding. |

Never hand-edit or partially reformat generated or CTS-authored SPIR-V. Replace the complete owned artifact or leave it unresolved.

After editing or complete artifact regeneration, reread the affected section and its dependent sections to prevent local corrections from creating inconsistency.

## Compact Finding Format

Record only findings that caused an edit or remain unresolved. Every recorded finding must be evidence-backed: include concrete evidence in the `Mistake` or `Correction` bullet, such as an exact source link with line anchor, an exact mustpass line, an exact registration-tree entry, an exact generated-artifact regeneration result, or the specific page text that was inconsistent with those authorities. If a suspected defect cannot be tied to concrete evidence after reasonable inspection, leave it unresolved instead of presenting it as a confirmed correction.

Structure every finding with the fixed `Mistake` and `Correction` bullets so readers can scan the audit without parsing an unstructured paragraph. Allow multiple sentences in either bullet when needed to preserve the evidence and correction clearly; optimize for low reading burden, not minimum sentence count.

Prefer direct **incorrect model → corrected model** wording. The labels already establish page-edit context, so omit routine framing such as “the page treated,” “the page stated,” and “the page now explains.” State the concrete incorrect and corrected values, mechanisms, scopes, or relationships instead.

Use indirect wording only when the defect itself is an omission, ambiguity, misleading emphasis, or cross-section inconsistency that cannot be represented honestly as one explicit false claim. Do not invent a quotation or proposition merely to make the wording direct.

Keep one coherent mistaken mental model per finding. Split unrelated corrections into separate findings when they do not share one explanatory cause. Avoid omnibus inventories such as “matrix, pruning, marker, and shader details were inaccurate”; name the actual before/after facts.

For a resolved finding:

```markdown
### <finding title>

- **Mistake:** <Concrete incorrect model and concise confirming evidence.>
- **Correction:** <Concrete corrected model implemented by the edit or complete regeneration.>
```

For an unresolved finding:

```markdown
### <finding title> (UNRESOLVED)

- **Mistake:** <What the page communicates that could not be confirmed and what evidence was inspected.>
- **Correction:** No edit was made because <the unresolved evidence gap or risk>.
```

Keep the title short and descriptive. Do not repeat it in the bullets. Omit location, severity, separate technical/exposition verdicts, and confidence fields. Link concise evidence references when useful.

## Worker Result Contract

When operating under an orchestrator, edit only the assigned page and return:

```text
Page: <relative path>
Status: edited | no-confirmed-issues | unresolved
Findings:
- Title: <finding title>
  Mistake: <concrete incorrect model and compact evidence>
  Correction: <concrete corrected model or reason no edit was made>
  Evidence: <source link / mustpass line / registration entry / artifact regeneration result>
Validation: registration pass/fail/not-applicable; links pass/fail
Escalation: none | <shared pattern requiring category attention>
```

Do not edit the category audit summary. The orchestrator owns summary aggregation.

## Category Audit Summary Template

Write the combined result to `external/vulkancts/wiki/internal_doc/<category>_audit_summary.md`.

Include sections only for pages with resolved or unresolved findings. Place both kinds of findings under the affected page. Mark unresolved finding headings with `(UNRESOLVED)`.

Before writing page-specific findings, check whether the same root-cause defect recurs across multiple pages. When the same evidence-backed defect appears across 3 or more pages with the same Mistake and Correction, consolidate it into a `## Recurring Defect Patterns` section placed before the page-specific sections. Give the pattern one `Mistake` bullet, one `Correction` bullet, and one `Pages` bullet listing every affected page. Do not add back-references to the recurring pattern from page-specific sections; pages whose only finding is a recurring pattern go under `## Pages With Only Recurring Findings` instead of getting their own page section.

```markdown
# <Category> Audit Summary

## Recurring Defect Patterns

### <Pattern 1>

- **Mistake:** <Concrete incorrect model and concise confirming evidence.>
- **Correction:** <Concrete corrected model implemented by the edit or complete regeneration.>
- **Pages:** `Page1.md`, `Page2.md`, `Page3.md`.

## `<PageWithChanges1.md>`

### <Finding 1>

- **Mistake:** <Concrete incorrect model and concise confirming evidence.>
- **Correction:** <Concrete corrected model implemented by the edit or complete regeneration.>

### <Finding 2>

- **Mistake:** <Concrete incorrect model and concise confirming evidence.>
- **Correction:** <Concrete corrected model implemented by the edit or complete regeneration.>

### <Finding 3> (UNRESOLVED)

- **Mistake:** <What the page communicates that could not be confirmed and what evidence was inspected.>
- **Correction:** No edit was made because <the unresolved evidence gap or risk>.

## `<PageWithChanges2.md>`

### <Finding 1>

- **Mistake:** <Concrete incorrect model and concise confirming evidence.>
- **Correction:** <Concrete corrected model implemented by the edit or complete regeneration.>

## Pages With Only Recurring Findings

- `PageD.md`
- `PageE.md`

## Pages With No Confirmed Issues

- `PageA.md`
- `PageB.md`
- `PageC.md`
```

Rules:

- Use one page section for all of that page’s findings.
- Use exactly one `Mistake` bullet and one `Correction` bullet under every finding; either bullet may contain multiple sentences. Recurring pattern findings add one `Pages` bullet.
- Every finding must be evidence-backed. Include concrete evidence in the `Mistake` or `Correction` bullet, such as an exact source link with line anchor, an exact mustpass line, an exact registration-tree entry, an exact generated-artifact regeneration result, or the specific page text that conflicted with those authorities. If a suspected defect cannot be tied to concrete evidence after reasonable inspection, leave it unresolved instead of presenting it as a confirmed correction.
- Prefer direct incorrect-model versus corrected-model wording; reserve indirect wording for omissions, ambiguity, misleading emphasis, and cross-section inconsistency.
- State concrete before/after facts and split unrelated defects instead of collecting them in an omnibus finding.
- Do not create separate global resolved and unresolved sections; the `## Recurring Defect Patterns` section is for pattern grouping, not status grouping.
- Place `## Recurring Defect Patterns` before the page-specific sections. Place `## Pages With Only Recurring Findings` and `## Pages With No Confirmed Issues` at the end, parallel to each other.
- Omit `## Recurring Defect Patterns` when no pattern recurs across 3 or more pages. Omit `## Pages With Only Recurring Findings` when every affected page has at least one page-specific finding.
- Do not add back-references to a recurring pattern from page-specific sections; the pattern section already lists the affected pages.
- Include Level-2 in the same page-centered structure when it has findings.
- Omit `Pages With No Confirmed Issues` only when every page has a finding.
- Add a final compact `## Validation` section only when category validation failures or limitations need reporting; otherwise report validator success in the task completion response.
- Do not include the internal worksheet, passed claims, verbose validator logs, severity labels, or review narration.
