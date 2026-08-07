# Repository Agent Instructions

## Global skill safety

- The repository-local `.agents/skills/` directory is the canonical workflow source for VK-GL-CTS Wiki work.
- Existing global skills may be read when relevant or explicitly required, including approved language and style gates.
- Never create, edit, patch, delete, or add supporting files to a global skill under `$HERMES_HOME/skills/` unless the user explicitly requests a global skill-library change in the current conversation.
- In particular, never create global skills specific to VK-GL-CTS, Vulkan CTS Wiki, wiki rewriting, source-backed wiki audit, translation, publishing, or this repository's pipeline.
- Do not automatically save a successful task, reusable workflow, correction, or debugging procedure as a global skill. Report the candidate workflow to the user instead.
- Do not use `skill_manage` write actions (`create`, `edit`, `patch`, `delete`, `write_file`, or `remove_file`) without the explicit authorization described above.
- Subagent prompts must preserve these rules. A worker may read approved existing global skills, but it must not create or modify global skills.

## VK-GL-CTS Wiki boundaries

- Follow the applicable repository-local workflow under `.agents/skills/`.
- Preserve the user's Git index and the phase boundary between staged rewrite output and unstaged audit repairs.
- During audit, source code, mustpass files, specifications, briefs, legacy pages, shared summaries, and the Git index are read-only unless the user explicitly authorizes otherwise.
- A source defect discovered during documentation audit must be reported as unresolved; documentation workers must not modify C or C++ source.
- Do not access or modify `vkcts-wiki-pages/` before explicit publishing authorization.
