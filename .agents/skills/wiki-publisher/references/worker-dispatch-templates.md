# Publisher Worker Dispatch Templates

Load this reference when orchestrating a category publication. Keep prompts minimal because
[`../SKILL.md`](../SKILL.md) is the canonical workflow source.

## Level-2 translation worker

```text
Translate the Level-2 `<category>` category page using `.agents/skills/wiki-publisher/SKILL.md`.

Input:
- `external/vulkancts/wiki/categories/<category>.md`

Output:
- `vkcts-wiki-pages/categories/<category>.md`

Strictly follow the skill's translation-worker requirements. For this page, load and apply `shuorenhua` then `humanizer-zh` yourself; do not dispatch another language-review agent or launch a separate chat, session, or process. Do not run link conversion. When complete, use `attempt_completion`.
```

## Level-3 translation worker

```text
Translate this one `<category>` Level-3 page using `.agents/skills/wiki-publisher/SKILL.md`.

Input:
- `external/vulkancts/wiki/testfiles/<category>/<file>.md`

Output:
- `vkcts-wiki-pages/categories/<category>/<file>.md`

Do not assign an `*_brief.md` file. Read and translate only the assigned page; do not edit any other English or Chinese page, shared
summary, or Git index. Strictly follow the skill's translation-worker requirements. Load and apply `shuorenhua` then `humanizer-zh`
yourself; do not dispatch another language-review agent or launch a separate chat, session, or process. After both passes, run:

`python3 .agents/skills/wiki-publisher/scripts/verify_translation_structure.py --source external/vulkancts/wiki/testfiles/<category>/<file>.md --target vkcts-wiki-pages/categories/<category>/<file>.md`

Do not run link conversion. Return the exact source/target paths, validator result, and language-pass status. When complete, use
`attempt_completion`.
```

## Link-conversion worker

```text
Run the publish link-conversion phase for the completed `<category>` translations using
`.agents/skills/wiki-publisher/SKILL.md`.

Inputs:
- `vkcts-wiki-pages/categories/<category>.md`
- all `vkcts-wiki-pages/categories/<category>/*.md`

Strictly follow the skill's link-conversion requirements. Do not translate content. When complete, use `attempt_completion`.
```
