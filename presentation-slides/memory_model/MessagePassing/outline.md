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

## 07: Execution Topology: Pairing Lanes and Locating Data

### Page 07 intention

- Explain who the participants are in the representative shader.
- Show that each active subgroup lane is paired with another lane using the subgroup XOR partner rule.
- Explain how local invocation coordinates become payload/guard buffer indices.
- Introduce the three key buffers in the representative case: payload buffer, guard buffer, and fail buffer.
- Prepare the audience to read the shader protocol without getting lost in coordinate setup.
- Visualization required: show paired subgroup lanes and the mapping from each lane to payload/guard/fail buffer slots.

## 08: Core Protocol: Payload Before Guard, Check After Guard

### Page 08 intention

- Walk through the technical heart of `message_passing` using the representative shader's main sequence.
- Step 1: each invocation writes its own payload.
- Step 2: each invocation publishes its guard with release / make-available semantics.
- Step 3: each invocation tries to observe the partner guard with acquire / make-visible semantics.
- Step 4: only after observing the guard, the invocation checks whether the partner payload has the expected value.
- State the expected behavior as a claim here, after `payload`, `guard`, invocation roles, and `skip` have already been introduced.
- Visualization required: show the two-invocation protocol as a timeline or message-passing sequence, including the conditional `skip` path.

## 09: Memory Semantics in the Shader: Why the Guard Should Carry the Payload

### Page 09 intention

- Explain the memory-model mechanism behind the protocol, without turning the talk into a full Vulkan memory model lecture.
- Connect release with making the payload write available before/with the guard signal.
- Connect acquire with making the partner payload visible after the guard is observed.
- Explain why scope and storage semantics matter: the guarantee only applies over the selected synchronization domain and storage class.
- Use the representative case to show where `gl_ScopeSubgroup`, `gl_StorageSemanticsBuffer`, `gl_SemanticsRelease`, `gl_SemanticsAcquire`, `gl_SemanticsMakeAvailable`, and `gl_SemanticsMakeVisible` enter.
- Recommended visualization: annotate the guard store/load operations with the semantics flags and show the payload visibility edge they are meant to establish.

## 10: Result Checking: `skip`, `fail`, and Host-Side Pass/Fail

### Page 10 intention

- Explain how shader-level observations become a CTS result.
- Clarify that not observing the partner guard produces `skip`, not failure.
- Clarify that observing the guard but reading a stale or wrong payload writes to the fail buffer.
- Summarize host behavior: clear resources, run many iterations, copy back the fail buffer, scan nonzero entries.
- Connect failure meaning to likely implementation problems such as incomplete release/acquire propagation, scope mishandling, or dropped memory semantics.
- Recommended visualization: shader-side `skip`/`fail` decision feeding into the host-side loop and fail-buffer scan.

## 11: From One Case Back to the Full `message_passing` Family

### Page 11 intention

- Generalize from the representative shader to the full family without repeating the entire matrix.
- Explain which dimensions vary: API/memory-model mode, data type, synchronization form, atomic operation, scope, payload storage, guard storage, and shader stage.
- Reuse the substance of `## Parameter Dimensions and Observed Values`, but compress it into grouped dimensions rather than a full table copy.
- Emphasize that the core payload-before-guard claim remains the same while resources, operations, and synchronization domains change.
- Prepare the transition from Part B's deep walkthrough to Part C's controlled zoom-out.
- Recommended visualization: a compact matrix/radar-style summary of which dimensions vary around the fixed core protocol.

## 12: How `write_after_read` and `transitive` Differ from `message_passing`

## 13: Zooming Out: Other Test Families in `memory_model`

## 14: Zooming Out Again: Applying This Wiki Method to Other CTS Categories

## 15: Three Takeaways
