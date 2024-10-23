# ies:AngleScale - findings and questions

While working to [explicitly specify
UsdLux](https://github.com/PixarAnimationStudios/OpenUSD/pull/3182), we needed
to determine the formula for applying the [ies:angleScale][ies_angleScale_doc].

The [version we settled on for our initial PR][pr_iesAngleScale_formula] was:

$$ \theta_{ies} = \frac{\theta_{light} - \pi}{1 + angleScale} + \pi $$

This formula was chosen because it matches the behavior of how RenderMan applies
`ies:angleScale`, as the attribute is presumably derived from the [profile scale
attribute in Renderman.][rman_profile_scale_doc].

However, this choice has several drawbacks, so we thought we should share our
findings and solicit advice.

## Visualization

### Render 1 - Preview render

The most intuitive way to get a sense for the data in an `.ies` file is to
provide a rendering of what a basic scene illuminated by that light might look
like.  This is the approach used by [ieslibrary.com](ieslibrary.com) in it's
preview lights, so I decided to roughly replicate their setup:

- scene has a floor and a wall (both perfectly diffuse)
- light is placed 1 meter above the floor, and 5 cm in front of the wall
- camera is 2.5 meters above the floor, and 4 meters in front of the wall
- camera is aimed back at the wall / light, angled down 30° from parallel
  to the floor
- light is oriented so that:
  - down is 0° vertical
  - up is 180° vertical
  - 0° horizontal is aimed toward the camera
  - +90° horizontal is screen left (from camera's point of view)
  - -90° / +270° horizontal is screen right (from camera's point of view)

#### Render 1 Example:

For an example of this render, I used a downward-aimed light picked
arbitrarily from [ieslibrary.com](ieslibrary.com):

<table>
  <tr>
    <td>
    <td> +180° vertical, +180° horizontal
    <td>
  </tr>
  <tr>
    <td> +90° horizontal
    <td>
      <img src="https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0001.png"
           title="Render 1 - Preview render - Example downward light" height="200"> <p>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/karma/iesLibPreview-karma.0001.exr">
        [exr]
      </a>
      <a href="https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0001.png">
        [png]
      </a>
      <a href="https://ieslibrary.com/browse/download/ies/04f377f94ce81cd7b5101fffdf571454/bf62776e70fb1699c9163756404c6c7ac19a1d875f069d2e964f69722374be23?cHash=1d691542fcd0ce49d33daf0288d2092e">
        [ies]
      </a>
      <br>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesLibPreview.usda">
        [usda]
      </a> (frame 1)
     </td>
    <td> -90° horizontal<p>(+270° horizontal)
  </tr>
  <tr>
    <td>
    <td>0° vertical, 0° horizontal
    <td>
  </tr>
</table>


### Render 2 - Interior of sphere

While the above render gives a quick sense of what the light might look like in
the world, it's not good for displaying the distribution of the light across
the entire 0° (bottom) to 180° (top) range of vertical angles, as the scene
is set up to mostly highlight downward emissions.

To view the entire vertical-angle distribution, I made a second scene rendering
the light casting on the interior of a sphere:

- a light with the IES profile is at the center of a sphere
- a camera with a 90° field of view is also placed at the sphere center
- the interior of the sphere is rendered twice, aimed to display:
    - horizontal angles -45° to 45°, vertical angles 90° to 180° (top)
    - horizontal angles -45° to 45°, vertical angles 0° to 90° (bottom)
- the two renders are then stitched together to create a single image

#### Render 2 Example:

For an example of this render, I used the same downward-aimed light picked
arbitrarily from [ieslibrary.com](ieslibrary.com) used in the previous render:

<table>
  <tr>
    <td>
    <td>+180° vertical
    <td>
  </tr>
  <tr>
    <td> +45° horizontal
    <td>
      <img src="https://pmolodo.github.io/luxtest/img/iesTest-karma.0001.png"
           title="Render 2 - Interior of sphere - Example downward light" height="200"> <p>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/karma/iesTest-karma.0001.exr">
        [exr]
      </a>
      <a href="https://pmolodo.github.io/luxtest/img/iesTest-karma.0001.png">
        [png]
      </a>
      <a href="https://ieslibrary.com/browse/download/ies/04f377f94ce81cd7b5101fffdf571454/bf62776e70fb1699c9163756404c6c7ac19a1d875f069d2e964f69722374be23?cHash=1d691542fcd0ce49d33daf0288d2092e">
        [ies]
      </a>
      <br>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesTest.usda">
        [usda]
      </a> (frame 1)
     </td>
    <td> -45° horizontal<p>(+315° horizontal)
  </tr>
  <tr>
    <td>
    <td>0° vertical
    <td>
  </tr>
</table>


### Striped IES Test file

Finally, to visualize the effect of the angleScale, I created a [test .ies
file][ies_test_file] consisting of bands of alternating dark/light horizontal
stripes every 10 vertical degrees.  The bottom (verticalAngle=0) is always .25
(gray-black) and the top (verticalAngle=180) is always .75 (gray-white). (The
horizontal angle space is also divided into quadrants, but we can ignore
horizontal-angle differences for this discussion.)

#### Striped IES File: Render 1 - Preview Render:

<table>
  <tr>
    <td>
    <td> +180° vertical, +180° horizontal
    <td>
  </tr>
  <tr>
    <td> +90° horizontal
    <td>
      <img src="https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0011.png"
           title="Striped IES File: Render 1 - Preview Render" height="200"> <p>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/karma/iesLibPreview-karma.0011.exr">
        [exr]
      </a>
      <a href="https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0011.png">
        [png]
      </a>
      <a href="https://github.com/pmolodo/luxtest/blob/0f9955768eca64557be5150b78134b560749e392/test_vstripes_hquadrants_nonuniform.ies">
        [ies]
      </a>
      <br>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesLibPreview.usda">
        [usda]
      </a> (frame 11)
     </td>
    <td> -90° horizontal<p>(+270° horizontal)
  </tr>
  <tr>
    <td>
    <td>0° vertical, 0° horizontal
    <td>
  </tr>
</table>

#### Striped IES File: Render 2 - Interior of sphere:

<table>
  <tr>
    <td>
    <td>+180° vertical
    <td>
  </tr>
  <tr>
    <td> +45° horizontal
    <td>
      <img src="https://pmolodo.github.io/luxtest/img/iesTest-karma.0011.png"
           title="Striped IES File: Render 2 - Interior of sphere" height="200"> <p>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/karma/iesTest-karma.0011.exr">
        [exr]
      </a>
      <a href="https://pmolodo.github.io/luxtest/img/iesTest-karma.0011.png">
        [png]
      </a>
      <a href="https://github.com/pmolodo/luxtest/blob/0f9955768eca64557be5150b78134b560749e392/test_vstripes_hquadrants_nonuniform.ies">
        [ies]
      </a>
      <br>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesLibPreview.usda">
        [usda]
      </a> (frame 11)
     </td>
    <td> -45° horizontal<p>(+315° horizontal)
  </tr>
  <tr>
    <td>
    <td>0° vertical
    <td>
  </tr>
</table>


## Existing formulas

### RenderMan

As noted above, RenderMan appears to use this formula:

$$ \theta_{ies} = \frac{\theta_{light} - \pi}{1 + angleScale} + \pi $$

...which can be rewritten as:

$$ (\theta_{ies} - \pi)\ (1 + angleScale) = (\theta_{light} - \pi) $$

...from which we can see that the relation is a simple scale by
$(1 + angleScale)$, offset so the scale origin is at $(\theta_{light},\ \theta_{ies}) = (\pi,\ \pi)$.

![ies_angleScale_Renderman_clamped.jpg](ies_angleScale_Renderman_clamped.jpg)

#### RenderMan: ies:angleScale from -1 to 1


| -1.00         | -0.75         | -0.50         | -0.25         | =0.00         | +0.25         | +0.50         | +0.75         | +1.00         |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| ![RM-1.00_pre] | ![RM-0.75_pre] | ![RM-0.50_pre] | ![RM-0.25_pre] | ![RM=0.00_pre] | ![RM+0.25_pre] | ![RM+0.50_pre] | ![RM+0.75_pre] | ![RM+1.00_pre] |
| ![RM-1.00_tst] | ![RM-0.75_tst] | ![RM-0.50_tst] | ![RM-0.25_tst] | ![RM=0.00_tst] | ![RM+0.25_tst] | ![RM+0.50_tst] | ![RM+0.75_tst] | ![RM+1.00_tst] |
| ![RM-1.00_gph] | ![RM-0.75_gph] | ![RM-0.50_gph] | ![RM-0.25_gph] | ![RM=0.00_gph] | ![RM+0.25_gph] | ![RM+0.50_gph] | ![RM+0.75_gph] | ![RM+1.00_gph] |


-----------------------

### Karma

Karma appears to use this formula, which has different behavior for positive and
negative values of angleScale:

$$
\theta_{ies} =
\begin{dcases}
    \frac{\theta_{light}}{1 - angleScale},  & \text{if} \quad 0 < angleScale < 1 \\
    \theta_{light} \ (1 + angleScale),     & \text{if} \quad -1 < angleScale < 0   \\
    0,                                      & \text{otherwise}    \\
\end{dcases}
$$

These are similar to the RenderMan formula, except there is a switch in behavior
at $angleScale = 0$, and the scaling origin is left at
$(\theta_{light},\ \theta_{ies}) = (0,\ 0)$:


![ies_angleScale_Karma_clamped.jpg](ies_angleScale_Karma_clamped.jpg)


#### Karma: ies:angleScale from -1 to 1

| -1.00         | -0.75         | -0.50         | -0.25         | =0.00         | +0.25         | +0.50         | +0.75         | +1.00         |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| ![Ka-1.00_pre] | ![Ka-0.75_pre] | ![Ka-0.50_pre] | ![Ka-0.25_pre] | ![Ka=0.00_pre] | ![Ka+0.25_pre] | ![Ka+0.50_pre] | ![Ka+0.75_pre] | ![Ka+1.00_pre] |
| ![Ka-1.00_tst] | ![Ka-0.75_tst] | ![Ka-0.50_tst] | ![Ka-0.25_tst] | ![Ka=0.00_tst] | ![Ka+0.25_tst] | ![Ka+0.50_tst] | ![Ka+0.75_tst] | ![Ka+1.00_tst] |
| ![Ka-1.00_gph] | ![Ka-0.75_gph] | ![Ka-0.50_gph] | ![Ka-0.25_gph] | ![Ka=0.00_gph] | ![Ka+0.25_gph] | ![Ka+0.50_gph] | ![Ka+0.75_gph] | ![Ka+1.00_gph] |

-----------------------

## Analysis of Karma + Renderman formulas

### Behavior for common use case - spotlights

Both of these are create linear relationships between $\theta_{light}$ and
$\theta_{ies}$, with the exact scaling factor depending on $angleScale$.

Further, they both have a fixed scale-origin, though the origin varies between the
two:
- Renderman scale origin: $\theta = \pi$
- Karma scale origin: $\theta = 0$

In the common case of a "spotlight" (or any light with a maximum brightness
centered in a particular direction), the scaling origin direction matters
because, if the scaling origin direction aligns with the light's primary axis,
`ies:angleScale` will behave in a manner artists will likely find intuitive.

That is, if we have a spotlight where

$$ iesProfilePrimaryAxis = scaleOrigin $$

...then altering the `ies:angleScale` will make the the "cone" seem to broaden
or narrow, in a manner that will "feel" a bit like opening and closing barn
doors on a light.

However, if the primary axis is NOT aligned to the scaleOrigin, then altering
the `ies:angleScale` will make the light behave in a way that is likely less
intuitive or useful for lighters.

This means that each of these will work "best" for only a certain subset of
spotlights, and *neither* will work "intuitively" for all lights:

- RenderMan formula:
  - works best for spotlights aimed "up"
  - ie, maximum brightness centered around $verticalAngle = 180°$
    ($\theta = \pi$)
- Karma formula:
  - works best for spotlights aimed "down"
  - ie, maximum brightness centered around $verticalAngle = 0°$ ($\theta = 0$)

#### Animations - Examples of "Good" and "Bad" scaling

What exactly does it mean that I say the formulas work "best" only for lights
aimed in a certain direction?  After all, even if the scaling origin is not
aligned to the ies light primary direction, it is still possible to achieve
something that looks somewhat like scaling the light up and down.

However, if origin + primary light direction are not aligned, though you can
get the boundaries the light to shrink and grow, the behavior of the profile
within it's boundaries is probably not what a lighter would expect.

To help visualize what I mean, I've created animations showing behavior of
both RenderMan and Karma for spot lights aimed both down and up.  They're
displaying versions of my "striped" ies test file, but limited to a 90° cone
aimed either down (ie, verticalAngle < 45°) or up (ie, verticalAngle > 135°).
The `ies:angleScale` attribute is then animated to scale the light between
.5 (45° cone angle) and 1.5 (135° cone angle) - due to the differences in the
angleScale formula, the exact value need to achieve this varies in each case.


<table>
  <tr>
    <td>Light Direction</td>
    <td>RenderMan (Scale origin: Up)</td>
    <td>Karma (Scale origin: Down)</td>
  </tr>
  <tr>
    <td rowspan="2">Up</td>
    <td style="vertical-align:top">
      <video controls loop src="https://github.com/user-attachments/assets/f79c0502-d602-48e3-94d1-a88f1e084822" type="video/mp4" height="200">
        Your browser does not support displaying this video.
      </video>
      <br>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/iesUp-ris.mp4">
        [mp4]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/test_vstripes_hquadrants_nonuniform_aimUp.ies">
        [ies]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesUp.usda">
        [usda]
      </a> (frames 1-49)
    </td>
    <td style="vertical-align:top">
      <video controls loop src="https://github.com/user-attachments/assets/a4494800-49ea-4819-8d37-32074535aca8" type="video/mp4" height="200">
        Your browser does not support displaying this video.
      </video>
      <br>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/iesUp-karma.mp4">
        [mp4]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/test_vstripes_hquadrants_nonuniform_aimUp.ies">
        [ies]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesUp.usda">
        [usda]
      </a> (frames 50-98)
    </td>
  </tr>
  <tr>
    <td style="vertical-align:top">
      <ul>
        <li> "Good" scaling - seems to grow + shrink
        <li> angleScale: .5 scale = -.5; 1.5 scale = .5
        <li> Please disregard the "blurry" rendering - I'm trying to resolve
             <a href="https://renderman.pixar.com/forum/showthread.php?s=&postid=269779">this issue with RenderMan</a>
        </li>
      </ul>
    </td>
    <td style="vertical-align:top">
      <ul>
        <li> "Bad" scaling - bands are created + disappear, large dead area at center when scaling up
        <li> angleScale: .5 scale = -0.142857; 1.5 scale = 0.166667
      </ul>
    </td>
  <tr>
    <td rowspan="2">Down</td>
    <td style="vertical-align:top">
      <video controls loop src="https://github.com/user-attachments/assets/f915a1b4-a38e-4d8a-9a60-6227f9e3cf7d" type="video/mp4" height="200">
        Your browser does not support displaying this video.
      </video>
      <br>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/iesDown-ris.mp4">
        [mp4]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/test_vstripes_hquadrants_nonuniform_aimDown.ies">
        [ies]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesDown.usda">
        [usda]
      </a> (frames 1-49)
    </td>
    <td style="vertical-align:top">
      <video controls loop src="https://github.com/user-attachments/assets/81fcecde-3d28-4e2a-86bf-fee77434968c" type="video/mp4" height="200">
        Your browser does not support displaying this video.
      </video>
      <br>
      <a href="https://github.com/pmolodo/luxtest_renders/raw/5de1733f711d9fa4dbc313e6bded4b312d321137/iesDown-karma.mp4">
        [mp4]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/test_vstripes_hquadrants_nonuniform_aimDown.ies">
        [ies]
      </a>
      <a href="https://raw.githubusercontent.com/pmolodo/luxtest/9d555a66d0a699855342df5491a93851b3e011c2/usd/iesDown.usda">
        [usda]
      </a> (frames 50-98)
    </td>
  </tr>
  <tr>
    <td style="vertical-align:top">
      <ul>
        <li> "Bad" scaling - bands are created + disappear, large dead area at center when scaling up
        <li> angleScale: .5 scale = 0.166667; 1.5 scale =-0.166667
        <li> Please disregard the "blurry" rendering - I'm trying to resolve
             <a href="https://renderman.pixar.com/forum/showthread.php?s=&postid=269779">this issue with RenderMan</a>
        </li>
      </ul>
    </td>
    <td style="vertical-align:top">
      <ul>
        <li> "Good" scaling - seems to grow + shrink
        <li> angleScale: .5 scale = .5; 1.5 scale =-0.333333
      </ul>
    </td>
  </tr>
</table>

#### Which is more common - spotlights aimed up or down?

If [ieslibrary.com](ieslibrary.com) is indicative, lights aimed **down** are
much more common - an ad-hoc perusal indicates that if a light has a "primary
direction", down is the by far the most common. They are apparently common
enough that the site maker designed their preview images assuming the light is
aimed downward, as lights aimed in other directions are poorly framed:

| Aimed down (vangle 0°)    | Aimed Side (vangle 90°)   | Aimed Up (vangle 180°) |
| ------------------------- | ------------------------- | ---------------------- |
| ![down_light][down_light] | ![side_light][side_light] | ![up_light][up_light]  |

This indicates that the **Karma**-formula will result in more intuitive
manipulation for a greater majority of lights.

### RenderMan vs Karma

Here's a chart directly comparing these two formulas, with the option I consider
"better":

| Feature                                                      | RenderMan      | Karma     | Winner    |
| ------------------------------------------------------------ | -------------- | --------- | --------- |
| Scaling origin (works "best" with spotlights aimed this way) | Up (180°)      | Down (0°) |           |
| • Allows "good" scaling for "most common" spotlights    | No             | ***Yes*** | Karma     |
| • Allows "good" scaling for spotlight aimed up OR down  | No             | No        |           |
| Useable domain (angleScale)                                  | $(-1, \infty)$ | $[-1, 1]$ |           |
| • Useable domain - Symmetric?                                | No             | ***Yes*** | Karma     |
| Relation between angleScale and scaling control  | <b><i><ul><li>Negative: narrower<li>Positive: broader</ul></i></b> | <ul><li>Negative: broader<li>Positive: narrower</ul> | RenderMan |
| Same formula for entire domain?                              | ***Yes***      | No        | RenderMan |
| Allows backwards-compatible mapping for RenderMan and Karma? | No             | No        |           |


### No clear winner

Unfortunately, I don't think either option is a clear winner, mostly because:

- *Neither* will provide "good" scaling for a spotlight aimed in any
  direction
- *Neither* formula is "backward compatible" with the other - ie, there's no
  mapping from "old" values to "new" values that will result in unaltered
  behavior for existing scenes.

## Alternatives

Given that bot the RenderMan and Karma formulas have significant drawbacks,
here are some proposals for alternative formulas:

### A. Bimodal - Scaling Origin at 0° for angleScale > 0, 180° for angleScale < 0

This would allow us to support behavior "similar" to either of the current Karma
or RenderMan formulas, without having to add any new attributes.

**Mathematical Description:**

$$
\theta_{ies} =
\begin{dcases}
    \frac{\theta_{light}}{angleScale},
        & \text{if} \quad angleScale > 0 \\
    \\
    \theta_{light}
        & \text{if} \quad angleScale = 0 \\
    \\
    \frac{\theta_{light} - \pi}{-angleScale} + \pi,
        & \text{if} \quad angleScale < 0   \\
\end{dcases}
$$

![ies_angleScale_bimodal_clamped.jpg](ies_angleScale_bimodal_clamped.jpg)

#### Bimodal: ies:angleScale from -2 to -2


| -2.00         | -1.50         | -1.00         | -0.50         | =0.00         | +0.50         | +1.00         | +1.50         | +2.00         |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| ![Bi-2.00_pre] | ![Bi-1.50_pre] | ![Bi-1.00_pre] | ![Bi-0.50_pre] | ![Bi=0.00_pre] | ![Bi+0.50_pre] | ![Bi+1.00_pre] | ![Bi+1.50_pre] | ![Bi+2.00_pre] |
| ![Bi-2.00_tst] | ![Bi-1.50_tst] | ![Bi-1.00_tst] | ![Bi-0.50_tst] | ![Bi=0.00_tst] | ![Bi+0.50_tst] | ![Bi+1.00_tst] | ![Bi+1.50_tst] | ![Bi+2.00_tst] |
| ![Bi-2.00_gph] | ![Bi-1.50_gph] | ![Bi-1.00_gph] | ![Bi-0.50_gph] | ![Bi=0.00_gph] | ![Bi+0.50_gph] | ![Bi+1.00_gph] | ![Bi+1.50_gph] | ![Bi+2.00_gph] |



Pros:
- Can give "good" scaling with lights aimed either up OR down
  - Use positive values for lights aimed down (most common)
  - Use negative values for lights aimed up
- Requires no additional attributes
- Provides a backwards-compatible mapping for either RenderMan or Karma
  - Renderman:

    $$
        angleScale_{new} = - (1 + angleScale_{old_R})
    $$

  - Karma:

    $$
        angleScale_{new} = \begin{dcases}
            1 -  angleScale_{old_K} & \text{if} \quad 0 < angleScale_{old_K} < 1 \\
            \frac{1}{1 + angleScale_{old_K}} & \text{if} \quad -1 < angleScale_{old_K} < 0   \\
        \end{dcases}
    $$


Cons:
- Doesn't give "good" scaling with ALL lights (ie, lights aimed to the side)
- ...nor does it provide a clear path to supporting any aim direction in the
  future
- Non-intuitive "switch" in behavior when the angleScale crosses 0
- Requires user to figure out whether they should use negative or positive
  values to get "good" scaling for their light

### B. Add other attributes

If we're open to adding new attributes, we could allow precise control over
the scaling origin, potentially allow scaling even from horizontally-aimed
lights, and (possibly) make the formula seem a little less "black box" /
obscure.

Options might include:

- Adding a `vAngleScaleType` attributes
  - Be an eumerated attribute that would allow choosing from fixed number of
    behaviors - ie, scaling origin at top (RenderMan style) or bottom (Karma
    style)
  - Or could have an "auto" setting that attempts to calculate a primary light
    direction
  - Could provide some future proofing, by adding new allowed values
- Adding a `vAngleScaleCenter` attribute
  - Would allow scaling from bottom (by setting to 0°) or top (by setting to
    180°)
  - By itself, could allow "distorted" scaling of sideways-aimed lights (ie,
    by still only scaling the vertical angle, and leaving horizontal angle
    unaltered)
- Adding a `hAngleScaleCenter` attribute
  - If combined with a `vAngleScaleCenter`, would allow radial scaling for
    any ies light

While these would enable more control, they would also introduce various levels
of additional complexity, and require more modification to the schema... and
there may not be much demand for this level of control.



<!-- ################################ -->
<!-- URL Reference definitions -->
<!-- ################################ -->

<!--     Internal Links -->
[option_B]: #add-vAngleScaleCenter-attribute
[option_C]: #add-vAngleScaleCenter-hAngleScaleCenter-and-anglescaledirection-attributes

<!--     General External URLs -->
[ies_angleScale_doc]:
    https://openusd.org/release/api/class_usd_lux_shaping_a_p_i.html#a36b62167bddbf3125fc922d78d104d0c
[pr_iesAngleScale_formula]:
    https://github.com/PixarAnimationStudios/OpenUSD/blob/2bd74e30ca5110187b02ad3e8efa1b1c23891cd0/pxr/usd/usdLux/schema.usda#L797-L808
[rman_profile_scale_doc]:
    https://rmanwiki-26.pixar.com/space/REN26/19661751/PxrSphereLight#Light-Profile:~:text=Profile%20Scale
[ies_test_file]:
    https://github.com/pmolodo/luxtest/blob/0f9955768eca64557be5150b78134b560749e392/test_vstripes_hquadrants_nonuniform.ies
[iesTest_usda]:
    https://github.com/pmolodo/luxtest/blob/0f9955768eca64557be5150b78134b560749e392/usd/iesTest.usda
[iesLibPreview_usda]:
    https://github.com/pmolodo/luxtest/blob/0f9955768eca64557be5150b78134b560749e392/usd/iesLibPreview.usda
[luxtest_repo]:
    https://github.com/pmolodo/luxtest/tree/0f9955768eca64557be5150b78134b560749e392
[down_light_ies]:
    https://ieslibrary.com/browse/download/ies/04f377f94ce81cd7b5101fffdf571454/bf62776e70fb1699c9163756404c6c7ac19a1d875f069d2e964f69722374be23?cHash=1d691542fcd0ce49d33daf0288d2092e
[down_light]: https://ieslibrary.com/ies/BEGA/04f377f94ce81cd7b5101fffdf571454.jpg
[side_light]: https://ieslibrary.com/ies/GE_LIGHTING_SOLUTIONS/000720b7043c3ae136132bbad11155ed.jpg
[up_light]: https://ieslibrary.com/ies/BEGA/0184e55f1f5ef8ee9e8b006d6a7bf558.jpg

<!--     iesTest render images -->
[RM-1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0012.png
    'RIS -1.00 angleScale'
[RM-0.75_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0013.png
    'RIS -0.75 angleScale'
[RM-0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0014.png
    'RIS -0.50 angleScale'
[RM-0.25_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0015.png
    'RIS -0.25 angleScale'
[RM=0.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0016.png
    'RIS =0.00 angleScale'
[RM+0.25_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0017.png
    'RIS +0.25 angleScale'
[RM+0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0018.png
    'RIS +0.50 angleScale'
[RM+0.75_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0019.png
    'RIS +0.75 angleScale'
[RM+1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-ris.0020.png
    'RIS +1.00 angleScale'

[Ka-1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0012.png
    'Karma -1.00 angleScale'
[Ka-0.75_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0013.png
    'Karma -0.75 angleScale'
[Ka-0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0014.png
    'Karma -0.50 angleScale'
[Ka-0.25_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0015.png
    'Karma -0.25 angleScale'
[Ka=0.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0016.png
    'Karma =0.00 angleScale'
[Ka+0.25_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0017.png
    'Karma +0.25 angleScale'
[Ka+0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0018.png
    'Karma +0.50 angleScale'
[Ka+0.75_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0019.png
    'Karma +0.75 angleScale'
[Ka+1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-karma.0020.png
    'Karma +1.00 angleScale'

[Bi-2.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0012.png
    'Bimodal -2.00 angleScale'
[Bi-1.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0013.png
    'Bimodal -1.50 angleScale'
[Bi-1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0014.png
    'Bimodal -1.00 angleScale'
[Bi-0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0015.png
    'Bimodal -0.50 angleScale'
[Bi=0.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0016.png
    'Bimodal =0.00 angleScale'
[Bi+0.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0017.png
    'Bimodal +0.50 angleScale'
[Bi+1.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0018.png
    'Bimodal +1.00 angleScale'
[Bi+1.50_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0019.png
    'Bimodal +1.50 angleScale'
[Bi+2.00_tst]: https://pmolodo.github.io/luxtest/img/iesTest-bimodal.0020.png
    'Bimodal +2.00 angleScale'

<!--     iesLibPreview render images -->
[RM-1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0012.png
    'RIS -1.00 angleScale'
[RM-0.75_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0013.png
    'RIS -0.75 angleScale'
[RM-0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0014.png
    'RIS -0.50 angleScale'
[RM-0.25_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0015.png
    'RIS -0.25 angleScale'
[RM=0.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0016.png
    'RIS =0.00 angleScale'
[RM+0.25_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0017.png
    'RIS +0.25 angleScale'
[RM+0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0018.png
    'RIS +0.50 angleScale'
[RM+0.75_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0019.png
    'RIS +0.75 angleScale'
[RM+1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-ris.0020.png
    'RIS +1.00 angleScale'

[Ka-1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0012.png
    'Karma -1.00 angleScale'
[Ka-0.75_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0013.png
    'Karma -0.75 angleScale'
[Ka-0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0014.png
    'Karma -0.50 angleScale'
[Ka-0.25_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0015.png
    'Karma -0.25 angleScale'
[Ka=0.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0016.png
    'Karma =0.00 angleScale'
[Ka+0.25_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0017.png
    'Karma +0.25 angleScale'
[Ka+0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0018.png
    'Karma +0.50 angleScale'
[Ka+0.75_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0019.png
    'Karma +0.75 angleScale'
[Ka+1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-karma.0020.png
    'Karma +1.00 angleScale'

[Bi-2.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0012.png
    'Bimodal -2.00 angleScale'
[Bi-1.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0013.png
    'Bimodal -1.50 angleScale'
[Bi-1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0014.png
    'Bimodal -1.00 angleScale'
[Bi-0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0015.png
    'Bimodal -0.50 angleScale'
[Bi=0.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0016.png
    'Bimodal =0.00 angleScale'
[Bi+0.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0017.png
    'Bimodal +0.50 angleScale'
[Bi+1.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0028.png
    'Bimodal +1.00 angleScale'
[Bi+1.50_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0019.png
    'Bimodal +1.50 angleScale'
[Bi+2.00_pre]: https://pmolodo.github.io/luxtest/img/iesLibPreview-bimodal.0020.png
    'Bimodal +2.00 angleScale'

<!--     angleScale formula graph images -->

[RM-1.00_gph]: ies_angleScale_Renderman_clamped_-1.00.jpg
[RM-0.75_gph]: ies_angleScale_Renderman_clamped_-0.75.jpg
[RM-0.50_gph]: ies_angleScale_Renderman_clamped_-0.50.jpg
[RM-0.25_gph]: ies_angleScale_Renderman_clamped_-0.25.jpg
[RM=0.00_gph]: ies_angleScale_Renderman_clamped_+0.00.jpg
[RM+0.25_gph]: ies_angleScale_Renderman_clamped_+0.25.jpg
[RM+0.50_gph]: ies_angleScale_Renderman_clamped_+0.50.jpg
[RM+0.75_gph]: ies_angleScale_Renderman_clamped_+0.75.jpg
[RM+1.00_gph]: ies_angleScale_Renderman_clamped_+1.00.jpg

[Ka-1.00_gph]: ies_angleScale_Karma_clamped_-1.00.jpg
[Ka-0.75_gph]: ies_angleScale_Karma_clamped_-0.75.jpg
[Ka-0.50_gph]: ies_angleScale_Karma_clamped_-0.50.jpg
[Ka-0.25_gph]: ies_angleScale_Karma_clamped_-0.25.jpg
[Ka=0.00_gph]: ies_angleScale_Karma_clamped_+0.00.jpg
[Ka+0.25_gph]: ies_angleScale_Karma_clamped_+0.25.jpg
[Ka+0.50_gph]: ies_angleScale_Karma_clamped_+0.50.jpg
[Ka+0.75_gph]: ies_angleScale_Karma_clamped_+0.75.jpg
[Ka+1.00_gph]: ies_angleScale_Karma_clamped_+1.00.jpg

[Bi-2.00_gph]: ies_angleScale_Bimodal_clamped_-2.00.jpg
[Bi-1.50_gph]: ies_angleScale_Bimodal_clamped_-1.50.jpg
[Bi-1.00_gph]: ies_angleScale_Bimodal_clamped_-1.00.jpg
[Bi-0.50_gph]: ies_angleScale_Bimodal_clamped_-0.50.jpg
[Bi=0.00_gph]: ies_angleScale_Bimodal_clamped_+0.00.jpg
[Bi+0.50_gph]: ies_angleScale_Bimodal_clamped_+0.50.jpg
[Bi+1.00_gph]: ies_angleScale_Bimodal_clamped_+1.00.jpg
[Bi+1.50_gph]: ies_angleScale_Bimodal_clamped_+1.50.jpg
[Bi+2.00_gph]: ies_angleScale_Bimodal_clamped_+2.00.jpg