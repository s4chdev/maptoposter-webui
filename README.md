# MapToPoster

Generate beautiful, minimalist map posters for any city in the world.

<p align="center">
  <img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="220">
  <img src="posters/dubai_midnight_blue_20260108_174920.png" width="220">
  <img src="posters/tokyo_japanese_ink_20260108_165830.png" width="220">
</p>

---

> **📌 Credits:** This project is a fork of [originalankur/maptoposter](https://github.com/originalankur/maptoposter) by [@originalankur](https://github.com/originalankur). All original work and concept credit goes to the original author.

---

## Quick Start

```bash
git clone https://github.com/s4chdev/maptoposter-webui.git
cd maptoposter-webui
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## Features

- 🗺️ Generate map posters for any city worldwide
- 🎨 17 beautiful color themes
- 📏 Adjustable map radius (3km - 30km)
- 💾 Download high-resolution PNG (300 DPI)
- ⚡ Real-time generation progress
- 🖼️ Gallery of recent posters

## Examples

| City | Theme | Preview |
|:----:|:-----:|:-------:|
| San Francisco | sunset | <img src="posters/san_francisco_sunset_20260108_184122.png" width="180"> |
| Venice | blueprint | <img src="posters/venice_blueprint_20260108_165527.png" width="180"> |
| Tokyo | japanese_ink | <img src="posters/tokyo_japanese_ink_20260108_165830.png" width="180"> |
| Mumbai | contrast_zones | <img src="posters/mumbai_contrast_zones_20260108_170325.png" width="180"> |
| Singapore | neon_cyberpunk | <img src="posters/singapore_neon_cyberpunk_20260108_184503.png" width="180"> |
| Dubai | midnight_blue | <img src="posters/dubai_midnight_blue_20260108_174920.png" width="180"> |

## Themes

17 themes available:

| Theme | Style |
|-------|-------|
| `noir` | Pure black background, white roads |
| `midnight_blue` | Navy background with gold roads |
| `blueprint` | Architectural blueprint aesthetic |
| `neon_cyberpunk` | Dark with electric pink/cyan |
| `warm_beige` | Vintage sepia tones |
| `japanese_ink` | Minimalist ink wash style |
| `sunset` | Warm oranges and pinks |
| `ocean` | Blues and teals for coastal cities |
| `terracotta` | Mediterranean warmth |
| `forest` | Deep greens and sage |
| `pastel_dream` | Soft muted pastels |
| `contrast_zones` | High contrast urban density |
| `copper_patina` | Oxidized copper aesthetic |
| `autumn` | Seasonal burnt oranges and reds |
| `monochrome_blue` | Single blue color family |
| `gradient_roads` | Smooth gradient shading |
| `feature_based` | Classic black & white |

## Adding Custom Themes

Create a JSON file in `themes/` directory:

```json
{
  "name": "My Theme",
  "description": "Description of the theme",
  "bg": "#FFFFFF",
  "text": "#000000",
  "gradient_color": "#FFFFFF",
  "water": "#C0C0C0",
  "parks": "#F0F0F0",
  "road_motorway": "#0A0A0A",
  "road_primary": "#1A1A1A",
  "road_secondary": "#2A2A2A",
  "road_tertiary": "#3A3A3A",
  "road_residential": "#4A4A4A",
  "road_default": "#3A3A3A"
}
```

## Project Structure

```
maptoposter/
├── app.py                # Flask web application
├── templates/
│   └── index.html        # Web UI
├── themes/               # Theme JSON files
├── fonts/                # Typography
├── posters/              # Generated output
└── requirements.txt
```

## License

MIT License - See [LICENSE](LICENSE) file.

## Credits & Acknowledgments

- **Original Author:** [@originalankur](https://github.com/originalankur) — [github.com/originalankur/maptoposter](https://github.com/originalankur/maptoposter)
- **Map Data:** © [OpenStreetMap](https://www.openstreetmap.org/) contributors
- **Libraries:** [OSMnx](https://github.com/gboeing/osmnx), [Matplotlib](https://matplotlib.org/), [Flask](https://flask.palletsprojects.com/)
