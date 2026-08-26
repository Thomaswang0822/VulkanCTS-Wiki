# Phase Input Contracts

This reference defines only what the lead agent supplies to each primary skill. The primary skill remains the canonical owner of how that phase is executed.

## Rewrite: one Level-3 page

Supply:

- repository root and category;
- approved rewrite-outline path and the assigned batch entry;
- exactly one obsolete Level-3 page, read-only;
- exactly one rewritten output path;
- owning implementation source and relevant support files;
- relevant registration and mustpass evidence;
- exact page-scoped completion commands from `wiki-rewriter/references/validation-checklist.md` for English structure,
  Registration Hierarchy/mustpass validation, and wiki links;
- source-backed no-walkthrough status: either a required `shader-analyzer` walkthrough or an existing/lead-approved entry in
  `wiki-rewriter/scripts/walkthrough_exceptions.py`; workers must not create an exception merely to make validation pass;
- the outline's `brief required` or `direct rewrite` decision;
- dispatcher-folding or page-specific scope notes from the outline;
- explicit permission to write only the assigned brief, when required, and assigned rewritten page;
- explicit prohibition on modifying/deleting the obsolete page, editing summaries, translating, publishing, or changing the Git index.

Tell the worker to load `.agents/skills/wiki-rewriter/SKILL.md` and every dependency it requires. Do not restate its internal rewrite,
shader, language-pass, template, or validator rule implementations. Require the worker result to report English structure,
registration, and link validator status for its assigned page.

A required Understanding Brief and its final rewrite stay with the same page worker. They do not make the worker a multi-page worker.

## Rewrite: Level-2 synthesis

This is lead-owned. Perform it only after every Level-3 page is stable. Supply the primary rewriter workflow with:

- approved outline;
- obsolete Level-2 page;
- every stabilized rewritten Level-3 page;
- registration-only dispatcher source and its fold/no-fold decision;
- category mustpass hierarchy;
- repeated Level-3 Background Knowledge concepts requiring consolidation.

After drafting the ordinary gateway sections, run the category Background Knowledge consolidation required by wiki-rewriter. Revalidate affected Level-3 upward links and the Level-2 page.

Before declaring Level-3 input stable for synthesis, the lead runs the category-scoped English structure and registration validators.
After synthesis and Background Knowledge consolidation, run the category wiki-link command from the canonical validation checklist
against the new Level-2 page and all Level-3 pages. Level-2 synthesis does not waive failed Level-3 gates.

## Audit: one Level-3 page

Supply:

- repository root and category;
- exactly one rewritten Level-3 page;
- its owning implementation source and support files;
- relevant registration, mustpass, and Vulkan specification evidence;
- current page-scoped English structure, registration hierarchy, and wiki-link validator commands and starting results;
- `.agents/skills/wiki-auditor/SKILL.md` and its required references;
- write scope limited to the assigned page;
- explicit prohibition on editing the combined audit summary, other pages, publish outputs, or the Git index;
- the auditor worker result contract.

Require the worker to correct confirmed meaningful defects in place, rerun all three page-scoped English validators after any edit,
and return either compact findings or `no-confirmed-issues` together with those validator results.

## Audit: Level-2 and category aggregation

These are lead-owned:

- audit Level-2 Background Knowledge before judging Level-3 Background Knowledge ownership;
- create the category audit summary before the first Level-3 audit wave;
- append completed worker results after each wave;
- reconcile recurring patterns after all Level-3 pages finish;
- audit the complete Level-2 page;
- run category validation and finalize the summary.

Do not infer counts from delegation size. Count actual page entries and findings in the finalized summary.

## Publish: one Level-3 page

Supply:

- exactly one audited English source page;
- exactly one Chinese publish target under `vkcts-wiki-pages/categories/<category>/`;
- `.agents/skills/wiki-publisher/SKILL.md` and the Level-3 dispatch template it owns;
- the exact canonical Chinese validator command for that English source/Chinese target pair;
- explicit prohibition on link conversion, English-source edits, shared-file edits, and Git-index changes.

The worker itself loads `translate-doc` and all dependencies required by wiki-publisher, including in-agent `shuorenhua` followed by
`humanizer-zh`. Do not dispatch separate language-review agents. Require the worker to rerun the Chinese validator after the language
passes and return its result.

## Publish: Level-2 page

Supply the audited Level-2 source and its exact target `vkcts-wiki-pages/categories/<category>.md` using wiki-publisher's Level-2 dispatch template. Keep all other boundaries identical to Level-3 publishing.

## Link conversion

Run only after all translation outputs exist and pass structural and target-language checks. Follow wiki-publisher's link-conversion contract exactly. Convert each publishable file individually; `home.md` remains outside publish scope.

## Lookup DB update

After publication and link verification, supply `db-lookup-updater` with:

- the completed category and current rewrite-checklist state;
- the audit-stable English Level-3 page set;
- exact category mustpass inputs and current case-lookup registry state;
- the pre-update `site/mappings.json` counts/hash;
- permission to edit only evidence-backed English ownership defects, lookup registry/handlers/tests, tracked runtime JSON, and related
  lookup documentation;
- explicit prohibition on CTS source/mustpass edits, fallback ownership, Git-index changes, commit, or push.

No third hard stop applies. If an English page changes during lookup repair, feed that page back through English validation and the
single-page publisher, then reconvert/revalidate its Chinese target before accepting the final lookup build.
