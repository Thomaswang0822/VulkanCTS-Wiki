## Overview

Start with one concise sentence using this shape:

```markdown
The `<test category name>` test category collects tests that check <test intention clause>.
```

Then add more short sentences only if the category identity needs clarification.

Guidelines:

- State the shared testing theme of the test category, not the implementation layout.
- Do not repeat generic wiki-reading guidance such as “details live in Level-3 pages.” That belongs in the future reader guide.
- Do not mention source files here unless the source file itself is part of the test category identity.

## Background Knowledge

Keep this heading in every Level-2 category page. Use it for prerequisite concepts that are shared by multiple Level-3 pages and are
better explained once at category level than repeated in every test-family page.

Use a brief unordered list when common concepts exist. Each item should:

- define one prerequisite concept outside the target-reader baseline;
- be needed by multiple Level-3 pages in the category;
- explain the minimum concept and, only when useful, briefly identify why later Level-3 reasoning depends on it;
- remain category-level background rather than becoming a summary of concrete test setup, parameters, validation, expected results,
  or failure meaning.

A concise realistic example or analogy is allowed when it materially improves the shared mental model. Make clear that it is
illustrative rather than the actual CTS setup.

If no common prerequisite concepts need category-level explanation, keep the heading and write exactly:

```text
No common prerequisite concepts need category-level explanation for this test category.
```

## Category Structure

Show the direct test category hierarchy using the textual tree format.

```text
<test category>
├── <test family>
├── <test family>
└── <test family>
```

After the tree, add a short note only when it helps navigation.

Useful cases:

- one Level-3 page covers multiple direct test families;
- one direct test family is delegated to a separate Level-3 page;
- the visible Level-3 page count differs from the direct test family count.

Keep this section factual and short. Do not turn it into source navigation.

## How the Families Fit Together

Explain why the test families belong to the same test category and why they are separated into different test families or Level-3 pages.

Preferred shape:

- one short lead sentence;
- 2-4 bullets comparing the test families at category level;
- one optional closing sentence summarizing the shared theme.

Guidelines:

- Focus on test family relationships, not test family internals which belong to respective Level-3 pages.
- Explain similarities and differences only at the test category level.
- Do not duplicate Level-3 matrices, shader walkthroughs, validation mechanics, feature gates, or source-reference appendices.
- Use bold contrast words such as **when**, **which bytes**, or **which fields** only when they make the test family relationship clearer.

## Level-3 Pages Navigation

Route readers to the right Level-3 page using a compact navigation table.

Preferred table shape:

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| <test family, intermediate node, test case range, or conceptual area> | <Level-3 page link> | <specific reader-facing purpose> |

Guidelines:

- Use this as the uniform Level-2 navigation section.
- Link to Level-3 pages, not source files.
- Keep rows compact and concrete.
- Use `test family` for direct Level-3 components. Use `intermediate node` only for registered path components below a
  test family; do not use `node` as an alias for the test category or a test family.
- For large test categories, a longer table is acceptable; clarity should scale through structure, not through omitting important
  Level-3 pages.
- If a test category has many Level-3 pages, organize rows by registered test family, intermediate node, or conceptual area inside
  this section.
- Do not add generic catch-all rows such as “for exact details, read the relevant Level-3 page.”
- Every row should map a specific registered test family, intermediate node, test case range, concept, or reader goal to a concrete
  Level-3 page.
- Avoid repeating generic reading-guide prose that should live in a future wiki reader guide.

## Category Notes

Use this optional section only for miscellaneous test-category-level characteristics that improve navigation or clarify scope and do not
fit naturally in another section.

Preferred shape:

- <short note about unusual test category organization, naming, coverage boundary, or navigation caveat>.

Guidelines:

- Omit this section when there are no such notes.
- Prefer placing special facts directly in the section where they fit best. For example, notes about how the test category tree maps to
  Level-3 pages usually belong under `Category Structure`, not here.
- Keep notes at test-category level; do not duplicate Level-3 technical details.
- Use source references only when a test-category entrypoint or scope boundary cannot be explained through Level-3 links.
