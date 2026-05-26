# vktAmberGraphicsFuzzTests.cpp

## Overview

[`vktAmberGraphicsFuzzTests.cpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L1-L52) is the registered
source file for the Vulkan CTS `graphicsfuzz` category. The root is registered from the Vulkan test package as
`dEQP-VK.graphicsfuzz` through [`addRootChild("graphicsfuzz", ...)`](../../../modules/vulkan/vktTestPackage.cpp#L1380-L1382),
and the package includes the Amber GraphicsFuzz factory header at
[`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L106-L108).

The implementation is intentionally compact: it creates the category group with the name supplied by root registration and
populates that group from `data/vulkan/amber/graphicsfuzz/index.txt` by calling
[`createAmberTestsFromIndexFile()`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49). The inspected index
contains 757 entries, and the mustpass file contains the same 757 `dEQP-VK.graphicsfuzz.*` registered names, though not in
identical order ([`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757),
[`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757)).

## Role

Registration wrapper for Amber GraphicsFuzz tests. This source file does not define each test case inline; instead, the
shared Amber index parser reads triples of `.amber` filename, registered test name, and description, plus optional
requirements, then adds an [`AmberTestCase`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169) to the group.

## Source Code

- Primary source: [`vktAmberGraphicsFuzzTests.cpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L1-L52)
- Header: [`vktAmberGraphicsFuzzTests.hpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.hpp#L1-L41)
- Root package registration: [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L106-L108),
  [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1380-L1382)
- Shared index parser: [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L100-L189)
- Shared Amber execution support: [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L193-L286),
  [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432),
  [`vktAmberTestCase.cpp`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)
- Amber data directory: [`graphicsfuzz/`](../../../data/vulkan/amber/graphicsfuzz/)
- Mustpass list: [`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757)

## Registration Hierarchy

```text
graphicsfuzz
├── access-new-vector-inside-if-condition
├── always-discarding-function
├── always-false-if-in-do-while
├── always-false-if-with-discard-return
├── arr-value-set-to-arr-value-squared
├── array-idx-multiplied-by-for-loop-idx
├── assign-array-value-to-another-array
├── assign-array-value-to-another-array-2
├── barrier-in-loop-with-break
├── break-in-do-while-with-nested-if
├── call-function-with-discard
├── call-if-while-switch
├── color-set-in-for-loop
├── color-write-in-loop
├── complex-nested-loops-and-call
├── conditional-return-in-infinite-while
├── continue-and-merge
├── control-flow-in-function
├── control-flow-switch
├── cosh-return-inf-unused
├── cov-access-array-dot
├── cov-analysis-reachable-from-many
├── cov-and-even-numbers-from-fragcoord
├── cov-apfloat-acos-ldexp
├── cov-apfloat-determinant
├── cov-apfloat-mix-nan
├── cov-apfloat-mod-zero
├── cov-apfloat-module-small-number
├── cov-apfloat-negative-step-func
├── cov-apfloat-sinh-negative-log2
├── cov-apfloat-tanh
├── cov-apfloat-undefined-matrix-mul
├── cov-apfloat-determinant-for-if
├── cov-apfloat-reflect-denorm
├── cov-apfloat-unpackunorm-loop
├── cov-array-accesses-clamp
├── cov-array-cast-bool-float-div-by-zero-no-effect
├── cov-array-copies-loops-with-limiters
├── cov-array-set-element-condition-negative-modulus
├── cov-asin-undefined-smoothstep
├── cov-atan-trunc-vec4
├── cov-basic-block-discard-in-function
├── cov-bitcount
├── cov-bitfieldExtract-undefined
├── cov-bitfieldinsert-undefined
├── cov-bitfieldreverse-left-shift-findmsb
├── cov-bitfieldreverse-loop-limit-underflow
├── cov-bitwise-and-variable-and-its-negation
├── cov-bitwise-inverse-uniform-condition
├── cov-bitwise-or-uniform-zero-tenth-bit-loop-limit-find-lsb
├── cov-bitwise-shift-right-always-select-one
├── cov-bitwise-shift-right-full-bits-no-effect-clamp
├── cov-blockfrequency-several-for-loops
├── cov-branch-probability-identity-matrix
├── cov-cast-float-to-int-and-back
├── cov-clamp-loop-limit-increment-float-array
├── cov-clamp-lower-limit-from-always-false
├── cov-clamp-min-bitcount-uniform
├── cov-clamp-value-and-min-select-uniform
├── cov-clamp-vector-component-condition-using-matrix
├── cov-clamp-vector-element-ceil-negative
├── cov-clamp-vector-variable-negative-offset
├── cov-clear-yz-inside-condition
├── cov-color-output-undefined-in-unexecuted-branch
├── cov-combine-and-or-xor-gt-lt
├── cov-condition-bitfield-extract-integer
├── cov-condition-clamp-min-from-uniform-never-larger
├── cov-condition-increment-zero-to-one-divide-by-two
├── cov-condition-loop-index-bitwise-not
├── cov-condition-matrix-determinant-uniform
├── cov-conditional-discard-inside-loop
├── cov-conditions-empty-blocks-index-array-one-divided-by-findlsb
├── cov-const-folding-bitfieldinsert-div-one
├── cov-color-overwrite-identity-matrix-multiply
├── cov-const-folding-ceil-vec4
├── cov-const-folding-clamp
├── cov-const-folding-clamp-inside-while
├── cov-const-folding-clamp-max
├── cov-const-folding-clamp-min
├── cov-const-folding-clamp-vs-original
├── cov-const-folding-det-identity
├── cov-const-folding-dot-condition-true
├── cov-const-folding-dot-determinant
├── cov-const-folding-gte-const-first
├── cov-const-folding-min-as-loop-range
├── cov-const-folding-mod-one-one-lte
├── cov-const-folding-pow-large-exp
├── cov-const-folding-same-condition
├── cov-const-folding-sinh-inf
├── cov-const-folding-vector-shuffle
├── cov-constant-folding-atan-over-tanh
├── cov-constants-combine-add-sub
├── cov-constants-mix-uniform
├── cov-continue-break-discard-return-in-loop
├── cov-copy-array-elements-except-first-nested-loop-replace-identical-values
├── cov-copy-output-color-swizzle-array-indexing
├── cov-copy-prop-arrays-no-stores
├── cov-copy-prop-arrays-param-uniform
├── cov-cosh-clamped-to-one
├── cov-cumulate-loops-unreachable
├── cov-dag-combiner-clamp-undefined-access-array
├── cov-dag-combiner-combine-casts-legalize-vector-types-xyz-swizzle-for-loop
├── cov-dag-combiner-findmsb-loop
├── cov-dag-combiner-increment-color
├── cov-dag-combiner-glf_color
├── cov-dag-combiner-loop-bitfieldreverse
├── cov-dag-combiner-neg-div-pow2
├── cov-dag-combiner-same-cond-nested
├── cov-dead-branch-func-return-arg
├── cov-dead-code-unreachable-merge
├── cov-decrement-vector-elements-clamp-index
├── cov-derivative-uniform-vector-global-loop-count
├── cov-descending-loop-index-temporary-array
├── cov-descending-loop-min-max-always-zero
├── cov-determinant-uninitialized-matrix-never-chosen
├── cov-dfdx-dfdy-after-nested-loops
├── cov-discard-condition-loop-same-condition-again
├── cov-divide-matrix-transpose-by-constant
├── cov-do-while-loop-until-uniform-lt-itself
├── cov-do-while-negative-iterator-nested-loops-increment-array-element
├── cov-do-while-switch-case-bitcount-findmsb
├── cov-double-if-true-in-loop
├── cov-double-negation-fragcoord-cast-ivec2-bitwise-and
├── cov-dummy-function-loop-array-element-increment-never-read
├── cov-empty-loop-minus-one-modulo-variable-one
├── cov-enable-bits-pixel-location-negate-not-equal-one
├── cov-exp2-two
├── cov-extend-uniform-vec2-to-vec3-matrix-multiply
├── cov-find-msb-input-either-zero-or-minus-one
├── cov-findlsb-division-by-zero
├── cov-float-array-init-pow
├── cov-fold-and-in-for-loop-range
├── cov-fold-bitwise-and-zero
├── cov-fold-bitwise-or-full-mask
├── cov-fold-bitwise-xor
├── cov-fold-logical-and-const-variable
├── cov-fold-logical-and-constant
├── cov-fold-logical-or-constant
├── cov-fold-negate-min-int-value
├── cov-fold-negate-variable
├── cov-fold-shift-gte32
├── cov-fold-shift-right-arithmetic
├── cov-fold-switch-udiv
├── cov-folding-clamp-cmp-const-first
├── cov-folding-merge-add-sub-uniform
├── cov-folding-rules-construct-extract
├── cov-folding-rules-dot-extract
├── cov-folding-rules-dot-no-extract
├── cov-folding-rules-merge-add-sub
├── cov-folding-rules-merge-div-mul
├── cov-folding-rules-merge-divs
├── cov-folding-rules-merge-mul-div
├── cov-folding-rules-merge-sub-add
├── cov-folding-rules-merge-sub-sub
├── cov-folding-rules-merge-var-sub
├── cov-folding-rules-mix-uniform-weight
├── cov-folding-rules-negate-div
├── cov-folding-rules-negate-sub
├── cov-folding-rules-redundant-mix
├── cov-folding-rules-shuffle-extract
├── cov-folding-rules-shuffle-mix
├── cov-folding-rules-split-vector-init
├── cov-folding-rules-vec-mix-uniform
├── cov-for-array-initializing-modulo
├── cov-for-loop-condition-one-shift-right-integer-comparison-break
├── cov-for-loop-min-increment-array-element
├── cov-for-loop-start-negative-increment-variable
├── cov-for-loop-struct-as-iterator
├── cov-for-switch-fallthrough
├── cov-fract-asin-undefined-never-used
├── cov-fract-smoothstep-undefined
├── cov-fract-trunc-always-zero
├── cov-fragcood-multiple-conditions-function-loop-global-counter
├── cov-fragcoord-and-one-or-same-value
├── cov-fragcoord-bitwise-and-loop-reduce-value-index-array
├── cov-fragcoord-bitwise-not
├── cov-fragcoord-clamp-array-access
├── cov-fragcoord-conditions-never-return-index-array-using-uniform
├── cov-fragcoord-integer-loop-reduce-to-range
├── cov-fragcoord-loop-limit-negative-decrease-sum-first-iteration
├── cov-fragcoord-multiple-conditions-function-global-loop-counter-simplified
├── cov-fragcoord-multiply
├── cov-fragcoord-select-always-one
├── cov-function-always-return-negative-bitfield-extract
├── cov-function-argument-uniform-float-loop-never-return
├── cov-function-check-argument-one-always-return-minus-one
├── cov-function-clamp-min-identical-shift-right
├── cov-function-call-twice-clamp-global-variable
├── cov-function-divide-argument-until-lt-one
├── cov-function-find-lsb-ivec2-one
├── cov-function-fragcoord-condition-always-return
├── cov-function-global-loop-counter-sample-texture
├── cov-function-global-variables-fragcoord-condition-call-twice
├── cov-function-index-array-redundant-clamps
├── cov-function-infinite-loop-always-return
├── cov-function-infinite-loop-return-identical-condition
├── cov-function-large-array-max-clamp
├── cov-function-large-loop-always-return-first-iteration
├── cov-function-large-loop-break-argument-lte-global-loop-bound
├── cov-function-loop-check-determinant-zero-return-vector
├── cov-function-loop-clamp-no-effect
├── cov-function-loop-condition-constant-array-always-false
├── cov-function-loop-condition-uniform-shift-right
├── cov-function-loop-condition-variable-less-than-min-itself
├── cov-function-loop-copy-array-elements-based-on-arguments
├── cov-function-loop-modify-ivec-components-infinite-loop-never-executed
├── cov-function-loop-same-conditions-multiple-times-struct-array
├── cov-function-loop-switch-increment-array-element-return
├── cov-function-max-all-ones-select-always-true
├── cov-function-min-identical-integer-division-multiplication
├── cov-function-min-integer-large-shift-unused
├── cov-function-loop-variable-multiplied-unused
├── cov-function-loops-vector-mul-matrix-never-executed
├── cov-function-multiple-loops-compare-integer-return
├── cov-function-nested-do-whiles-looped-once
├── cov-function-nested-loops-break-early-never-discard
├── cov-function-nested-loops-limit-uniform-xor-uniform
├── cov-function-set-struct-field-zero-loop-reset-first-element
├── cov-function-parameter-zero-divided-by-uniform
├── cov-function-round-unpack-half-2x16
├── cov-function-struct-int-array-loop-check-element
├── cov-function-switch-case-constant-clamp-transpose-identity-matrices
├── cov-function-trivial-switch-case
├── cov-function-two-loops-limit-using-arguments-array-element-copies
├── cov-function-undefined-shift-left-index-array-with-return-value
├── cov-function-unpack-unorm-2x16-one
├── cov-function-unused-argument-single-loop-iteration-icrement-global-counter
├── cov-function-variable-plus-one-minus-one
├── cov-function-vec2-never-discard
├── cov-function-with-nested-loops-called-from-nested-loops
├── cov-global-loop-bound-true-logical-or
├── cov-global-loop-count-array-struct-field-set-int-array-element
├── cov-global-loop-counter-accumulate-integer-condition-large-array-elements
├── cov-global-loop-counter-exhaust-calling-function-twice
├── cov-global-loop-counter-findlsb-zero
├── cov-global-loop-counter-float-accumulate-matrix
├── cov-global-loop-counter-for-loop-function-call-inside-never-called
├── cov-global-loop-counter-main-function-call
├── cov-global-loop-counter-multiply-one-minus
├── cov-global-loop-counter-read-past-matrix-size-never-executed
├── cov-global-loop-counter-select-one-or-zero-never-greater-than-one
├── cov-global-loop-counter-set-array-element-once-index-using-findmsb
├── cov-global-loop-counter-squared-comparison
├── cov-global-loop-counter-texture-sample-loop-condition-set-array-element
├── cov-if-conversion-identical-branches
├── cov-if-switch-fallthrough
├── cov-if-true-continue
├── cov-if-true-discard-in-do-while-never-reached
├── cov-if-true-float-bits-to-int-one
├── cov-inc-array-element-loop-lsb
├── cov-inc-inside-switch-and-for
├── cov-increment-array-element-in-loop
├── cov-increment-array-element-usub-borrow
├── cov-increment-float-in-loop-abs
├── cov-increment-global-counter-loop-function
├── cov-increment-inside-clamp
├── cov-increment-int-loop-counter-mod-array
├── cov-increment-multiple-integers
├── cov-increment-one-array-element-check-index-from-fragcoord
├── cov-increment-vector-array-matrix-element
├── cov-increment-vector-component-with-matrix-copy
├── cov-increment-vector-function-call-conditional
├── cov-index-array-using-uniform-bitwise-or-one
├── cov-initialize-integer-array-variable-divided-by-itself
├── cov-inline-pass-empty-block
├── cov-inline-pass-nested-loops
├── cov-inline-pass-return-in-loop
├── cov-inline-pass-unreachable-func
├── cov-inst-combine-add-sub-ldexp
├── cov-inst-combine-add-sub-pre-increase
├── cov-inst-combine-compares-while-modulo
├── cov-inst-combine-shifts-left-shift-for
├── cov-inst-peephole-optimizer-acosh
├── cov-inst-value-tracking-inversesqrt
├── cov-instr-emitter-pow-asinh
├── cov-instruction-simplify-atanh-log-undefined
├── cov-instruction-simplify-bit-shifting
├── cov-instruction-simplify-inclusive-or
├── cov-instruction-simplify-inst-combine-calls-for-compare-function-call-result
├── cov-instruction-simplify-mod-acos-undefined
├── cov-instruction-simplify-mod-sqrt-undefined
├── cov-instruction-simplify-sqrt
├── cov-instructions-first-value-phi
├── cov-inst-combine-add-sub-determinant
├── cov-inst-combine-add-sub-increase-negative
├── cov-inst-combine-add-sub-neg-func-arg
├── cov-inst-combine-and-or-xor-pack-unpack
├── cov-inst-combine-and-or-xor-switch
├── cov-inst-combine-and-or-xor-xor-add
├── cov-inst-combine-compares-combine-select-uaddcarry
├── cov-inst-combine-compares-isnan
├── cov-inst-combine-compares-ldexp
├── cov-inst-combine-compares-ternary-vector-access
├── cov-inst-combine-shifts-bitfield-bitcount
├── cov-inst-combine-shifts-mix-mix-clamp
├── cov-instr-info-det-mat-min
├── cov-instructions-for-if-less-than-equal
├── cov-inst-combine-and-or-xor-for-bitfieldinsert
├── cov-inst-combine-compares-pre-increment-clamp
├── cov-inst-combine-mul-div-rem-if-undefined-divide-mix
├── cov-inst-combine-pack-unpack
├── cov-inst-combine-select-findlsb-uaddcarry
├── cov-inst-combine-simplify-demanded-pack-unpack
├── cov-inst-combine-simplify-demanded-packsnorm-unpackunorm
├── cov-inst-combine-simplify-demanded-switch-or-xor
├── cov-inst-combine-vector-ops-asin
├── cov-int-div-round-to-zero
├── cov-int-full-bits-divide-by-two-loop
├── cov-int-initialize-from-multiple-large-arrays
├── cov-integer-constant-mod-variable-increased-condition-array-element
├── cov-integer-minus-one-increased-before-indexing-array
├── cov-integer-modulo-negative
├── cov-integer-variable-or-with-inversion
├── cov-intervalmap-set-stop
├── cov-ir-builder-constant-fold-inst-combine-calls-value-tracking-findmsb-incr-if
├── cov-irbuilder-matrix-cell-uniform
├── cov-isnan-asinh-clamp-always-zero
├── cov-ivec-from-uniform-float-shift-right-add-components
├── cov-ivec-shift-right-by-large-number
├── cov-large-for-loop-exit-early-set-iterator-array-element
├── cov-large-int-array-nested-loops-set-ivec-index-component-sum
├── cov-large-loop-break-early-condition-iterator-divided
├── cov-large-loop-multiply-integer-by-uniform-one
├── cov-large-number-of-false-conditions-return-discard-continue
├── cov-ldexp-exponent-undefined-divided-fragcoord-never-executed
├── cov-ldexp-undefined-mat-vec-multiply
├── cov-left-shift-array-access
├── cov-left-shift-right-shift-compare
├── cov-liveinterval-different-dest
├── cov-loop-abs-multiply-offset
├── cov-loop-array-element-bitfield-insert-undefined-never-read
├── cov-loop-array-element-copy-index-clamp-sign
├── cov-loop-array-index-decrement-never-negative
├── cov-loop-array-struct-field-index-array-with-uniforms
├── cov-loop-break-after-first-iteration-set-array-element
├── cov-loop-break-floor-nan-never-executed
├── cov-loop-break-fragcoord-x-empty-loop
├── cov-loop-clamp-to-one-empty-condition
├── cov-loop-condition-bitfield-extract-set-array-elements
├── cov-loop-condition-clamp-vec-of-ones
├── cov-loop-condition-constant-struct-field-data
├── cov-loop-condition-divide-by-uniform-always-false
├── cov-loop-condition-double-negate
├── cov-loop-condition-filter-some-iterations-never-discard
├── cov-loop-condition-increment-integer-fallback-global-counter
├── cov-loop-condition-logical-or-never-iterated
├── cov-loop-decrease-integer-never-break
├── cov-loop-construct-vec4-from-vec4-clamp-same-min-max
├── cov-loop-decrease-vector-components-assign-multiple-times
├── cov-loop-decrease-vector-component-only-first-iteration
├── cov-loop-dfdx-constant-divide
├── cov-loop-exit-conditions-sampler-struct-integer-variable
├── cov-loop-divide-uninitialized-vector-min-unused
├── cov-loop-find-lsb-eight-fragcoord-never-discard
├── cov-loop-findmsb-findlsb
├── cov-loop-fragcoord-identical-condition
├── cov-loop-function-call-vector-matrix-multiplication
├── cov-loop-global-counter-break-set-ivec-elements
├── cov-loop-function-call-negative-argument
├── cov-loop-global-counter-increment-iterator-select-uniform
├── cov-loop-increase-iterator-condition-uniform-copy-array-elements
├── cov-loop-increment-array-elements-clamp-index
├── cov-loop-increment-array-index-array-usuborrow-feedback
├── cov-loop-increment-integer-findmsb-minus-uniform
├── cov-loop-increment-integer-set-output-color-break
├── cov-loop-increment-matrix-element-break-after-first-iteration
├── cov-loop-increment-or-divide-by-loop-index
├── cov-loop-index-array-max-negative-zero
├── cov-loop-integer-half-minus-one
├── cov-loop-iterator-bitwise-negate
├── cov-loop-iterator-limit-xor-and-unifrom
├── cov-loop-iterator-plus-one-variable-outside-index-array
├── cov-loop-iterator-start-select-uniform-negative-integer
├── cov-loop-large-array-index-clamp-negative-value
├── cov-loop-iterator-start-shift-left-right
├── cov-loop-limiter-min-findlsb
├── cov-loop-limiter-uniform-bitwise-and-one-always-break
├── cov-loop-logical-xor
├── cov-loop-multiple-iterator-variables-copy-array-elements
├── cov-loop-never-iterated-constant-vector-condition
├── cov-loop-read-array-index-from-array-data
├── cov-loop-max-divide-integer-by-ten
├── cov-loop-overwrite-sample-texture-as-color-output
├── cov-loop-min-max-clamp-increment-only-first-iteration
├── cov-loop-replace-output-color-restore-original
├── cov-loop-returns-behind-true-and-false
├── cov-loop-sampled-texel-integer-counter
├── cov-loop-set-vector-components-pow-two
├── cov-loop-start-fragcoord-while-iterates-once
├── cov-loop-start-from-one-switch-case-invalid-color-never-executed
├── cov-loop-start-from-one-switch-case-never-executed
├── cov-loop-struct-array-field-set-value-self-dependency
├── cov-loop-switch-discard-never-hit
├── cov-loop-two-iterators-increment-array-empty-do-while
├── cov-loop-variable-less-than-itself
├── cov-loop-with-two-integers
├── cov-loops-and-conditions-fragcoord-always-false-floats-one
├── cov-loops-same-code-outside-loop
├── cov-machine-scheduler-for-if-pow
├── cov-machine-basic-block-for-for-for-less-than
├── cov-machinevaluetype-one-iter-loop
├── cov-matching-conditions-break
├── cov-matching-if-always-true-inside-loop
├── cov-matrix-double-transpose
├── cov-matrix-mult-round-even-asinh
├── cov-matrix-square-mul-with-vector
├── cov-max-clamp-same-minval
├── cov-max-min-less-than
├── cov-mem-pass-sum-struct-members
├── cov-mem-pass-unused-component
├── cov-merge-return-condition-twice
├── cov-min-identical-uint-uniform
├── cov-min-identical-uint-uniform-check-highest-bit
├── cov-min-intbitstofloat-undefined-never-used
├── cov-min-negative-constant-always-below-one
├── cov-min-nested-loop-same-value-for-variables
├── cov-min-vec2-transpose-mat2-identity
├── cov-missing-return-value-function-never-called
├── cov-mix-uninitialized-float-never-selected
├── cov-mix-uninitialized-vector-select-only-defined-data
├── cov-mod-acosh
├── cov-mod-uint-bits-float
├── cov-modf-clamp-for
├── cov-modf-integer-to-private
├── cov-modulo-zero-never-executed
├── cov-multiple-fragcoord-conditions-false-never-return-sample-texture
├── cov-multiple-fragcoord-conditions-never-return-color-uninitialized
├── cov-multiple-functions-global-never-change
├── cov-multiple-loops-same-condition-always-false-global-loop-counter
├── cov-multiple-one-iteration-loops-global-counter-write-matrices
├── cov-negative-integer-bitwise-or-uniform-increment-loop
├── cov-nested-functions-accumulate-global-matrix
├── cov-nested-functions-compare-fragcood-length-zero-vector
├── cov-nested-functions-loop-assign-global-array-element
├── cov-nested-functions-struct-arrays-vector-lengths
├── cov-nested-functions-vec4-array-element-argument
├── cov-nested-loop-continue-inner-copy-array-element
├── cov-nested-loop-decrease-vector-components
├── cov-nested-loop-initializer-value-increased-inside
├── cov-nested-loop-large-array-index-using-vector-components
├── cov-nested-loop-not-greater-than-increment-array-element
├── cov-nested-loop-undefined-smoothstep-never-executed
├── cov-nested-loops-assign-vector-elements-from-matrix-no-negative-indexing
├── cov-nested-loops-array-choose-red-last-iteration
├── cov-nested-loops-clamp-ivec-push-constant-increment-global-counter
├── cov-nested-loops-copy-array-elements-skip-first
├── cov-nested-loops-decrease-ivec-component
├── cov-nested-loops-different-iteration-rates-function-copy-array-elements
├── cov-nested-loops-divide-integer-constant-always-zero
├── cov-nested-loops-decrease-vector-component-by-matrix-element-global-loop-counter
├── cov-nested-loops-float-array-select-by-fragcoord
├── cov-nested-loops-float-bits-to-int-increment-array
├── cov-nested-loops-fragcoord-conditions-empty-blocks
├── cov-nested-loops-fragcoord-never-return-descending-loop
├── cov-nested-loops-global-counter-func-set-struct-field
├── cov-nested-loops-global-counter-increment-single-element
├── cov-nested-loops-global-loop-counter-do-while-accumulate-float
├── cov-nested-loops-global-loop-counter-fragcoord-negative-always-false
├── cov-nested-loops-global-loop-counter-index-array-vec2
├── cov-nested-loops-global-loop-counter-iterator-dependency
├── cov-nested-loops-global-loop-counter-output-color-from-backup
├── cov-nested-loops-global-loop-counter-reached-second-iteration
├── cov-nested-loops-identical-iterator-names-multiply-divide
├── cov-nested-loops-identical-iterators-compare-same-array-elements
├── cov-nested-loops-increase-integer-dot-product
├── cov-nested-loops-inner-loop-min-copy-array-elements
├── cov-nested-loops-iterator-times-two-while-min
├── cov-nested-loops-never-change-array-element-one
├── cov-nested-loops-redundant-condition
├── cov-nested-loops-return-inside-while-never-executed
├── cov-nested-loops-sample-opposite-corners
├── cov-nested-loops-select-starting-value-fragcoord
├── cov-nested-loops-set-struct-data-verify-in-function
├── cov-nested-loops-substract-matrix-element-change-float
├── cov-nested-loops-switch-case-fallthrough-increment-array-element
├── cov-nested-loops-temporary-copy-output-color-index-matrix
├── cov-nested-loops-while-min-iterator-condition-always-false
├── cov-nested-loops-switch-add-zero-matrix-elements
├── cov-nested-loops-while-condition-integer-range-increment-variable
├── cov-nested-structs-function-set-inner-struct-field-return
├── cov-nir-array-access
├── cov-nir-opt-large-constants-for-clamp-vector-access
├── cov-nir-opt-loop-unroll-if-if-if-if-do-while
├── cov-nouble-negation-fragcoord-cast-ivec2-bitwise-and
├── cov-one-bitwise-and-bitwise-or-full-bits
├── cov-one-minus-clamp-always-one-cast-to-int
├── cov-optimize-phis-for
├── cov-optimize-phis-for-for-do-while-if-if
├── cov-not-clamp-matrix-access
├── cov-packhalf-unpackunorm
├── cov-pattern-match-signum
├── cov-pattern-match-single-bit
├── cov-peephole-optimizer-target-instr-info-for-if-if-if
├── cov-pow-distance-uniform-vector-constant-one-vector
├── cov-pow-identical-value-sqrt
├── cov-pow-undefined
├── cov-pow-undefined-result-condition-with-always-true
├── cov-rcp-negative-int
├── cov-read-matrix-push-constant
├── cov-reciprocal-var-minus-one
├── cov-reduce-load-replace-extract
├── cov-register-coalescer-live-intervals-target-instr-info-for-discard-for-discard
├── cov-reinitialize-matrix-after-undefined-value
├── cov-repeating-conditions-fract-unused
├── cov-replace-copy-object
├── cov-return-after-do-while
├── cov-return-after-first-iteration
├── cov-return-partly-undefined-vector-from-array
├── cov-sample-texture-hundred-iterations
├── cov-sampler-as-function-argument
├── cov-scaled-number-nested-loops
├── cov-selection-dag-assign-back-and-forth
├── cov-selection-dag-lt-gt
├── cov-scaled-number-nested-loops-array-access
├── cov-schedule-dag-rrlist-mix-log-cos
├── cov-selection-dag-inverse-clamp
├── cov-selection-dag-same-cond-twice
├── cov-set-array-elements-to-uniform-check-value-break
├── cov-set-output-color-function-call-nested-loop
├── cov-set-vector-cos-fragcoord
├── cov-sign-array-access-uaddcarry
├── cov-simplification-unused-struct
├── cov-simplification-while-inside-for
├── cov-simplify-clamp-max-itself
├── cov-simplify-combine-compares-max-max-one
├── cov-simplify-component-uniform-idx
├── cov-simplify-div-by-uint-one
├── cov-simplify-for-bitwise-condition
├── cov-simplify-ldexp-exponent-zero
├── cov-simplify-max-multiplied-values
├── cov-simplify-modulo-1
├── cov-simplify-mul-identity
├── cov-simplify-not-less-than-neg
├── cov-simplify-right-shift-greater-than-zero
├── cov-simplify-select-fragcoord
├── cov-simplify-sign-cosh
├── cov-simplify-smoothstep-undef
├── cov-sin-mul-mat-mat-mul-vec-mat
├── cov-single-block-elim-self-assign
├── cov-single-store-elim-assume-store
├── cov-sinh-ldexp
├── cov-small-array-overwrite-most-uniform-value-check-data-break
├── cov-ssa-rewrite-case-with-default
├── cov-step-sinh
├── cov-struct-array-ivec-negative-modulus-empty-function
├── cov-struct-float-array-mix-uniform-vectors
├── cov-struct-int-array-select-uniform-ivec
├── cov-sum-uniform-vector-components-round
├── cov-switch-fallthrough-variable-from-first-case
├── cov-tail-duplicator-for-for-for
├── cov-tail-duplicator-infinite-loops
├── cov-target-lowering-dfdx-cos
├── cov-target-lowering-inst-combine-compares-struct-array-clamp-function-cal
├── cov-texel-double-negation
├── cov-transpose-multiply
├── cov-trunc-fract-always-zero
├── cov-two-functions-loops-copy-elements-infinite-loops-never-executed
├── cov-two-functions-modify-struct-array-element-return-from-loop
├── cov-two-loops-global-loop-counter-clamp-ivec-elements-index-array
├── cov-two-loops-global-loop-counter-shift-right-zero-increment-array-element
├── cov-two-loops-increment-integer-global-counter-break-square-threshold
├── cov-two-loops-never-iterated
├── cov-two-nested-loops-switch-case-matrix-array-increment
├── cov-types-return-in-main-never-hit
├── cov-uadd-carry-bit-count-index-array
├── cov-ucarryadd-one-and-one
├── cov-undefined-inversesqrt-reflect
├── cov-uniform-vector-copy
├── cov-uniform-vector-function-argument-mod-increment-integers
├── cov-uninitialized-values-passed-to-function-never-executed
├── cov-unpack-unorm-mix-always-one
├── cov-unused-access-past-matrix-elements
├── cov-unused-matrix-copy-inside-loop
├── cov-val-cfg-case-fallthrough
├── cov-value-inst-combine-select-value-tracking-flip-bits
├── cov-value-tracking-apint-inst-combine-simplify-one-mod-loop-iterator
├── cov-value-tracking-const-dfdy
├── cov-value-tracking-constant-fold-refraction-dfxd-determinant
├── cov-value-tracking-inclusive-or
├── cov-value-tracking-known-nonzero
├── cov-value-tracking-max-uintbitstofloat
├── cov-value-tracking-selection-dag-negation-clamp-loop
├── cov-value-tracking-uniform-incident
├── cov-variable-copy-in-function-tex-sample
├── cov-vec2-dot-max-uniform
├── cov-vec2-dot-minus-negative-zero
├── cov-vec2-duplicate-min-always-half
├── cov-vector-dce-inc-unused-comp
├── cov-vector-dce-unused-component
├── cov-vector-illegal-index-never-executed
├── cov-vector-log2-cosh
├── cov-wrap-op-kill-for-loop
├── cov-wrap-op-kill-two-branches
├── cov-write-past-matrix-elements-unused
├── cov-x86-instr-info-determinant-min
├── cov-x86-isel-lowering-determinant-exp-acos
├── cov-x86-isel-lowering-machine-value-type-uint-to-float
├── cov-x86-isel-lowering-selection-dag-struct-array-clamp-index
├── cov-x86-isel-lowering-apfloat-nan-cos-cos
├── cov-x86-isel-lowering-negative-left-shift
├── create-color-in-do-while-for-loop
├── dead-barriers-in-loops
├── dead-struct-init
├── disc-and-add-in-func-in-loop
├── discard-continue-return
├── discard-in-array-manipulating-loop
├── discard-in-loop
├── discard-in-loop-in-function
├── discards-in-control-flow
├── do-while-false-if
├── do-while-false-loops
├── do-while-if-return
├── do-while-loop-in-conditionals
├── do-while-with-always-true-if
├── do-while-with-if-condition
├── early-return-and-barrier
├── find-msb-from-lsb
├── flag-always-false-if
├── for-condition-always-false
├── for-loop-with-return
├── for-with-ifs-and-return
├── frag-coord-func-call-and-ifs
├── fragcoord-control-flow
├── fragcoord-control-flow-2
├── function-with-float-comparison
├── function-with-uniform-return
├── global-array-loops
├── if-and-switch
├── increment-value-in-nested-for-loop
├── injection-switch-as-comparison
├── int-mat2-struct
├── loop-call-discard
├── loop-dead-if-loop
├── loop-nested-ifs
├── loops-breaks-returns
├── loops-ifs-continues-call
├── mat-array-deep-control-flow
├── mat-array-distance
├── mat-mul-in-loop
├── matrices-and-return-in-loop
├── max-mix-conditional-discard
├── mix-floor-add
├── modf-gl-color
├── modf-temp-modf-color
├── nested-for-break-mat-color
├── nested-for-loops-switch-fallthrough
├── nested-for-loops-with-return
├── nested-ifs-and-return-in-for-loop
├── nested-loops-switch
├── nested-switch-break-discard
├── one-sized-array
├── pow-vec4
├── return-before-writing-wrong-color
├── return-float-from-while-loop
├── return-in-loop-in-function
├── return-inside-loop-in-function
├── returned-boolean-in-vector
├── set-color-in-one-iteration-while-loop
├── similar-nested-ifs
├── smoothstep-after-loop
├── spv-access-chains
├── spv-composite-phi
├── spv-composite2
├── spv-composites
├── spv-copy-object
├── spv-dead-break-and-unroll
├── spv-declare-bvec4
├── spv-double-branch-to-same-block
├── spv-double-branch-to-same-block2
├── spv-double-branch-to-same-block3
├── spv-load-from-frag-color
├── spv-null-in-phi-and-unroll
├── spv-stable-bifurcation-Os-mutate-var-vector-shuffle
├── spv-stable-bubblesort-flag-complex-conditionals
├── spv-stable-collatz-O-mutate-composite-construct-extract
├── spv-stable-colorgrid-modulo-O-move-block-down
├── spv-stable-maze-O-dead-code
├── spv-stable-maze-O-memory-accesses
├── spv-stable-maze-flatten-copy-composite
├── spv-stable-mergesort-O-prop-up-mutate-var
├── spv-stable-mergesort-dead-code
├── spv-stable-mergesort-flatten-selection-dead-continues
├── spv-stable-mergesort-func-inline-mutate-var
├── spv-stable-orbit-O-mutate-variable
├── spv-stable-orbit-Os-access-chain-mutate-pointer
├── spv-stable-pillars-O-op-select-to-op-phi
├── spv-stable-pillars-volatile-nontemporal-store
├── spv-stable-quicksort-dontinline
├── spv-stable-quicksort-mat-func-param
├── spv-stable-rects-Os-mutate-var-push-through-var
├── spv-stable-sampler-loop-extra-instructions
├── spv-stable-sampler-polar-simple-O-access-chain
├── stable-binarysearch-tree-false-if-discard-loop
├── stable-binarysearch-tree-fragcoord-less-than-zero
├── stable-binarysearch-tree-nested-if-and-conditional
├── stable-binarysearch-tree-with-loop-read-write-global
├── stable-collatz-push-constant-with-nested-min-max
├── stable-colorgrid-modulo-double-always-false-discard
├── stable-mergesort-for-always-false-if-discard
├── stable-mergesort-reversed-for-loop
├── stable-colorgrid-modulo-float-mat-determinant-clamp
├── stable-colorgrid-modulo-injected-conditional-true
├── stable-colorgrid-modulo-true-conditional-divided-1
├── stable-colorgrid-modulo-true-conditional-simple-loop
├── stable-colorgrid-modulo-vec3-values-from-matrix
├── stable-mergesort-clamped-conditional-bit-shift
├── stable-quicksort-conditional-bitwise-or-clamp
├── stable-quicksort-for-loop-with-injection
├── stable-quicksort-if-false-else-return
├── stable-quicksort-max-value-as-index
├── stable-rects-vec4-clamp-conditional-min-mix
├── stable-triangle-array-nested-loop
├── stable-triangle-nested-for-loop-and-true-if
├── stable-triangle-clamp-conditional-mix
├── stable-triangle-nested-conditional-clamped-float
├── struct-and-unreachable-infinite-loop
├── struct-array-data-as-loop-iterator
├── struct-array-index
├── struct-controlled-loop
├── struct-used-as-temporary
├── switch-if-discard
├── switch-inside-while-always-return
├── switch-loop-switch-if
├── switch-with-empty-if-false
├── switch-with-fall-through-cases
├── swizzle-struct-init-min
├── transpose-rectangular-matrix
├── two-2-iteration-loops
├── two-for-loops-with-barrier-function
├── two-loops-mat-add
├── two-loops-matrix
├── two-loops-set-struct
├── two-loops-with-break
├── two-nested-do-whiles
├── two-nested-for-loops-with-returns
├── two-nested-infinite-loops-discard
├── undefined-integer-in-function
├── uninit-element-cast-in-loop
├── uninitialized-var-decrement-and-add
├── undefined-assign-in-infinite-loop
├── unreachable-barrier-in-loops
├── unreachable-continue-statement
├── unreachable-discard-statement-in-if
├── unreachable-discard-statement
├── unreachable-loops
├── unreachable-loops-in-switch
├── unreachable-return-in-loop
├── unreachable-switch-case-with-discards
├── uv-value-comparison-as-boolean
├── vec2-modf
├── vector-values-multiplied-by-fragcoord
├── vectors-and-discard-in-function
├── while-function-always-false
├── while-inside-switch
├── write-before-break
├── write-red-in-loop-nest
└── wrong-color-in-always-false-if
```

The direct children above come from the second string field of each index entry. The parser creates an `AmberTestCase` with
that test-name field, attaches any following quoted requirements, and the caller adds the case to the `graphicsfuzz` group
([`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L169),
[`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L175-L189)).

## Test Families

### Individual index entries — one Amber script per registered child

Each direct child is an index-driven Amber test. The index format documents the tuple shape as
`{"filename","test name","description"[,requirement...]}`, and the parser turns each tuple into an Amber test case
([`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L126),
[`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L149-L163)). Representative entries show
simple shader bug reproducers, coverage-oriented `cov-*` cases, raw/SPIR-V comparison cases, and `stable-*` reference-vs-
variant comparisons:

| Registered child | Amber file | Index description | Optional CTS requirements | Evidence |
|---|---|---|---|---|
| `access-new-vector-inside-if-condition` | `access-new-vector-inside-if-condition.amber` | A shader that accesses a new vector within an if condition | None listed | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L1) |
| `control-flow-switch` | `control-flow-switch.amber` | A fragment shader with somewhat complex control flow and a switch | None listed | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L19-L19) |
| `cov-apfloat-sinh-negative-log2` | `cov-apfloat-sinh-negative-log2.amber` | A fragment shader that covers a specific floating point code path | `VK_KHR_shader_float_controls`, `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32` | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L30-L30) |
| `spv-double-branch-to-same-block` | `spv-double-branch-to-same-block.amber` | Equivalent shaders, one with more complex branching | `VK_KHR_shader_terminate_invocation` | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L668-L668) |
| `stable-mergesort-reversed-for-loop` | `stable-mergesort-reversed-for-loop.amber` | A fragment shader with once iterated reversed for loop | `VK_KHR_shader_terminate_invocation` | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L700-L700) |
| `while-inside-switch` | `while-inside-switch.amber` | A fragment shader that uses a while loop inside a switch | `VK_KHR_shader_terminate_invocation` | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L754-L754) |

### `cov-*` coverage-oriented cases

The largest observed naming family is `cov-*` with 580 entries in the parsed index. Their descriptions repeatedly say they
cover specific compiler, optimizer, or analysis paths, such as LLVM, NIR, APFloat, instruction-combine, DAG, value-tracking,
and loop-related paths ([`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L21-L40),
[`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L350-L390)). The wiki does not infer compiler coverage beyond
these index descriptions.

### `spv-*` and `stable-*` comparison cases

The parsed index includes `spv-*` and `stable-*` names. Representative scripts define a reference shader and a variant shader
and compare the resulting framebuffers with an Amber histogram Earth-Mover-Distance expectation, for example
[`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L21-L27),
[`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L628-L630),
and [`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1231-L1231),
as well as [`stable-mergesort-reversed-for-loop.amber`](../../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L23-L25),
[`stable-mergesort-reversed-for-loop.amber`](../../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L779-L951),
and [`stable-mergesort-reversed-for-loop.amber`](../../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L1555-L1555).

### Direct red-output shader cases

Many representative non-comparison scripts use a passthrough vertex shader, one SPIR-V assembly fragment shader, and an
`EXPECT` command checking that a rendered framebuffer region is red. Examples include
[`access-new-vector-inside-if-condition.amber`](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L22-L42),
[`access-new-vector-inside-if-condition.amber`](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L110-L110),
[`control-flow-switch.amber`](../../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L17-L23), and
[`control-flow-switch.amber`](../../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L86-L242).

## Parameter Dimensions

| Dimension | Observed values | Evidence |
|---|---|---|
| Registered test count | 757 direct children under `graphicsfuzz` | [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757), [`graphicsfuzz.txt`](../../../mustpass/main/vk-default/graphicsfuzz.txt#L1-L757) |
| Registration source | One index file, `vulkan/amber/graphicsfuzz/index.txt` | [`vktAmberGraphicsFuzzTests.cpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L42), [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L100-L107) |
| Per-entry fields | filename, test name, description, optional requirement strings | [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L116-L126), [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L149-L163) |
| Optional requirements observed in the index | `VK_KHR_shader_terminate_invocation` on 72 entries; `VK_KHR_shader_float_controls` and `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32` on 8 entries | Examples in [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L2-L4), [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L30-L40), and parser behavior in [`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L155-L163) |
| Shader stage patterns | Representative cases use passthrough vertex shaders and SPIR-V assembly fragment shaders; some sampled coverage cases include GLSL texture-generation helper shaders; sampled comparison cases use reference and variant shader pairs | [`access-new-vector-inside-if-condition.amber`](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L24-L42), [`cov-global-loop-counter-texture-sample-loop-condition-set-array-element.amber`](../../../data/vulkan/amber/graphicsfuzz/cov-global-loop-counter-texture-sample-loop-condition-set-array-element.amber#L23-L27), [`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L25-L30) |
| Framebuffer checks observed in sampled scripts | Direct RGBA/RGB red checks and reference-vs-variant histogram EMD comparisons | [`access-new-vector-inside-if-condition.amber`](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L110-L110), [`write-before-break.amber`](../../../data/vulkan/amber/graphicsfuzz/write-before-break.amber#L341-L342), [`stable-mergesort-reversed-for-loop.amber`](../../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L1555-L1555) |

## Support/Feature Requirements

The C++ registration wrapper itself adds no category-wide feature gate. Optional support requirements are supplied per entry
by extra quoted strings in the index. The shared parser adds each extra string with `testCase->addRequirement()`, and the
shared Amber support path checks required extensions, features, and properties before execution
([`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L155-L163),
[`AmberTestCase::checkSupport()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L203-L286)).

Observed index-level requirements are:

| Requirement | Observed count in index | Example evidence |
|---|---:|---|
| `VK_KHR_shader_terminate_invocation` | 72 | [`always-discarding-function`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L2-L2), [`spv-double-branch-to-same-block`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L668-L668), [`while-inside-switch`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L754-L754) |
| `VK_KHR_shader_float_controls` | 8 | [`cov-apfloat-sinh-negative-log2`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L30-L30), [`cov-asin-undefined-smoothstep`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L40-L40) |
| `FloatControlsProperties.shaderSignedZeroInfNanPreserveFloat32` | 8 | Same APFloat/undefined floating-point entries as the float-controls extension, with matching Amber script requirements in [`cov-apfloat-sinh-negative-log2.amber`](../../../data/vulkan/amber/graphicsfuzz/cov-apfloat-sinh-negative-log2.amber#L62-L64) |

The Amber runner also checks requirements declared inside each Amber recipe before execution and treats unsupported Amber-side
requirements as an internal error if they were not reflected in CTS requirements
([`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L571-L581),
[`AmberTestCase::validateRequirements()` context](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L675-L706)).

## Verification Methods

Execution is delegated to the shared Amber runner. The shared test case parses the `.amber` script from the CTS archive
([`AmberTestCase::parse()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L407-L432)), collects compiled shader binaries
where present, executes the recipe through Amber's Vulkan engine, and reports pass/fail from `ExecuteWithShaderData()`
([`AmberTestInstance::iterate()`](../../../modules/vulkan/amber/vktAmberTestCase.cpp#L546-L615)).

The script-level pass/fail criteria are Amber `EXPECT` statements. Inspected examples show two recurring verification styles:

- Direct rendered-output checks, usually expecting a framebuffer region to be red, as in
  [`access-new-vector-inside-if-condition.amber`](../../../data/vulkan/amber/graphicsfuzz/access-new-vector-inside-if-condition.amber#L110-L110)
  and [`control-flow-switch.amber`](../../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L242-L242).
- Reference-vs-variant image comparisons using `EQ_HISTOGRAM_EMD_BUFFER` and a tolerance in sampled `spv-*`/`stable-*`
  scripts, as in [`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L1231-L1231)
  and [`stable-mergesort-reversed-for-loop.amber`](../../../data/vulkan/amber/graphicsfuzz/stable-mergesort-reversed-for-loop.amber#L1555-L1555).

## Test Principles

- **Index-driven coverage corpus**: the C++ source keeps the category registration stable while the data-side `index.txt`
  enumerates hundreds of GraphicsFuzz shader reproducers and their requirement strings
  ([`vktAmberGraphicsFuzzTests.cpp`](../../../modules/vulkan/amber/vktAmberGraphicsFuzzTests.cpp#L37-L49),
  [`index.txt`](../../../data/vulkan/amber/graphicsfuzz/index.txt#L1-L757)).
- **Shader compiler/control-flow stress**: index descriptions explicitly cover control flow, arrays, loops, undefined or
  edge-case arithmetic, optimizer/code-generation paths, and GraphicsFuzz-found bugs; representative source comments identify
  cases as GraphicsFuzz bug tests ([`control-flow-switch.amber`](../../../data/vulkan/amber/graphicsfuzz/control-flow-switch.amber#L17-L23),
  [`spv-double-branch-to-same-block.amber`](../../../data/vulkan/amber/graphicsfuzz/spv-double-branch-to-same-block.amber#L19-L24)).
- **Requirements remain per-test, not category-wide**: only entries with extra requirement fields receive CTS requirement
  checks through the shared parser ([`vktAmberTestCaseUtil.cpp`](../../../modules/vulkan/amber/vktAmberTestCaseUtil.cpp#L155-L163)).

## Notes / Uncertainties

- No separate `external/vulkancts/modules/vulkan/graphicsfuzz/` source directory was found during source discovery; this
  category is rooted from [`vktTestPackage.cpp`](../../../modules/vulkan/vktTestPackage.cpp#L1380-L1382) and implemented by
  the Amber source file documented here.
- The documentation does not claim semantic details for all 757 individual shaders beyond the inspected index, representative
  scripts, mustpass coverage, and shared Amber execution behavior cited above.
