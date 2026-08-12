# Understanding Brief: signal-order synchronization tests

## One-sentence test purpose

These tests check that writes recorded in a sequence of queue submissions become visible to reads that wait only for the final signal, for both legacy synchronization and synchronization2, with binary/timeline semaphores and optional cross-device sharing.

## Background knowledge

A queue submission orders its command execution and semaphore signal operations. The test deliberately puts each of twelve writes in a separate submit entry, then waits on the final signal before executing all reads. That wait is useful only when the implementation preserves the required signal ordering and the submission's synchronization scopes make each write visible to its matching read.

Binary semaphores provide one signal/wait event per iteration. Timeline semaphores provide one semaphore with increasing values; the host signals the initial value to release the chain. `SynchronizationWrapper` selects the legacy submit commands or synchronization2 submit commands from `SynchronizationType`.

The shared families use two logical devices. Exported memory is imported by the second device, and the final semaphore is exported/imported. Only reference-semantics semaphore handles are used: opaque FD, opaque Win32 KMT, and opaque Win32. Sync-fd handles are intentionally excluded because their one-shot/copy semantics are unsuitable for this sequence.

## Concrete example

A binary case creates twelve resources and write/read operation pairs. Queue A submits write 0 through write 11 in separate `VkSubmitInfo` entries, each signaling its own semaphore. Queue B submits one command buffer containing reads 0 through 11 and waits only for semaphore 11. If signal ordering and visibility are correct, every read observes its corresponding write even though the first eleven semaphores are not waited on individually.

## What the source enumerates

- 19 write operations and 30 read operations are listed directly in each signal-order group. A case is created only when the selected resource supports both operations.
- Non-shared leaves are `<resource>` below `<writeOp>_<readOp>`.
- Shared leaves append the external semaphore handle name: `<resource>_<externalSemaphoreType>`.
- The resource list comes from `s_resources` in `vktSynchronizationOperationTestData.hpp`; it is a compatibility filter, not a fixed promise that every operation pair has every resource.

## End-to-end flow

```text
select category/API type, semaphore family, operation pair, and compatible resource
check timeline, synchronization2, queue, external-memory, and external-semaphore support
create twelve write/read operation instances and command buffers
record one write plus a write-to-read barrier per command buffer
submit all writes in one queue-submit call as twelve ordered submit entries
record all reads in one command buffer; wait only on the final write signal
for shared cases, export/import resources and the final semaphore across devices
wait for the read completion and compare expected versus actual operation data
wait for device idle before teardown
```

## Oracles and failure interpretation

Buffer/image results are compared with `deMemCmp`. Indirect-buffer reads pass when the observed counter is at least the expected value. A mismatch can indicate signal ordering, synchronization scope/stage/access handling, resource ownership/import, or the operation itself; it is not by itself proof of one specific Vulkan defect. A missing second queue or unsupported external handle is a support skip, not a result failure.

## Source evidence to preserve in the final page

- `createSignalOrderTests()` registers the four direct families.
- `QueueSubmitSignalOrderTests::init()` and `QueueSubmitSignalOrderSharedTests::init()` define the operation cross-product, resource filtering, and shared handle cases.
- `QueueSubmitSignalOrderTestInstance::iterate()` implements twelve ordered writes followed by one final-signal wait.
- `QueueSubmitSignalOrderSharedTestInstance::iterate()` implements the two-device export/import path.
- `SynchronizationWrapper` in `vktSynchronizationUtil.hpp` selects legacy versus synchronization2 submission/barrier commands.

## Audit cautions

- The source's signal-order arrays are not the same as the full `s_writeOps`/`s_readOps` arrays in the general operation-data header; document the values actually enumerated here.
- The page must name both exact roots, `synchronization.signal_order` and `synchronization2.signal_order`, rather than implying one category.
- The final signal orders execution; the page should not claim that merely waiting on a semaphore automatically replaces every required memory dependency. The source records explicit write-to-read barriers.
