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

We could have instead opted to create an entirely new schema, possibly making use of USD's [schema versioning].  The advantage of this would be backward compatibility for existing UsdLux assets - any renderers which previously implemented any UsdLux behavior in a different way could retain their existing implementation for the "old" schema, and only provide new / unified behavior for a new schema.

However, we felt that it would be better to simply update the existing schema, for the following reasons:

- **Not Keeping Undefined Behavior**

  In most cases, we are not changing defined behavior, but clarifying undefined or ambiguously defined behavior.  If we leave the current schema "as is", then we are essentially committing to forever keeping the current schema's behavior undefined or poorly defined.

- **C++ Complexity of Supporting Multiple Schemas**

  If we introduce a completely new schema, it makes interacting with "generic" UsdLux objects difficult at a C++ level.  For instance, if we add a new `UsdLuxDomeLight_1`, all C++ methods that currently work with `UsdLuxDomeLight` will have to be modified to work with `std::variant<UsdLuxDomeLight, UsdLuxDomeLight_1>`, or else they are both made to inherit from a `UsdLuxDomeLightBase`, etc.  In either case, it's a fairly large change to the existing APIs, both inside of the OpenUSD codebase, and for any 3rd-party render delegate implementations.

  Unfortunately, current USD [schema versioning] doesn't help with this - it only provides utilities for identifying if two schemas share the same "family", but no means for treating members of a family in a unified manner.

- **Relatively Low Current Adoption of UsdLux**

  Without having done any formal polling, our general sense is that adoption of UsdLux is still fairly low.

  The ambiguities in the current specification make UsdLux a poor fit for external interchange of lights, as there is no assurance that they will be interpreted in the same manner as originally intended.

  Thus we expect most existing usage of UsdLux assets to be "site internal" - ie, for private assets used within a company in it's own rendering pipeline.  While it's hard to know the extent of such usage, such entities can employ tactics to ease transition that aren't applicable in the "general" case - see below for more details.

### Backward Compatibility Notes

Support for UsdLux-defined lights has already been added to several renderers.  Unfortunately, due to the lack of precise definitions in the current schema, each renderer has had to make their own implementation decisions, resulting in divergent behavior.  Therefore, any existing UsdLux assets have an implicit dependency on the renderer they were "designed" for.

We expect/hope renderers will update their implementations to conform to the new, more precise definitions in this proposal by default.  Since the exact details on current UsdLux implementation are renderer specific, we leave it up to each renderer to decide how best to deal with compatibility with existing UsdLux assets designed with the "old" ambiguous behavior in mind.  However, if they opt to support some form of backward compatibility for existing assets, we can provide some guidelines:

- Renderers can provide a means to explicitly specify whether a given UsdLux asset should use "old" (ambiguously-defined) behavior or "new" (precisely defined, in accordance with this proposal) behavior.
  - For instance, a hypothetical HappyRenderer could check for the existence of a "happy:usdlux_old_compatibility" boolean attribute, and if authored, always use "old" behavior if true, and "new" behavior if false for that asset.
- For assets with no such attribute authored, default should be the "new" behavior.
- However, renderers can provide a way to override the default behavior for prims with no explicit behavior specified
  - For instance, HappyRenderer could check whether a "HAPPY_USDLUX_OLD_COMPATIBILITY" environment var is set, and if so, use that to determine default behavior.
  - If no environment var is set, it could check for the value of a "usdlux_old_compatibility" configuration option in it's renderer configuration files, and potentially use that to override default behavior.

As mentioned above, we expect most existing usage of UsdLux assets to be "site internal" to a specific company or project.  By providing a way to control default behavior and have explicit overrides, it allows such entities several options for how to handle compatibility / transition:

- They could opt to do a one-time mass conversion of all existing assets to be explicitly tagged as having "usdlux_old_compatibility".  Going forward, all new UsdLux assets would inherit the "new" behavior by default.
- They could opt to alter configuration on a per-project basis, if they have project-wide renderer configuration files
- They could specify "old" behavior by default in a site-wide renderer configuration file.  Going forward, all new UsdLux assets could be explicitly authored as using the "new behavior".  At some point in the future when no "old" assets are in use, they could switch the site-wide default to "new", and stop explicitly authoring compatibilty information on new assets.


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

[schema versioning]: https://openusd.org/dev/wp_schema_versioning.html