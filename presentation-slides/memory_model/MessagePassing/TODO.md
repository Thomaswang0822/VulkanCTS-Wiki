# MessagePassing Slides TODO

## Scope

- Output directory: `presentation-slides/memory_model/MessagePassing`
- Primary topic: Vulkan CTS `memory_model.message_passing`
- Secondary topic: `write_after_read` and `transitive` differences, limited to at most one slide
- Audience: colleagues who know GPU and memory model concepts, but may not know Vulkan CTS
- Duration target: 30 minutes
- Theme/style target: `tokyo-night`-inspired dark technical sharing
- Interaction target: keep keyboard navigation, presenter mode, and overview mode behavior

## Sources

- Primary: `external/vulkancts/wiki/testfiles/memory_model/MessagePassing.md`
- Supporting explanation: `external/vulkancts/wiki/testfiles/memory_model/MessagePassing_brief.md`
- Chinese reference: `vkcts-wiki-pages/categories/memory_model/MessagePassing.md`
- Context: `external/vulkancts/wiki/README.md`, `Reader_Guide.md`, `CTS_Framework.md`, `categories/memory_model.md`

## Progress

- [x] Confirm global `html-ppt` skill location and installed skill
- [x] Read installed skill metadata and official overview/article
- [x] Read wiki context and `memory_model` category page
- [x] Capture accepted style decisions: `tokyo-night` theme and skill-provided interactions
- [x] Capture updated constraints: 30-minute duration, English-first workflow, and primary focus on `message_passing`
- [x] Discuss three-part talk framework before rewriting the outline
- [x] Rewrite `outline.md` with only `## {page number}: {page title/summary}` entries
- [-] Discuss and decide each page content one at a time
- [ ] Generate first minimal deck draft only after outline approval
- [ ] Browser-review deck rendering
- [ ] Iterate on density, wording, diagrams, and speaker notes

## Working Notes

- Output path is fixed.
- Use the `tokyo-night` theme.
- Keep skill-provided interactions such as `S` presenter mode, left/right navigation, and overview mode.
- Start from English-only slide content.
- Use `.agents/skills/translate-doc/SKILL.md` principles only at the final translation stage.
- During final translation, preserve identifiers, paths, filenames, registered test paths, code tokens, inline code, and Vulkan/CTS terms where English is clearer.
- During final translation, do not use excessive English-Chinese mixing for ordinary explanatory prose.
- Main content should focus on `message_passing`; `write_after_read` and `transitive` are comparison-only topics.
- Per-page workflow:
  1. Write page intention: included content plus important page-specific style/layout/format decisions.
  2. Implement only that page in `index.html`.
  3. Review both `outline.md` intention and rendered slide.
  4. Iterate on the same page until accepted, then move to the next page.
- Keep existing `index.html` only as a bad-example/reference artifact until each page is rebuilt.
- Existing `outline.md` is an English-only review outline; add detailed notes only for the current page under discussion.
- Proceed one TODO item at a time.

## Review Checklist

- [ ] Slide count fits 30 minutes.
- [ ] Core question is clear by slide 4.
- [ ] Payload/guard diagram is understandable without source code.
- [ ] `message_passing`, `write_after_read`, and `transitive` distinction is memorable.
- [ ] Runtime pass/fail flow explains how shader failure becomes CTS failure.
- [ ] Speaker notes are useful but not overlong.
