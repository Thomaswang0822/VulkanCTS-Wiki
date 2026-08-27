## Overview

The `reconvergence` test category collects tests that check how shader invocations reconverge and how terminated invocations affect later subgroup and quad behavior.

## Background Knowledge

- **Subgroup operations.** Subgroup elect, ballot, vote, and quad operations observe the invocations that are active for the operation. Ballots represent that active set as a bit mask, while elect and vote operations reduce information from it. Both rewritten Level-3 pages use these observations to distinguish correct control-flow behavior from incorrect participation after divergence or termination.
- **Invocation termination.** `terminateInvocation` ends the current invocation before it executes later instructions. The generated maximal-reconvergence case and the dedicated termination family both use operations after termination to check which invocations remain eligible to contribute.
- **Helper invocations and maximal reconvergence.** Fragment helper invocations support derivative and quad-related shader behavior but do not represent ordinary framebuffer results. Maximal reconvergence can keep helpers active for their quad scope until an invocation terminates, so tests that combine helper status, subgroup operations, and termination must distinguish active shader participation from framebuffer output.

## Category Structure

```text
reconvergence
├── subgroup_uniform_control_flow_elect
├── subgroup_uniform_control_flow_ballot
├── workgroup_uniform_control_flow_elect
├── workgroup_uniform_control_flow_ballot
├── maximal
└── terminate_invocation
```

The five generated reconvergence families are implemented together. `terminate_invocation` is a separate test family delegated to its own Level-3 page.

## How the Families Fit Together

The families use related observations of active shader invocations, but vary the control-flow contract or the operation performed after termination.

- The two subgroup-uniform families check subgroup-uniform control flow with either election or ballot observations.
- The two workgroup-uniform families apply the same observation split to workgroup-uniform control flow.
- `maximal` checks maximal reconvergence, including generated cases and fixed fragment cases that observe termination and demotion.
- `terminate_invocation` focuses on four fragment test cases that observe termination through subgroup population, helper votes, an unreachable memory access, and a quad vote.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `subgroup_uniform_control_flow_elect` | [Reconvergence.md](../testfiles/reconvergence/Reconvergence.md) | How generated subgroup-uniform control flow is checked with elect observations. |
| `subgroup_uniform_control_flow_ballot` | [Reconvergence.md](../testfiles/reconvergence/Reconvergence.md) | How generated subgroup-uniform control flow is checked with ballot masks. |
| `workgroup_uniform_control_flow_elect` | [Reconvergence.md](../testfiles/reconvergence/Reconvergence.md) | How generated workgroup-uniform control flow is checked with elect observations. |
| `workgroup_uniform_control_flow_ballot` | [Reconvergence.md](../testfiles/reconvergence/Reconvergence.md) | How generated workgroup-uniform control flow is checked with ballot masks. |
| `maximal` | [Reconvergence.md](../testfiles/reconvergence/Reconvergence.md) | Generated maximal-reconvergence cases and fixed fragment cases involving termination or demotion. |
| `terminate_invocation` | [TerminateInvocation.md](../testfiles/reconvergence/TerminateInvocation.md) | The four fragment cases and their post-termination subgroup, memory, helper, and quad checks. |