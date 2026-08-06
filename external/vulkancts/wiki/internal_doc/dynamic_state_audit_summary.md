# Dynamic State Audit Summary

## Audit Scope

- Category: `dynamic_state`
- Rewritten Level-3 pages: 10
- Rewritten Level-2 page: `categories/dynamic_state.md`
- Audit mode: orchestrated parallel (1 worker per page)

## `VP.md`

### Scissor test geometry overstated and mislabeled

- **Mistake:** The `scissor` behavior section stated the NDC `-0.5..0.5` quad "covers the whole framebuffer" and the half-size scissor clips to "the bottom-left quadrant." NDC `-0.5..0.5` maps to pixels `32..96` (central 64x64), not the whole framebuffer. The scissor clips to the `32..64` overlap at the top-left corner, not "bottom-left."
- **Correction:** Rewrote to state the quad covers the central 64x64 region and the scissor clips to the `32..64` overlap, using NDC regions instead of orientation-dependent labels. Evidence: `vktDynamicStateVPTests.cpp#L200-L236`.

## `RS.md`

### Wrong `r` formula for fixed-point depth attachment

- **Mistake:** BGK stated `r = 1.0 / (2^N - 1)`. The Vulkan spec says `r` is implementation-dependent and at most `2 × 2^(-n)`, which for D16 is `1/32768`, not `1/65535`. The wrong formula propagated into nonzero case explanations and failure analysis.
- **Correction:** Corrected the formula to match the spec bound, rewrote nonzero case depth/bias reasoning, and fixed failure analysis to accommodate any conformant `r`. Evidence: `primsrast.adoc#L3856-L3862`.

### Conflation of `DepthBiasBaseCase` and `DynamicStateBaseClass`

- **Mistake:** The page stated all three base-class cases use `DynamicStateBaseClass`. Only `line_width` extends it; `depth_bias` and `depth_bias_clamp` extend `DepthBiasBaseCase` (a self-contained class with its own depth/stencil setup).
- **Correction:** Distinguished the two base classes across Overview, Runtime, Parameter Dimensions, Pruning, and Source Appendix. Evidence: `vktDynamicStateRSTests.cpp#L59`, `#L707`.

## `DS.md`

### Stencil advanced opening sentence falsely claimed both pipelines use `NOT_EQUAL`

- **Mistake:** The `stencil_params_advanced` section opened with "both using `VK_COMPARE_OP_NOT_EQUAL`." Pipeline 1 uses `VK_COMPARE_OP_ALWAYS`; only pipeline 2 uses `NOT_EQUAL`.
- **Correction:** Removed the false clause. Evidence: `vktDynamicStateDSTests.cpp#L1127-L1143`.

## `General.md`

### `state_persistence` persistence mechanism misidentified

- **Mistake:** The page attributed `state_persistence` to viewport, claiming "the viewport set before the first draw must still apply to the second." Source re-sets viewport/scissor before each draw; the actual persistence-bearing states are rasterization, blend, and depth/stencil.
- **Correction:** Updated behavior subsection, failure mapping, and cause analysis to name rasterization/blend/depth-stencil as persistence-bearing. Evidence: `vktDynamicStateGeneralTests.cpp#L387-L405`.

## `Clear.md`

### Misleading "transfer-queue-scoped" claim

- **Mistake:** The page stated the clear-vs-blit/copy/resolve split "covers both render-pass-scoped and transfer-queue-scoped command paths," implying a dedicated transfer queue. The test uses only the universal queue.
- **Correction:** Replaced with "all four execute on the universal queue; the split covers render-pass-interior and render-pass-exterior recording points." Evidence: `vktDynamicStateClearTests.cpp#L88`.

## `Inheritance.md`

### Bogus-state injection scope overstated

- **Mistake:** The page stated "For the non-`baseline` modes, the primary buffer deliberately records bogus viewport/scissor state." `primary`/`primary_with_count` record correct state; bogus state is injected only for the other 6 modes.
- **Correction:** Rewrote to state `primary`/`primary_with_count` record correct state, every other mode records bogus state. Evidence: `vktDynamicStateInheritanceTests.cpp#L786-L876`.

### `VK_EXT_extended_dynamic_state` requirement overgeneralized to all with-count leaves

- **Mistake:** The page implied all with-count leaves require `VK_EXT_extended_dynamic_state`. The extension is required only for specific with-count variants, not all.
- **Correction:** Scoped the requirement accurately. Evidence: same source switch.

## Pages With No Confirmed Issues

- `CB.md`
- `LineWidth.md`
- `Compute.md`
- `Discard.md`

## `dynamic_state.md` (Level-2)

No confirmed issues. The Level-2 page accurately represents the category hierarchy (7 construction-type subgroups, conditional `compute_transfer`), routes every family correctly, and the shared Background Knowledge (dynamic state, construction-type subgroups, DynamicStateBaseClass harness) is correctly consolidated. The `discard` family description was corrected from the outline's `VK_EXT_discard_rectangles` mislabel to GLSL `discard` interaction during rewrite.

## Validation

- Category-scoped registration validation: **all paths verified** across all 10 Level-3 pages.
- Category-scoped link validation: **all local wiki links valid** across the Level-2 page and all 10 Level-3 pages.
- All page-scoped validators pass after audit edits.
