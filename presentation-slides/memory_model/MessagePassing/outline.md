## Global style/layout decisions

- Use `tokyo-night` dark technical visual style.
- Keep the page English-only until the final translation stage.
- Preserve keyboard interaction hints and skill-provided navigation/presenter behavior.
- Prefer short phrases, bullets, or half-sentences over full prose sentences.
- Prefer spacious, confident layouts over dense bullet lists.
- Use technical tags only when they fit the page, such as the title page; do not make them a global habit.
- Use visualization proactively in Part B: draw.io diagrams, Mermaid diagrams, ASCII structure, code-highlight panels, screenshots, and simple HTML/CSS diagrams are all acceptable depending on the page.
- When a page says visualization is required, the slide must include an actual visual explanation, not only bullets.
- Use visualization proactively in Part B: draw.io diagrams, Mermaid diagrams, ASCII structure, code-highlight panels, screenshots, and simple HTML/CSS diagrams are all acceptable depending on the page.
- When a page says visualization is required, the slide must include an actual visual explanation, not only bullets.

## 01: MessagePassing Visibility Tests

### Page 01 intention

- Role: title page and expectation setter.
- Establish the topic as Vulkan CTS `memory_model.message_passing`, not a general Vulkan memory model lecture.
- Tell the audience the core question early: after observing a synchronization signal, should the protected payload be visible?
- Signal the final talk structure lightly: CTS/wiki context, one concrete `message_passing` walkthrough, then controlled generalization.

### Page 01 style/layout decisions

- Large title at the top-left.
- Stack the framing cards vertically so the audience reads the Topic box first.
- Make the Topic box visually dominant through larger padding, stronger border, and larger text.
- Keep the 30-minute path box secondary and compact.
- Use tags ordered from broad to specific: `Vulkan CTS`, `memory model`, `visibility`, `guard`, `payload`.

## 02: Vulkan CTS: What and Why

### Page 02 intention

- Role: give just enough Vulkan CTS context before introducing the wiki work.
- Keep the card titles as `What it is`, `Why it matters`, and `Why this talk`.
- In the `What it is` card, answer both: what is a conformance test, and what does passing Vulkan CTS mean.
- Define conformance by rules/compatibility: checks adherence to official standards, unlike general functional or performance tests.
- Middle card title should be `Why it matters for us`, with `for us` visually highlighted.
- Middle card narrative: we need both DirectX/HLK and Vulkan CTS, current priority is DirectX/HLK, Vulkan CTS knowledge/resources are still limited, and Vulkan CTS is valuable because it is open source while HLK is closed source.
- In the `Why this talk` card, frame `memory_model` as critical, difficult, and relevant to the audience; the new lens is conformance testing.

### Page 02 style/layout decisions

- Mark the current working page as `class="slide active"` in `index.html` so review opens directly on that page.
- Use three cards with ordinary text highlighting, not technical tags.
- Prefer short bullets and emphasized phrases over full explanatory sentences.
- Card 1 title: `What it is`.
- Card 2 title: `Why it matters for us`; highlight `for us`.
- Card 3 title: `Why this talk`.

## 03: Wiki Work: Turning an Executable Specification into Readable Knowledge

### Page 03 intention

- Role: explain my main-track task before entering `message_passing` details.
- Core idea: Vulkan CTS is executable and source-backed, but not easy to read directly.
- Wiki work is not merely a map/navigation layer; it rewrites source-navigation notes into explanation-first, in-place technical documentation.
- The rewritten pages explain test intent, execution, validation, failure meaning, and source evidence in the page itself.
- Bridge to this talk: `message_passing` is one example where `## Shader Analysis` and a representative walkthrough are central.
- Practical value after completion: support failure triage, group-level diagnosis, and test-driven implementation planning.

### Page 03 style/layout decisions

- Mark page 03 as `class="slide active"` in `index.html`.
- Use short phrase cards, no technical tag chips.
- Layout: two existing cards on the top row, plus a third card centered in the middle-bottom area.
- Top-left card: why raw CTS is hard to read.
- Top-right card: explanation-first wiki output, including `Shader Analysis` / representative walkthrough.
- Bottom-center card: how completed wiki pages help debugging and implementation planning.
- Keep this page about the wiki method, not about `message_passing` internals yet.

## 04: Focus for This Talk: `message_passing`

### Page 04 intention

- Role: transition from general CTS/wiki context into Part B without assuming the audience already knows the test vocabulary.
- Clarify that `message_passing` is a test family represented by many mustpass cases, not one particular case.
- Use `images/mustpass_list.png` to show repeated `dEQP-VK.memory_model.message_passing...` entries and the large match count.
- Include an ASCII structure that labels `dEQP-VK.memory_model.message_passing` as:
  - `dEQP-VK`: registration root / executable test namespace;
  - `memory_model`: test category;
  - `message_passing`: test family.
- Avoid explaining the expected behavior here; instead, tell the audience that Part B will decode one representative case step by step.

## 05: Backgrounds Before the Walkthrough: Invocations, Payload, Guard

### Page 05 intention

- Introduce the minimal vocabulary needed before any expected-behavior claim.
- Use a concrete toy problem: one warp-like subgroup / 32 shader invocations work on a 4×8 thread-ID tile and mirror left/right endpoints.
- Define shader invocation roles in this test: an invocation is one shader execution instance; here it writes its own data and later checks its paired partner's data.
- Use common memory-ordering intuition only where it clarifies the test: the relevant idea is payload write-before-guard and later read-after-observing-guard, not a generic resource-contention story.
- Define `payload` as a per-invocation payload slot in a payload buffer/matrix; for pair T1/T6, T1's payload slot stores `1`, and T6 reads that slot when checking T1.
- Define `guard` as a separate per-invocation synchronization slot in a guard buffer/matrix; for pair T1/T6, T1's guard slot is the signal that T1's payload write should now be visible to its partner.
- Clarify that there is no extra swap-style temporary variable in this test; the communication storage is the payload buffer plus the guard buffer.
- Introduce `release` / `make-available` as the writer-side operation that publishes prior payload writes toward visibility before/with the guard signal.
- Introduce `acquire` / `make-visible` as the reader-side operation that makes the partner payload visible after observing the partner guard.
- Define `skip` at a high level: if the partner guard is not observed, that race instance is not judged as a failure.
- Visualization: top wide card shows the 4×8 thread tile; bottom-left shows payload/guard as separate per-thread slot matrices; bottom-right shows a flow chart with objects and operations separated.

## 06: Representative Case: The Path We Will Walk Through

### Page 06 intention

- Present the exact representative CTS path from `Representative Shader Walkthrough 1`.
- Explain why this path is a good default case: compute shader, `u32`, subgroup scope, buffer payload, buffer guard, atomic store/load synchronization.
- Reuse the substance of the `Parameter Values Chosen` table, but compress it into a slide-friendly decoding of the path.
- Translate the long registered path into a small set of meaningful choices rather than reading every token mechanically.
- Establish that later pages follow this one case deeply before generalizing back to the full family.
- Before the walkthrough finishes, do not introduce parameter variations such as alternative payload storage classes; keep the audience inside this one representative case.

### Page 06 style/layout decisions

- Mark page 06 as `class="slide active"` in `index.html` so review opens directly on that page.
- Hero code panel showing the full registered path `dEQP-VK.memory_model.message_passing.ext.u32.noncoherent.atomic_atomic.atomicwrite.subgroup.payload_nonlocal.buffer.guard_nonlocal.buffer.comp`, with `message_passing` highlighted in the family color.
- Token ↔ meaning table on the right: compact 9 rows covering test type, memory-model mode, data type, sync form, atomic op, scope, payload storage, guard storage, stage.
- Single bottom callout: "pages 07–10 stay inside this exact case".
- No GLSL, no scope/storage variations, no expected-behavior claim here — those belong to pages 07/08/11.

## 07: Execution Topology: Pairing Lanes and Locating Data

### Page 07 intention

- Explain who the participants are in the representative shader.
- Show that each active subgroup lane is paired with another lane using the subgroup XOR partner rule.
- Explain how local invocation coordinates become payload/guard buffer indices.
- Introduce the three key buffers in the representative case: payload buffer, guard buffer, and fail buffer.
- Prepare the audience to read the shader protocol without getting lost in coordinate setup.
- Visualization required: show paired subgroup lanes and the mapping from each lane to payload/guard/fail buffer slots.

### Page 07 style/layout decisions

- Mark page 07 as `class="slide active"` in `index.html` so review opens directly on that page (and remove `active` from page 06).
- Mandatory visualization: a paired-lane diagram. Use the html-ppt in-slide CSS/HTML style (no external image). Concretely, render a row of 8 subgroup lanes paired across the row (e.g. lane `i` ↔ lane `i ^ 7`), with arrows connecting each pair. Below each lane show its `bufferCoord` (payload slot) and `partnerBufferCoord`.
- Lane-pairing diagram on the top half, in a single wide card.
- Bottom row: three small cards introducing the three host-created/bound resources: payload buffer (binding 0), guard buffer (binding 1), fail buffer (binding 2). Each card shows binding index, descriptor set, role, and which buffer slot it lives at. No GLSL on this slide; that's page 08.
- Speaker notes hold the literal `gl_SubgroupInvocationID ^ (gl_SubgroupSize − 1)` rule and the linearization formula `bufferCoord = (gl_WorkGroupID.y * NUM_WORKGROUP_EACH_DIM + gl_WorkGroupID.x) * DIM * DIM + localId.y * DIM + localId.x`.
- Do not show SPIR-V, do not show the `write_after_read` early-read inversion, do not introduce transitive workgroup relay — those belong on slides 08/09/12.

## 08: Core Protocol: Payload Before Guard, Check After Guard

### Page 08 intention

- Walk through the technical heart of `message_passing` using the representative shader's main sequence.
- Step 1: each invocation writes its own payload.
- Step 2: each invocation publishes its guard with release / make-available semantics.
- Step 3: each invocation tries to observe the partner guard with acquire / make-visible semantics.
- Step 4: only after observing the guard, the invocation checks whether the partner payload has the expected value.
- State the expected behavior as a claim here, after `payload`, `guard`, invocation roles, and `skip` have already been introduced.
- Visualization required: show the two-invocation protocol as a timeline or message-passing sequence, including the conditional `skip` path.

### Page 08 style/layout decisions

- Mark page 08 as `class="slide active"` in `index.html` so review opens directly on that page (and remove `active` from page 07).
- Lead with the **expected-behavior claim** as a one-line hero statement at the top of the slide, so the audience leaves with it.
- Below the claim, render a **4-step protocol timeline** (Step 1 → 2 → 3 → 4), each step on its own row showing: phase number, the operation name (e.g. "write payload"), the responsible lane role (publisher/consume), and a tiny `payload[i]`/`guard[i]` snippet.
- Two side-by-side consequence cards beneath the timeline: **if partner guard is observed (i.e. `!skip`) → check fires** (the expected outcome, payload matches), and **if partner guard is not observed (i.e. `skip`) → check skipped** (no failure recorded).
- A short `glsl` code block at the bottom showing the **literal 4-step pattern** as it would appear in the shader (`payload[i] = …; atomicStore(guard[i], 1, …release…); skip = atomicLoad(guard[partner], …acquire…) == 0; if (!skip && r != partnerCoord) fail[…] = 1;`). Use monospace, syntax-light highlight.
- Speaker notes hold the precise semantics flag tuple (`gl_ScopeSubgroup`, `gl_StorageSemanticsBuffer`, `gl_SemanticsRelease | gl_SemanticsMakeAvailable`, `gl_SemanticsAcquire | gl_SemanticsMakeVisible`) — that detail belongs to page 09, not here.
- Do not introduce transitive relay, write_after_read inversion, or the host pass/fail loop — those are pages 10/12.

## 09: Memory Semantics in the Shader: Why the Guard Should Carry the Payload

### Page 09 intention

- Explain the memory-model mechanism behind the protocol, without turning the talk into a full Vulkan memory model lecture.
- Connect release with making the payload write available before/with the guard signal.
- Connect acquire with making the partner payload visible after the guard is observed.
- Explain why scope and storage semantics matter: the guarantee only applies over the selected synchronization domain and storage class.
- Use the representative case to show where `gl_ScopeSubgroup`, `gl_StorageSemanticsBuffer`, `gl_SemanticsRelease`, `gl_SemanticsAcquire`, `gl_SemanticsMakeAvailable`, and `gl_SemanticsMakeVisible` enter.
- Recommended visualization: annotate the guard store/load operations with the semantics flags and show the payload visibility edge they are meant to establish.

### Page 09 style/layout decisions

- Mark page 09 as `class="slide active"` in `index.html` so review opens directly on that page (and remove `active` from page 08).
- Title and lead framing: "Why the guard should carry the payload — the memory-model mechanism". Skip any preliminary recap of the 4 steps; the audience just saw page 08.
- Top: a **two-pane symmetry block**. Left pane = the writer side (publisher), right pane = the reader side (consumer). Each pane shows: (a) the GLSL operation as a code line, (b) the four semantics-flags tuple it carries, (c) a one-line plain-English outcome.
- Middle: a **scope/storage-semantics explainer strip** with three small cards — `gl_ScopeSubgroup` (who can synchronize), `gl_StorageSemanticsBuffer` (which storage class), and a note that the guarantee only applies across this exact scope+storage combination.
- Bottom: a **drawio-style ASCII or CSS edge diagram** showing the payload-write availability edge crossing the guard signal, the scope boundary, and arriving at the partner payload read. Use a simple two-lane horizontal flow (publisher → consumer) with the guard atom in the middle.
- Do not introduce the host pass/fail loop, the write_after_read / transitive variation, or the failure-debug angle. Those are pages 10/12.

## 10: Result Checking: `skip`, `fail`, and Host-Side Pass/Fail

### Page 10 intention

- Explain how shader-level observations become a CTS result.
- Clarify that not observing the partner guard produces `skip`, not failure.
- Clarify that observing the guard but reading a stale or wrong payload writes to the fail buffer.
- Summarize host behavior: clear resources, run many iterations, copy back the fail buffer, scan nonzero entries.
- Connect failure meaning to likely implementation problems such as incomplete release/acquire propagation, scope mishandling, or dropped memory semantics.
- Recommended visualization: shader-side `skip`/`fail` decision feeding into the host-side loop and fail-buffer scan.

### Page 10 style/layout decisions

- Mark page 10 as `class="slide active"` in `index.html` so review opens directly on that page (and remove `active` from page 09).
- Lead framing: "From a per-invocation observation to a host-side verdict". The audience should leave with the two-step mapping: shader writes fail buffer → host scans fail buffer.
- Top half: a **2-column decision matrix** mapping (a) `skip = true` → no fail written (left card), (b) `!skip && r != partnerBufferCoord` → fail buffer entry 1 (right card). Use the same green/purple card colors as page 08 for visual continuity.
- Middle: a **host-side flow strip** as 5 small step pills in a row, each with a number, a host action label, and a tiny code/token:
  1. clear fail buffer (host-side reset, once)
  2. clear payload + guard (per iteration)
  3. dispatch shader (50× iterations, 4 submits)
  4. copy fail buffer → host-visible memory (only on final submit)
  5. scan fail buffer; any nonzero = case fails
- Bottom: a **failure-meaning card** that lists the most likely implementation problems this case catches — incomplete release/acquire propagation, scope mishandling, dropped MakeAvailable/MakeVisible semantics, bad image/buffer storage lowering.
- Speaker notes hold the wiki citations (the `vktMemoryModelMessagePassing.cpp` line ranges from the wiki) and the exact "fail the case if any entry is nonzero; log up to 256 failing invocation indices" rule.
- Do not introduce transitive relay, write_after_read early-read timing, or the full failure-debug taxonomy. Those are pages 12 / future.

## 11: From One Case Back to the Full `message_passing` Family

### Page 11 intention

- Generalize from the representative shader to the full family without repeating the entire matrix.
- Explain which dimensions vary: API/memory-model mode, data type, synchronization form, atomic operation, scope, payload storage, guard storage, and shader stage.
- Reuse the substance of `## Parameter Dimensions and Observed Values`, but compress it into grouped dimensions rather than a full table copy.
- Emphasize that the core payload-before-guard claim remains the same while resources, operations, and synchronization domains change.
- Prepare the transition from Part B's deep walkthrough to Part C's controlled zoom-out.
- Recommended visualization: a compact matrix/radar-style summary of which dimensions vary around the fixed core protocol.

### Page 11 style/layout decisions

- Mark page 11 as `class="slide active"` in `index.html` so review opens directly on that page (and remove `active` from page 10).
- Lead framing: "Same protocol, many dimensions". The audience should leave with the mental model of "one fixed claim, N varying axes".
- Top half: a **fixed-core vs varying-axes block** as a 2-column layout.
  - Left: a small "core" pill highlighting the fixed 4-step protocol claim from page 08.
  - Right: a 4×N (or N-row) list of varying dimensions. Each row: dimension name (yellow), values, "what it stresses".
- Middle: a **single representative radar/matrix summary** that shows all 8 dimensions in a compact visual form. Use simple HTML/CSS — for example, an 8-cell wheel or a horizontal bar where each axis has a label and 2-3 tokens. No external images, no drawio (the outline allows but I prefer the consistent html-ppt look at this scale).
- Bottom: a **continuity note** in a small footer-style card: the claim (page 08) holds across all dimensions; only the resources, operations, and synchronization domain change. No new GLSL, no host behavior on this page.
- Speaker notes hold the wiki's full dimension table values for reference and explicitly note that page 12 covers write_after_read / transitive, page 13 covers other memory_model families.

## 12: How `write_after_read` and `transitive` Differ from `message_passing`

### Page 12 intention

- Role: controlled zoom-out inside the same implementation file after the audience understands regular `message_passing`.
- Keep `message_passing` as the baseline: write payload first, synchronize through guard, then check partner payload after the guard is observed.
- Explain `write_after_read` as the timing inversion: read partner payload before the synchronization point, then verify that this early read did not see the later synchronized write.
- Explain `transitive` as the chain extension: visibility may travel through a representative invocation and workgroup synchronization before other invocations read the partner payload.
- Emphasize that all three families reuse the same payload/guard/fail-buffer vocabulary, but ask different ordering questions.
- Avoid diving into a second full shader walkthrough; this is a contrast slide, not another deep walkthrough.
- Transition message: Part B taught one direct payload/guard protocol; Part C now shows how nearby tests mutate the same idea.

### Page 12 style/layout decisions

- Use a three-column comparison layout: `message_passing`, `write_after_read`, and `transitive`.
- Each column should have the same internal structure: core question, simplified sequence, failure meaning.
- Use a small visual timeline per column:
  - `message_passing`: `write payload → release guard → acquire guard → read payload`.
  - `write_after_read`: `early read payload → synchronize → partner writes payload → early value must stay zero`.
  - `transitive`: `payload write → representative release/acquire → workgroup relay → payload read`.
- Use color continuity from Part B: payload in green, guard/sync in yellow, fail condition in red/pink.
- Speaker notes can mention `sharedSkip`, representative invocation `(0,0)`, `transvis`, and `nontransvis`, but keep the visible slide lightweight.
- Do not introduce `padding` or `shared` yet; those belong to page 13.

## 13: Zooming Out: Other Test Families in `memory_model`

### Page 13 intention

- Role: expand from the `message_passing`-related families to the full `memory_model` category.
- Show that `memory_model` has five registered families: `message_passing`, `write_after_read`, `transitive`, `padding`, and `shared`.
- Group the first three as synchronization/visibility tests, because they focus on when shader-visible writes become observable.
- Introduce `padding` as a layout-preservation test: shader-visible structure copies must not overwrite host-visible `std140` padding bytes.
- Introduce `shared` as a workgroup shared-memory layout/value-preservation family: generated fields are written, synchronized, read, and compared inside compute workgroups.
- Make clear that the category is not only about release/acquire; it is broader shader-visible memory correctness.
- Prepare the final zoom-out to the wiki method: different families need different explanation strategies, but the same documentation discipline applies.

### Page 13 style/layout decisions

- Use a category-map visual, not a dense table.
- Top: ASCII/tree or simple CSS hierarchy rooted at `memory_model`, with five family nodes.
- Middle: group cards:
  - `message_passing / write_after_read / transitive`: visibility timing and synchronization.
  - `padding`: declared members vs padding bytes.
  - `shared`: generated shared objects, barriers, readback comparison.
- Bottom: one synthesis sentence: "same category, different memory-correctness angles".
- Keep page 13 high-level; no source paths, no code snippets, no mustpass screenshots.
- Speaker notes can point back to the category page and the three Level-3 pages: `MessagePassing.md`, `Padding.md`, and `SharedLayout.md`.

## 14: Zooming Out Again: Vulkan CTS Is Much Bigger Than `memory_model`

### Page 14 intention

- Role: pull the audience out from the `memory_model` narrative and remind them that this talk only sampled one small region of Vulkan CTS.
- Use the 53 documented top-level Vulkan CTS categories from `external/vulkancts/wiki/README.md` as the factual anchor.
- Do not show a 53-row category table. Instead, group all 53 categories into broad, lightweight "areas" so the audience sees the suite's scale and variety at a glance.
- Make the page technically lightweight: no new memory-model concepts, no source-reading workflow, no detailed category internals.
- Core message: Vulkan CTS is a gigantic conformance suite that covers almost every visible part of Vulkan behavior, not just synchronization tests.
- Connect back to wiki value briefly: because the suite is this broad, explanation-first wiki pages are useful; engineers should not need to reverse-engineer every category directly from source.
- Prepare the final takeaway slide by moving from one case → one category → the full Vulkan CTS landscape.

### Page 14 style/layout decisions

- Use a compact grouped table titled `53 documented top-level categories, grouped by area`.
- Use `Area` as the grouping word.
- Table rows / area groups:
  - Foundation / API objects: `info`, `api`, `memory`, `query_pool`, `binding_model`, `descriptor_indexing`, `device_group`.
  - Synchronization / correctness: `synchronization`, `synchronization2`, `memory_model`, `robustness`, `protected_memory`, `sparse_resources`.
  - Pipeline / rendering: `pipeline`, `shader_object`, `renderpasses`, `imageless_framebuffer`, `dynamic_state`, `draw`, `rasterization`, `fragment_operations`, `clipping`, `depth`, `conditional_rendering`, `multiview`.
  - Resources / formats / presentation: `image`, `image_processing`, `texture`, `ycbcr`, `drm_format_modifiers`, `wsi`, `video`.
  - Shader stages / shader execution: `geometry`, `tessellation`, `transform_feedback`, `ubo`, `ssbo`, `glsl`, `spirv_assembly`, `subgroups`, `compute`, `graphicsfuzz`, `reconvergence`.
  - Modern / advanced features: `fragment_shader_interlock`, `fragment_shading_rate`, `fragment_shading_barycentric`, `mesh_shader`, `ray_query`, `ray_tracing_pipeline`, `cooperative_vector`, `tensor`, `data_graph`, `dgc`.
- Render category names as small monospace chips, not as dense prose.
- Add a bottom callout: "This talk covered one representative path; the same documentation effort makes the larger suite navigable."
- Avoid telling the audience to read CTS source code as the normal path. Mention source only as authority/confirmation, not as the main consumption route.

## 15: Three Takeaways

### Page 15 intention

- Role: closing slide for a 30-minute technical talk.
- Takeaway 1: `message_passing` tests a precise visibility contract — after observing the guard, the protected payload should be visible.
- Takeaway 2: Vulkan CTS encodes this contract through many parameterized cases, varying scope, storage, synchronization form, data type, and shader stage.
- Takeaway 3: the wiki work turns executable CTS logic into readable engineering knowledge that helps debugging, implementation, and future conformance work.
- End with a balanced scope: we walked one representative case deeply, then zoomed out enough to locate the rest of the category and the documentation method.
- Keep the final message confident and concise; no new technical material.

### Page 15 style/layout decisions

- Use three large numbered cards across the center: `Visibility contract`, `Parameterized CTS coverage`, `Readable engineering knowledge`.
- Each card should have one bold phrase and one short supporting line.
- Add a small final footer line: `from one shader protocol → one CTS family → one documentation method`.
- Avoid dense bullets, code, tables, or screenshots.
- Preserve navigation hint footer, but visually let the three takeaways dominate the slide.
