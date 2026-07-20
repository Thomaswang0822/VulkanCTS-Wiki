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

Strictly follow the skill's translation-worker requirements. Do not run link conversion. When complete, use `attempt_completion`.
```

## Level-3 translation worker

```text
Translate this `<category>` Level-3 page batch using `.agents/skills/wiki-publisher/SKILL.md`.

Inputs:
- `external/vulkancts/wiki/testfiles/<category>/<file1>.md`
- `external/vulkancts/wiki/testfiles/<category>/<file2>.md`
- `external/vulkancts/wiki/testfiles/<category>/<file3>.md`

Outputs:
- `vkcts-wiki-pages/categories/<category>/<file1>.md`
- `vkcts-wiki-pages/categories/<category>/<file2>.md`
- `vkcts-wiki-pages/categories/<category>/<file3>.md`

Do not assign `*_brief.md` files. Strictly follow the skill's translation-worker requirements. Do not run link conversion. When
complete, use `attempt_completion`.
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
