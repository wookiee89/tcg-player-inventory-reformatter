# Set Code Management Scripts

Scripts to fetch and consolidate Magic: The Gathering set codes from Scryfall and TCGplayer sources.

## Scripts

### `update_set_codes.py`

Fetches all Magic: The Gathering sets from Scryfall API and generates a `set_code_map.json` file.

**Basic usage:**
```bash
python update_set_codes.py
```

**Options:**
- `--output FILE`: Specify output file (default: `set_code_map.json`)
- `--format FORMAT`: Output format - `simple` (name->code) or `detailed` (full info) (default: `simple`)
- `--backup`: Create a backup of existing file before overwriting

**Examples:**
```bash
# Generate simple mapping (for set_code_map.json)
python update_set_codes.py

# Generate detailed mapping with all set information
python update_set_codes.py --format detailed --output sets_detailed.json

# Create backup before updating
python update_set_codes.py --backup
```

### `merge_set_sources.py`

Merges set codes from Scryfall (primary) and optionally TCGplayer sources.

**Basic usage:**
```bash
# Just Scryfall (same as update_set_codes.py)
python merge_set_sources.py

# With TCGplayer data
python merge_set_sources.py --tcgplayer-file tcgplayer_to_scryfall.json
```

**Options:**
- `--tcgplayer-file FILE`: Path to TCGplayer set mapping JSON file (optional)
- `--output FILE`: Output file path (default: `set_code_map.json`)
- `--backup`: Create a backup before overwriting

**TCGplayer file formats supported:**
1. Simple format: `{"Set Name": "code", ...}`
2. Detailed format: `{"Set Name": {"tcgplayer_code": "code", ...}, ...}`

## How It Works

### Scryfall API

The scripts use Scryfall's public API endpoint:
- `https://api.scryfall.com/sets` - Returns all sets with codes, names, and metadata

Scryfall provides:
- Set codes (used for API lookups)
- Set names (may differ from TCGplayer names)
- TCGplayer IDs (for reference)
- Release dates, set types, card counts, etc.

### TCGplayer Integration

TCGplayer doesn't have a public API, but you can:

1. **Extract manually** using the browser console script (`extract_sets_browser.js`)
2. **Use existing mapping files** if you have them (e.g., `tcgplayer_to_scryfall.json`)

The merge script will:
- Use Scryfall as the base (since we need Scryfall codes for API lookups)
- Add any TCGplayer-specific set names that don't exist in Scryfall
- Keep Scryfall codes even when TCGplayer uses different codes (since we use Scryfall API)

## Recommended Workflow

### Initial Setup

1. Generate base mapping from Scryfall:
   ```bash
   python update_set_codes.py --backup
   ```

2. If you have TCGplayer data, merge it:
   ```bash
   python merge_set_sources.py --tcgplayer-file tcgplayer_to_scryfall.json --backup
   ```

### Regular Updates

When new sets are released:

1. Update from Scryfall (they update quickly):
   ```bash
   python update_set_codes.py --backup
   ```

2. If needed, extract new TCGplayer sets and merge:
   ```bash
   python merge_set_sources.py --tcgplayer-file your_tcgplayer_data.json --backup
   ```

## Output Format

The default output format (`simple`) matches what `app.py` expects:

```json
{
  "10th Edition": "10e",
  "Adventures in the Forgotten Realms": "afr",
  "Aether Revolt": "aer",
  ...
}
```

This maps TCGplayer set names (as they appear in CSV exports) to Scryfall set codes (used for API lookups).

## Troubleshooting

### API Rate Limits

Scryfall allows up to 10 requests per second. The scripts make a single request to fetch all sets, so this shouldn't be an issue.

### Missing Sets

If a set appears in TCGplayer but not in Scryfall:
1. Check if it's a very new set (may take a few days to appear)
2. Check if it's a non-MTG product (scripts filter to MTG only)
3. Manually add it to the JSON file

### Duplicate Set Names

The scripts handle duplicates by:
- Preferring sets with release dates
- Preferring newer sets when both have dates
- Keeping the first encountered when neither has a date

You can manually edit the JSON to adjust if needed.

## Dependencies

- `requests` - For API calls
- Python 3.6+

Install with:
```bash
pip install requests
```

Or use the existing `requirements.txt`:
```bash
pip install -r requirements.txt
```

