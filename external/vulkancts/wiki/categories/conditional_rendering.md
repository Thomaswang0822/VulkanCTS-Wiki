## Overview

The `conditional_rendering` test category collects tests that check whether Vulkan commands execute, are suppressed, or remain unaffected under `VK_EXT_conditional_rendering`.

## Background Knowledge

- **Conditional rendering state:** `vkCmdBeginConditionalRenderingEXT` reads a 32-bit value from a buffer and controls affected commands until `vkCmdEndConditionalRenderingEXT`. The inverted flag reverses the zero/nonzero decision. The draw, dispatch, clear, transform-feedback, and ignored-command families all rely on this state.
- **Command-buffer inheritance:** A secondary command buffer can inherit conditional-rendering state when its inheritance structure enables it. This matters when the same affected command is recorded at different primary or secondary levels.
- **Observable command effects:** A conditional decision is tested through an external result such as pixels, a dispatch counter, transform-feedback data, or buffer contents. A successful submission alone does not show that the command had the intended effect.

## Category Structure

```text
conditional_rendering
├── draw
├── dispatch
├── clear_attachments
├── draw_clear
├── conditional_ignore
└── transform_feedback
```

The registration-only dispatcher `vktConditionalTests.cpp` creates these six direct families. The shared conditional-rendering utility supplies predicate data, naming, buffers, and capability checks; it does not register another family.

## How the Families Fit Together

The families vary both **which command** is under conditional control and **how its effect** is observed.

- **Draw**, **dispatch**, and **clear_attachments** test affected commands that should run for an allowed predicate and have no observable effect for a suppressed predicate.
- **draw_clear** combines attachment clears with draw and buffer-update interactions so the command scope and result state can be compared in one family.
- **conditional_ignore** checks commands that must continue to operate even while conditional rendering is active, which is the category's contrast case.
- **transform_feedback** applies the same conditional-rendering question to captured vertex data and draw variants rather than only to a color image.

Together, the families cover predicate interpretation, inversion, memory placement, command-buffer scope, inheritance, nesting, and command-specific result checking.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `draw` | [Draw.md](../testfiles/conditional_rendering/Draw.md) | Direct, indexed, indirect, and indirect-count draws, including image comparison and command-buffer variants. |
| `dispatch` | [Dispatch.md](../testfiles/conditional_rendering/Dispatch.md) | Direct, indirect, and base dispatch paths, compute execution, predicate variants, and counter validation. |
| `clear_attachments` | [ClearAttachments.md](../testfiles/conditional_rendering/ClearAttachments.md) | Conditional color and depth/stencil attachment clears, including secondary and nested command-buffer paths. |
| `draw_clear` | [DrawAndClear.md](../testfiles/conditional_rendering/DrawAndClear.md) | Combined clear, draw, and update-buffer interactions under the shared condition matrix. |
| `conditional_ignore` | [Ignore.md](../testfiles/conditional_rendering/Ignore.md) | Commands that are expected to ignore active conditional rendering and their command-specific observations. |
| `transform_feedback` | [TransformFeedback.md](../testfiles/conditional_rendering/TransformFeedback.md) | Conditional transform-feedback draw commands and captured-buffer validation. |

## Category Notes

The legacy dispatcher page `vktConditionalTests.md` is folded into this category gateway because it contains registration rather than an independent implementation-bearing test family. The legacy family pages remain as source-navigation records; the shortened pages above are the canonical rewritten documentation.