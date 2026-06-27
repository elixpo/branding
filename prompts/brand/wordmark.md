# Elixpo wordmark - OG-style (wordmark + tagline, no mascot)

The "Elixpo" logotype on its own - no panda - generated EXACTLY like an OG card:
the AI renders a text-free editorial DESIGN (dotted matrix + hairline geometry),
then Pillow composites the "Elixpo" headline (fancy serif) and the "Built in the
Open" tagline. 16:9, no alpha pass. Used inline in footers, letterhead, and
anywhere the mascot would be redundant.
Spec: [`references/OREO-LINEART.md`](../../references/OREO-LINEART.md).

## Prompt

A 16:9 brand-wordmark background design (1280x720) in editorial tech-minimalism -
structured, intellectual, airy. Flat 2D vector only: NO 3D, NO gradients, NO
glow, NO neon, NO shadows.

CRITICAL: NO TEXT - no words, letters, numbers or typography anywhere. NO mascot,
NO panda, NO animal. Leave the entire LEFT ~55% as clean, almost-empty negative
space for the wordmark; place ALL artwork in the RIGHT ~40%, pushed toward the
right edge with a clear gap before the left text zone.

Background: white (#ffffff) covered edge-to-edge by a faint dotted matrix - tiny,
evenly-spaced #d9d9dd dots (a subtle halftone / pegboard dot field) receding
behind everything.

Artwork: a small composed cluster of understated geometric shapes in thin
single-weight hairline #d9d9dd outlines (never filled) - a large open circle, a
slim triangle, a thin arc and one or two short straight rules - overlapping and
aligned like a design-system wireframe, calm and intentional, occupying the
RIGHT ~40%. A single short heavy coral #ff7759 bar or dot is the one accent of
colour, placed deliberately within the cluster. Everything else is #d9d9dd
hairline on white - no fills, no clutter.

## Text
headline: Elixpo
sub: Built in the Open
