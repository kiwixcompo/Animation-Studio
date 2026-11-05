# Looks & Styles: pick one per video, by animation type and topic

This engine supports two animation formats:
1. **Stickman Explainer**: Minimalist round-head stick-figure characters with dot eyes and thin limbs.
2. **2D Animated Explainer**: Full-character 2D illustrations with stylized anatomy, expressive faces, and rich art styles (see `2d_styles.md`).

---

## 1. Choosing Animation Format & Style

When starting a project, ask the user:
> **"Are you creating a Stickman video or a 2D Animated video?"**
> - If **Stickman**: Proceed with standard stickman character look (`bright`, `warm`, `ink`, `painted`, `night`).
> - If **2D Animated**: Offer the 2D styles from `2d_styles.md`:
>   1. **Modern Flat Vector (`flat-vector`)** - *(Recommended: vibrant, clean, Kurzgesagt/Infographics Show style)*
>   2. **Classic Hand-Drawn 2D Cartoon (`storybook-cartoon`)** - *(Charming, warm, expressive Disney/classic cartoon style)*
>   3. **Cinematic Graphic Novel (`graphic-novel`)** - *(Dramatic ink lines, atmospheric shading, comic-book realism)*
>   4. **Stylized Chibi / Anime 2D (`anime-chibi`)** - *(Cute, high energy, large expressive eyes)*

---

## 2. Color Palettes & Lighting (Applies to both Stickman and 2D)

Every look file has the same four parts:
- **When**: which topics it suits.
- **STYLE**: the paragraph that goes in the project's `STYLE.txt`, after the line
  `look: <name>`. `pictures.py` appends it to every prompt.
- **Character sheet**: the prompt for the one sheet that every character shot references.
- **Notes**: what went wrong before, and how to avoid it.

| Look | Feels like | Best for | Text card |
|---|---|---|---|
| `bright` | clean flat cartoon: blue skies, greens, white rooms | science, health, everyday-things history, anything that cuts between today and the past (the DEFAULT) | light cream to pale blue |
| `warm` | golden ochre, painterly, cosy | ancient humans, civilisation, religion, Indian history, Hindi audiences | ochre |
| `ink` | black ink line on off-white, a few flat colour accents | "explained" topics full of numbers and comparisons, psychology, money | white paper |
| `painted` | detailed painted places, muted and cinematic, one recurring hero | survival stories, "you" serials, disasters, war | grey-blue |
| `night` | deep blue night, firelight and moonlight | mysteries, dark history, space, horror-lite | dark navy, cream words |

## Adapting a look to the topic
- Edit the STYLE paragraph in the project's `STYLE.txt` to suit the topic. For example, add
  "Egyptian desert colours" for a topic about the Nile.
- Keep these four parts of the paragraph. They stop failures we saw in testing:
  - "full-bleed background that fills the whole frame"
  - the palette line
  - character style definition (stick-figure description for Stickman, or chosen 2D style description from `2d_styles.md` for 2D Animation)
  - the "no text" rule, which `pictures.py` adds itself
- Never add a brown or sepia filter to `bright`. A tester rejected a warm film for being
  "too brownish".
- Always test 2 shots (`pictures.py submit 1 8`) and look at them before running the
  full batch.
