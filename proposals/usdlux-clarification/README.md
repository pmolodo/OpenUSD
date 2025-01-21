![Status:Draft](https://img.shields.io/badge/Draft-blue)
# Clarification of UsdLux Quantities and Behavior, with Reference Implementation
Copyright &copy; 2024, NVIDIA Corporation, version 1.0


## Overview

The current specifications of the various UsdLux prims + attributes are imprecise or vague in many places, and as a result, actual implementations of them by various renderers have diverged, sometimes quite significantly.

For instance, here is Intel's [4004 Moore Lane](https://dpel.aswf.io/4004-moore-lane/) scene, with the same UsdLux lights defined, in 3 different renderers:

| Karma                                   | Arnold                                    | Omniverse RTX                                 |
| --------------------------------------- | ----------------------------------------- | --------------------------------------------- |
| ![4004 Moore Lane - Karma][moore-karma] | ![4004 Moore Lane - Arnold][moore-arnold] | ![4004 Moore Lane - Omniverse RTX][moore-rtx] |

To address this, we propose making two changes, in two stages: an update to documentation, and the inclusion of a reference renderer implementation in the main OpenUSD repository.

## Stage 1: Documentation Clarification

We propose that the documentation for the UsdLux schema should be updated, such that the behavior of all UsdLux attributes are defined in precise terms.  The goal would be to eliminate ambiguity and ensure that all renderers which conform to these definitions will produce similar results.


### Alternative approaches

#### New Schemas (or new schema versions)

TODO

### Backward Compatibility Notes

TODO

### Affected Schema Classes and Attributes

TODO
(if including exact formulas, would go here)

### Reference Pull Request

- [PR3182]: Accompanying OpenUSD Pull Request

### Prior Work

- [PR2758]: Old Pull Request (now superceded by [PR3182], above)
- [light_comparison]: Repository containing initial attempt to define the problem, and some test cases

## Stage 2: Reference Implementation

Once we have provided clear guidance on expected behavior for UsdLux lights, we will update the included Embree render delegate to include support for UsdLux lights.  This will give a reference implementation to aid those wishing to provide UsdLux support in their renderers.

### Performance vs Clarity

TODO

### Supported Light Types

TODO

### Unsupported Lights and Features

TODO

### Reference Pull Requests

To aid with review and adoption, the work to add UsdLux support to the HdEmbree
render delegate was broken into a chain of smaller PRs:

- Collapsed:
    - [PR3199]: Combination of all Embree UsdLux Reference Implementation PRs
- Separate PRs:
    - [PR3211]: \[hdEmbree\] fix for random number generation (hdEmbree-UsdLux-PR01)
    - [PR3183]: \[hdEmbree\] add HDEMBREE_RANDOM_NUMBER_SEED (hdEmbree-UsdLux-PR02)
    - [PR3185]: \[hdEmbree\] minor fixes / tweaks (hdEmbree-UsdLux-PR03)
    - [PR3234]: \[hdEmbree\][build_usd] add to build_usd.py status message (hdEmbree-UsdLux-PR04)
    - [PR3198]: \[hdEmbree\] ensure we respect PXR_WORK_THREAD_LIMIT (hdEmbree-UsdLux-PR05)
    - [PR3186]: \[hdEmbree\] Initial UsdLux reference implementation (hdEmbree-UsdLux-PR06)
    - [PR3196]: \[hdEmbree\] add HDEMBREE_LIGHT_CREATE debug code (hdEmbree-UsdLux-PR07)
    - [PR3195]: \[hdEmbree\] add support for lighting double-sided meshes (hdEmbree-UsdLux-PR08)
    - [PR3197]: \[hdEmbree\] add support for inputs:diffuse (hdEmbree-UsdLux-PR09)
    - [PR3187]: \[hdEmbree\] add light texture support (hdEmbree-UsdLux-PR10)
    - [PR3188]: \[hdEmbree\] add dome light suppport (hdEmbree-UsdLux-PR11)
    - [PR3189]: \[hdEmbree\] add direct camera visibility support for rect lights (hdEmbree-UsdLux-PR12)
    - [PR3190]: \[hdEmbree\] add pxrPbrt/pbrUtils.h (hdEmbree-UsdLux-PR13)
    - [PR3191]: \[hdEmbree\] add distant light support (hdEmbree-UsdLux-PR14)
    - [PR3192]: \[hdEmbree\] Add utilities for processing ies light files (hdEmbree-UsdLux-PR15)
    - [PR3193]: \[hdEmbree\] Add a PxrIESFile class which mimics iesFile, with additional functionality (hdEmbree-UsdLux-PR16)
    - [PR3194]: \[hdEmbree\] add lighting support for IES files (hdEmbree-UsdLux-PR17)

### Related Work

- [luxtest]: Various UsdLux test scenes and aids for rendering + comparison of results


<!-- Link Reference Definitions -->
[PR2758]: https://github.com/PixarAnimationStudios/OpenUSD/pull/2758
[PR3182]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3182
[PR3199]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3199

[PR3211]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3211
[PR3183]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3183
[PR3185]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3185
[PR3234]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3234
[PR3198]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3198
[PR3186]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3186
[PR3196]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3196
[PR3195]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3195
[PR3197]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3197
[PR3187]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3187
[PR3188]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3188
[PR3189]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3189
[PR3190]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3190
[PR3191]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3191
[PR3192]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3192
[PR3193]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3193
[PR3194]: https://github.com/PixarAnimationStudios/OpenUSD/pull/3194

[light_comparison]: https://github.com/anderslanglands/light_comparison/tree/main
[luxtest]: https://github.com/anderslanglands/luxtest

[moore-karma]: https://github.com/anderslanglands/light_comparison/blob/main/renders/moore-lane/moore-lane_karma.jpg?raw=true "Karma"
[moore-arnold]: https://github.com/anderslanglands/light_comparison/blob/main/renders/moore-lane/moore-lane_arnold.jpg?raw=true "Arnold"
[moore-rtx]: https://github.com/anderslanglands/light_comparison/blob/main/renders/moore-lane/moore-lane_rtx.jpg?raw=true "Omniverse RTX"