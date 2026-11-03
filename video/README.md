# The Rook video: how it is made

A YouTube explainer in which Rook Calloway (an AI persona, synthetic voice) walks through wvaihub.com. Everything on screen is the real site, captured at a pinned date. This folder holds the recipe, not the media: no footage, voice, or song is committed.

## The pieces

| File | What it does |
|---|---|
| `script.json` | The narration, one entry per scene. The approved wording. |
| `plan.json` | Which footage and which callouts appear, pinned to **sentences** of the narration, so they follow Rook's real pacing. |
| `capture.js` | Playwright captures stills and frame sequences of the live site at 1920x1080 (laid out at 1280x720, rendered at 1.5x so the type is readable on a phone), with `?today=` pinned so countdowns match the narration. It blurs every "People" row (private individuals). It does not capture sec.gov, which blocks scripted browsers. |
| `overlays.js` | Renders captions, callouts, and title cards to transparent PNGs in the site's own typefaces. |
| `build.py` | Times every sentence from the real voice audio (snapping to Rook's pauses), renders each frame, mixes the audio with the song as intro and outro, normalizes loudness to -14 LUFS, and writes the MP4 and an `.srt` caption file. |
| `thumbnail.js` | Renders the 1280x720 thumbnail. |

## Run it

```bash
node video/capture.js <footage-dir>                       # SITE=https://deploy-preview-N--wv-ai-hub.netlify.app to shoot a preview
python3 video/build.py --footage <footage-dir> --voice <voice-dir> --song <song.mp3> --work <work-dir> --out <out-dir>
python3 video/build.py ... --placeholder --draft          # free test with a stand-in voice and half-size frames
node video/thumbnail.js <footage-dir> <out.jpg>
```

The voice folder holds one clip per scene, named by scene id: `1a 1b 2 3 4 5 6 7 8`. Rook's voice is generated in ElevenLabs from `script.json`; `build.py` prints nothing about keys and never reads them.

## Rules it follows

- **Mercer reviews the script and the on-screen text before any credits are spent** (makenomistakes at the Heavy tier, with an independent auditor, plus his four duties). The first audit found six wrong claims in the narration and a wrong date on the site itself; both were fixed before the voice was generated. The site correction is in the verification log.
- **Nothing says buy, sell, or hold.** The "not investment advice" bar stays on screen through the money scene.
- **Disclosures are spoken, not just shown:** Rook is an AI persona with a synthetic voice (scene 1), and the Anthropic conflict is flagged before the Nscale numbers (scene 6) and repeated in scene 7.
- **Private individuals are not shown.** Case-file "People" rows are blurred.
- **The video is a snapshot.** Figures are "as of" the pinned date, on screen and aloud. A published video cannot be corrected, only replaced, so re-cut it when something big changes.
- **Scroll shots are real frames.** `capture.js` shoots each scroll sequence at 30 fps for as many seconds as the shot lasts in the cut, and `build.py` takes the nearest frame. Blending two scroll positions double-exposes the text. If a re-cut changes a shot's length, change its seconds in `SCROLLS` and re-shoot it.
- **Zooms never clip a headline.** Gentle zooms keep the crop within 40px of the left edge, where page text starts; close-ups (1.6x and up) are exempt.
- **Rook is a character.** He has a voice on a waveform, never a face.
