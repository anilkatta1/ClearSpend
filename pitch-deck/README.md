# ClearSpend pitch deck

## Deliverables

- `ClearSpend_Pitch_Deck.pdf` — 11-slide, 16:9 presentation deck.
- `ClearSpend_Pitch_Deck.pptx` — PowerPoint-compatible version with identical full-bleed slide renders.
- `generate_deck.py` — reproducible source that creates the rendered slides and PDF.
- `generate_pptx.py` — packages the rendered slides into the PPTX.
- `rendered/` — PNG slide renders for presentation fallback and visual review.

Regenerate from the `ClearSpend/` directory:

```bash
python pitch-deck/generate_deck.py
python pitch-deck/generate_pptx.py
```

The PDF script requires Pillow and pypdf. The PPTX script requires `python-pptx`; it uses the local build dependency under `pitch-deck/.build/python-pptx` when present. The PPTX preserves the reviewed visual layout as slide images; edit `generate_deck.py` and regenerate for content/layout changes.

## Claim and evidence boundary

The deck deliberately separates implemented MVP facts, qualitative research evidence, and unvalidated hypotheses. It does not claim a quantified customer outcome, paid traction, market size, production readiness, ERP acceptance, or payment execution.

| Deck content | Primary source |
|---|---|
| Product flow and screenshots | `README.md`; `demo/DEMO_NARRATIVE.md`; `demo/images/assets1.png`–`assets8.png` |
| Implemented controls and deferred boundaries | `docs/product/ramp-release-response.md`; `docs/known-limitations.md` |
| Interview evidence and its limitations | `docs/interviews/research-insights.md`; `docs/interviews/README.md` |
| Segment, offer, discovery gates, and evidence status | `docs/product/business-model-canvas.md` |
| Now / Next / Later sequencing | `docs/product/roadmap.md` |

## Presentation flow

Use slides 4–7 with the live product demo. If the local stack is unavailable, use the deck screenshots and follow the matching narration in `demo/DEMO_NARRATIVE.md`.

Expected delivery time: 5–7 minutes.
