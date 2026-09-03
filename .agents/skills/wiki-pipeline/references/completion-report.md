# Completion Report

Use this compact structure. Replace every count with independently verified filesystem or validator output.

```markdown
## <category> category complete

### Scope
- Level-3 written: <N>
- Level-2 written: <N>
- Understanding Briefs: <N>
- Chinese publish-target pages prepared: <N>

### Writing
- Outline: <path and approval status>
- Outline batches: <batch count and page counts>
- Worker granularity: one page per worker
- English structure validation: <N>/<N> pages; category <result>
- Registration hierarchy validation: <N>/<N> pages; category <result>
- English wiki-link validation: <N>/<N> pages; category/Level-2 <result>

### Audit
- Pages audited: <N>
- Pages edited: <N>
- Confirmed findings: <N>
- Pages with no confirmed issues: <N>
- Audit summary: <path>
- Post-audit English structure: <result>
- Post-audit registration hierarchy: <result>
- Post-audit wiki links: <result>

### Local publish target
- Chinese structure/fixed-language validation: <N>/<N> Level-3 source/target pairs
- Target-language check: <result>
- Link conversion: <N>/<N>
- Idempotency: <result>
- Git state: local working-tree changes only; no stage/commit/push
- Checklist: <result and updated totals>

### Lookup DB
- Category build: <result; leaves/mappings/owner pages>
- Full runtime index: <category count and mapping count>
- Mustpass runtime coverage: <passed>/<total>
- Lookup tests: <result>
- Tracked mappings JSON: <reviewed delta/result>
- Post-preparation ownership repair loop: <affected pages or none; local regeneration result>

### Safety
- Audited English pages during publish-target preparation: unchanged
- Git index: unchanged
- Git commit/push: not performed
- Unauthorized paths: none, or describe and escalate

### Recovery
- Failed/retried pages: <list or none>
- Terminal provider blockers: <none or provider error class and affected pages>
- Final retry result: <result>
```

Do not claim a page, phase, count, or side effect from a worker report alone. Verify it before including it here. If the process is incomplete, report the blocker and stop short of a completion claim.
