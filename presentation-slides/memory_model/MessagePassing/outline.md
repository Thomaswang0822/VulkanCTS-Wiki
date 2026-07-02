## Global style/layout decisions

- Use `tokyo-night` dark technical visual style.
- Keep the page English-only until the final translation stage.
- Preserve keyboard interaction hints and skill-provided navigation/presenter behavior.
- Prefer short phrases, bullets, or half-sentences over full prose sentences.
- Prefer spacious, confident layouts over dense bullet lists.
- Use technical tags only when they fit the page, such as the title page; do not make them a global habit.

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

- Role: transition from general CTS/wiki context into the concrete test family for the rest of the talk.
- Left box: clarify that `message_passing` is a test family represented by many mustpass test cases, not one specific case.
- Use `images/mustpass_list.png` to show repeated `dEQP-VK.memory_model.message_passing...` entries and the large match count.
- Right box: state the expected behavior as a claim, not as a question.
- Core claim: when a reader observes the guard/signal, the payload written before that guard must also be visible under the tested synchronization conditions.

### Page 04 style/layout decisions

- Mark page 04 as `class="slide active"` in `index.html`.
- Use a two-card layout.
- Left card combines a short statement with the mustpass screenshot.
- Right card uses a compact message-passing flow: writer publishes payload, writer publishes guard, reader sees guard, reader must see payload.
- Do not show internal scope-control phrases such as “not a full survey” or “later only as contrast” to the audience.

## 05: Representative Shader: Execution Roles and Data Layout

## 06: payload and guard: The Core Shape of Message Passing

## 07: How release/acquire, scope, and storage class Enter the Test Matrix

## 08: validation and skip: What Counts as Pass, What Is Not Failure

## 09: Host-Side Flow: Turning Shader Results into CTS pass/fail

## 10: From One Example Back to the Full message_passing Family

## 11: How write_after_read and transitive Differ from message_passing

## 12: Zooming Out: Other Test Families in memory_model

## 13: Zooming Out Again: Applying This Wiki Method to Other CTS Categories

## 14: Three Takeaways
