# Animation Hybrid Studio: Stickman & 2D Animation Explainer (instructions for Claude Code)

The user has opened this unzipped folder, or pointed you at it or at its zip.
Whatever they typed ("start", "continue", "hi", "install", a topic), do this:

1. **Install every skill in `skills/` globally**, so they work from any chat:
   - Copy each `skills/<name>/` to `~/.claude/skills/<name>/`. On Windows, `~` is
     `C:\Users\<me>`.
   - If a folder already exists, for example `vox-doc-sound` or `stickman-hybrid`, update it
     by copying over it. Never delete anything already there: the user's `.env`,
     `SETUP_STATUS.md`, `CATALOG.tsv` and their own sounds must survive.
   - Check that `~/.claude/skills/stickman-hybrid/SKILL.md` and
     `~/.claude/skills/vox-doc-sound/SKILL.md` are in place.
2. Tell the user, in their language (the one they wrote in, often Hinglish):
   - it is installed globally
   - from now on, in **any** Claude Code chat, they can type "stickman hybrid start", "animation start", or
     "stickman hybrid continue", or name a topic for an explainer video.
   - When executing or starting a video prompt, Claude will ALWAYS ask the user to choose their animation format:
     **Stickman Video** vs **2D Animated Video**. If 2D Animated Video is chosen, Claude will present the 2D art style choices (with the recommended choice highlighted).
3. Skills load when a session starts, so this session may not list them yet. Read
   `~/.claude/skills/stickman-hybrid/SKILL.md` directly now and follow it. It runs the one-time
   setup (resuming if it was half done) and then makes the video.

Prerequisite: the Flow Connector extension and its CLI (`flow-auto`), set up from the
extension's own setup prompt. Never give a Flow web address of your own.

Never ask for API keys or tokens in the chat. Keys go in files the user edits.
