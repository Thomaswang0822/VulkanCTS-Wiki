## Global style/layout decisions

- Use `tokyo-night` dark technical visual style.
- Keep the page English-only until the final translation stage.
- Preserve keyboard interaction hints and skill-provided navigation/presenter behavior.
- Prefer spacious, confident layouts over dense bullet lists.
- Use technical tags to preview vocabulary, ordered from broader context to concrete mechanism.

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

## 02: Why Start from Vulkan CTS

## 03: Wiki Work: Turning an Executable Specification into Readable Knowledge

## 04: Focus for This Talk: One Test Family, message_passing

## 05: The Minimal Question: After Seeing guard, Is payload Visible Too

## 06: Representative Shader: Execution Roles and Data Layout

## 07: payload and guard: The Core Shape of Message Passing

## 08: How release/acquire, scope, and storage class Enter the Test Matrix

## 09: validation and skip: What Counts as Pass, What Is Not Failure

## 10: Host-Side Flow: Turning Shader Results into CTS pass/fail

## 11: From One Example Back to the Full message_passing Family

## 12: How write_after_read and transitive Differ from message_passing

## 13: Zooming Out: Other Test Families in memory_model

## 14: Zooming Out Again: Applying This Wiki Method to Other CTS Categories

## 15: Three Takeaways
