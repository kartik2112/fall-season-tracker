# CLAUDE.md — New England Fall Foliage Tracker

One static file, `index.html` (inline CSS + JS, Leaflet 1.9.4 from cdnjs). No build, no backend, no API keys.
Live at https://kartik2112.github.io/fall-season-tracker/ — GitHub Pages serves `main` / root, so **a push to `main` is a deploy** (takes ~1 min; add `?v=N` to bypass the 10-min cache when checking).

## Where things are in index.html (grep these)
| Anchor | What |
|---|---|
| `YT_API_KEY` | Optional YouTube Data API key; empty = feature off |
| `EF_MAPS`, `EF_BOUNDS`, `NE_BOX` | Explore Fall image URL, its geographic corners, the crop we sample |
| `MAINE_ZONES` | Maine Forest Service ArcGIS query URL |
| `STAGES`, `RANK`, `TRIP_W` | The six stages + colours, best-to-visit order, trip-day weights |
| `SLIDER_END`, `TRIP`, `DAYS_BACK` | Slider's last day, planned trip dates (currently Oct 14–19 2026, slider to Oct 22) |
| `const DESTS = [` | Destinations: `[name, state, lat, lon]` |
| `const CAMS = [` | Live cams: `[youtubeId, name, state, lat, lon, channel]` |
| `function loadDay` / `stageAt` | Fetch a day's PNG into a canvas; read the stage under a point |
| `function tripInfo` / `outlook` | Trip ranking and the "Peak ~Oct 9" line |
| `function render` / `showDay` | Redraw markers + sidebar; change the displayed day |
| `<div id="info">` | "How it works" panel (summary + SVG system diagram) — update it when data flow changes |

## Data sources (all fetched by the visitor's browser at page load)
- **Explore Fall** — `https://www.explorefall.com/maps/<year>/<YYYYMMDD>.png` (1386×585, ~30 KB) and `<year>-highres/` (6930×2925, ~300 KB). Sent with `Access-Control-Allow-Origin: *`. Exactly six opaque palette colours = the six stages; transparent = water / no data. Corners are lon −126…−65, lat 23…52, **stretched in Web Mercator** (linear-in-latitude sampling is wrong). Files exist for every day Sep 1–Dec 31; future dates are the forecast. Regenerated daily.
  - `api.explorefall.com` is origin-locked (403) — do not use it.
  - The site hotlinks this image with on-map credit; there are no published terms for it.
- **Maine Forest Service** — ArcGIS FeatureServer layer 2, fields `ZoneName`, `FoliageClass` (`Very Low: 0-10%` … `Peak: 70-100%`, `Past Peak`). Weekly. Geometry is simplified in the query (`maxAllowableOffset=0.01`) to keep it ~100 KB gzipped.
- **YouTube** — thumbnail `https://i.ytimg.com/vi/<id>/hqdefault_live.jpg` (latest frame); player `youtube-nocookie.com/embed/<id>`. Embeds need an http(s) origin — they fail from `file://`.
- **Basemap** — Esri `Canvas/World_Light_Gray_Base` + `_Reference` (labels drawn above the foliage layer), plus `Reference/World_Transportation` as the toggleable roads overlay. CARTO basemaps now demand an API key; don't switch back.
- No public feed was found for NH; VT and MA were not investigated.

## Adding or checking cams (fast path)
1. Find candidates: YouTube search with the live filter, no key needed —
   `https://www.youtube.com/results?sp=EgJAAQ%253D%253D&search_query=<place>+live+cam`, parse `ytInitialData` for `videoRenderer`. Short single-place queries work; long multi-place queries return nothing.
   Productive channels: Boston and Maine Live, WCAX Channel 3 News (SkyWatch3), Mount Washington Observatory, Loon Mountain Resort, Sunday River, Stratton Mountain, Sugarloaf, EustisME, Newburyport.com, Go Martha's Vineyard.
2. Verify each id before adding: fetch `https://www.youtube.com/watch?v=<id>` and require `"isLiveNow":true`, `"playableInEmbed":true`, and `"playabilityStatus":{"status":"OK"`.
3. Add the row to `CAMS` with approximate coordinates. Stream ids change when an owner restarts a stream, so re-run step 2 over the whole list now and then.
   Known rejects: Sebasco Harbor (embedding disabled), Ski Sundown and the Bar Harbor east cam (offline), Smugglers' Notch (not a live view).

## Testing
- Syntax: extract the inline script and `node --check` it.
- Browser: `.claude/launch.json` has a `fall-tracker` static server on port 8766. In the console, `[...DESTS, ...CAMS].filter(x => x.stage < 0)` should be empty, and `DESTS[0].forecast` should fill in a few seconds after load.
- A background/hidden tab will not render YouTube iframes — check playback in a visible tab.

## Conventions
- Keep it a single file with no dependencies beyond Leaflet.
- Stage names and colours are Explore Fall's; the Maine classes map onto the same six by prefix.
- Anything date-specific (`SLIDER_END`, `TRIP`) degrades gracefully: once the dates pass, the slider falls back to today +10 and the trip UI hides itself.
