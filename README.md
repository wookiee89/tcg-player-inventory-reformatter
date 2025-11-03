# 🧙 TCGplayer Pull List Organizer

A Streamlit app by **WOOBUL Collectibles** that helps you organize your TCGplayer pull lists by adding metadata (like card colors for Magic: The Gathering) and creating printable checklists.

## Features

- **Color Metadata**: Automatically adds a **Color** column for Magic: The Gathering cards using Scryfall API lookups
- **Smart Matching**: Uses Set + Collector Number, with fallback to Set + Exact Name
- **Printable Checklists**: Export your organized pull list as a printer-friendly HTML checklist
- **CSV Export**: Download your enhanced CSV with all metadata included
- **Color Codes**: `W, U, B, R, G, Gd` (multi-color), `C` (colorless/artifacts/Eldrazi), `L` (lands)

## Current Status

**Currently optimized for Magic: The Gathering**, but we'd love to hear from you if you'd like support for other TCGs!

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

## How It Works

1. Upload your TCGplayer-style CSV file
2. The app processes Magic cards (Product Line == 'Magic')
3. For each card, it looks up the color using Scryfall API:
   - First tries: Set Code + Collector Number
   - Falls back to: Set Code + Exact Card Name
4. Adds a **Color** column with the appropriate color code
5. Export your organized pull list as:
   - Enhanced CSV with colors
   - Printable HTML checklist
   - JSON report of processing results

## Usage Tips

- **Set Code Mapping**: If your CSV uses different set names, you can customize the Set Name → Set Code mapping in the app
- **Printable Checklist**: Open the downloaded HTML file and use your browser's Print dialog (Ctrl+P / Cmd+P) to save as PDF or print directly
- **Last Row Removal**: The app automatically removes the last row from uploaded CSVs (common TCGplayer export quirk)

## Deployment

- **Streamlit Community Cloud**: Push to GitHub and deploy directly
- **Anywhere**: Works on any environment that can run `streamlit run app.py`

## Support

Made with ❤️ by [WOOBUL Collectibles](https://www.instagram.com/woobul_collectibles/)

If you found this tool helpful, we'd appreciate any support to keep it running for others. Every contribution helps cover hosting costs and keeps this service free for the community.

**☕ [Buy Me a Coffee](https://buymeacoffee.com/woobul_collectibles)** - Support the project

**Follow us:**
- [Instagram](https://www.instagram.com/woobul_collectibles/)
- [TikTok](https://www.tiktok.com/@woobul_collectibles)
- [YouTube](https://www.youtube.com/@woobul-collectibles)

## Requirements

See `requirements.txt` for dependencies:
- streamlit
- pandas
- requests

## License

See LICENSE file for details.
