# New England Fall Foliage Tracker

**Live site:** https://kartik2112.github.io/fall-season-tracker/

An interactive map for deciding where to go leaf-peeping in New Hampshire, Maine, Vermont, Massachusetts, Connecticut and Rhode Island.

- **Color map** — today's foliage stage everywhere (No color → Low → Moderate → Near peak → Peak → Past peak), with a slider to look back a week or ahead through the forecast.
- **Destinations** — 91 towns ranked for the selected day or for the planned trip dates, each with a day-by-day color strip.
- **Live cams** — 81 public YouTube webcams; thumbnails show the latest frame, hover to preview, click to watch.
- **Maine official zones** — the Maine Forest Service weekly report as an optional layer.

Click **ⓘ How it works** on the site for a system diagram and a plain-language summary.

## How it's built

A single `index.html` using [Leaflet](https://leafletjs.com/). There is no server, build step or API key: the visitor's browser fetches everything fresh on each visit.

| Data | Source | Updates |
|---|---|---|
| Foliage estimate + forecast | [Explore Fall](https://www.explorefall.com/fall-foliage-map) daily map image | Daily |
| Maine zones | [Maine Forest Service](https://www.maine.gov/dacf/mfs/projects/fall_foliage/report/index.shtml) | Weekly |
| Webcams | YouTube live streams from their owners' channels | Live |
| Basemap | Esri Light Gray Canvas | — |

## Run locally

```bash
python3 -m http.server 8766
```

Then open http://localhost:8766. (Opening the file directly works for the map, but YouTube players need an http origin.)

## Change the trip dates

Edit `TRIP` and `SLIDER_END` near the top of the script in `index.html`. Destinations and cams are the `DESTS` and `CAMS` lists just below. See [CLAUDE.md](CLAUDE.md) for maintenance notes.

## Credits

Foliage data © Explore Fall. Maine zones © Maine Forest Service. Webcam streams belong to their respective channels. Basemap © Esri and contributors.
