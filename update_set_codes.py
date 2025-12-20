#!/usr/bin/env python3
"""
Script to fetch Magic: The Gathering set codes from Scryfall API
and generate/update set_code_map.json

Scryfall API provides:
- Set codes (used for API lookups)
- Set names (used in TCGplayer CSVs)
- TCGplayer IDs (for reference)

Usage:
    python update_set_codes.py [--output OUTPUT_FILE] [--format FORMAT]

Options:
    --output: Output file path (default: set_code_map.json)
    --format: Output format - 'simple' (name->code) or 'detailed' (full info) (default: simple)
"""

import json
import requests
import argparse
import sys
from typing import Dict, List, Any
from datetime import datetime

SCRYFALL_SETS_URL = "https://api.scryfall.com/sets"

def fetch_scryfall_sets() -> List[Dict[str, Any]]:
    """Fetch all sets from Scryfall API"""
    print("Fetching sets from Scryfall API...")
    try:
        response = requests.get(SCRYFALL_SETS_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("object") != "list":
            raise ValueError("Unexpected response format from Scryfall API")
        
        sets = data.get("data", [])
        print(f"Found {len(sets)} sets from Scryfall")
        return sets
    except requests.RequestException as e:
        print(f"Error fetching from Scryfall API: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing Scryfall data: {e}", file=sys.stderr)
        sys.exit(1)

def filter_magic_sets(sets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to only Magic: The Gathering sets"""
    magic_sets = []
    for s in sets:
        # Scryfall includes other games, filter to Magic only
        game = s.get("game", "").lower()
        if game == "mtg" or game == "magic":
            magic_sets.append(s)
        # Some sets might not have game field but are MTG
        elif not game and s.get("set_type") not in ["token", "memorabilia"]:
            magic_sets.append(s)
    
    print(f"Filtered to {len(magic_sets)} Magic: The Gathering sets")
    return magic_sets

def create_simple_mapping(sets: List[Dict[str, Any]]) -> Dict[str, str]:
    """Create simple name->code mapping (for set_code_map.json format)"""
    mapping = {}
    
    for s in sets:
        name = s.get("name", "").strip()
        code = s.get("code", "").strip()
        
        if name and code:
            # Handle duplicates - prefer the most recent or most relevant set
            if name not in mapping:
                mapping[name] = code
            else:
                # If duplicate, prefer the one with a release date (more official)
                existing_code = mapping[name]
                existing_set = next((x for x in sets if x.get("code") == existing_code), None)
                current_set = s
                
                # Prefer set with release date, or newer set
                if current_set.get("released_at") and not existing_set.get("released_at"):
                    mapping[name] = code
                elif current_set.get("released_at") and existing_set.get("released_at"):
                    # Both have dates, prefer newer
                    if current_set.get("released_at") > existing_set.get("released_at"):
                        mapping[name] = code
    
    return mapping

def create_detailed_mapping(sets: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Create detailed mapping with all set information"""
    mapping = {}
    
    for s in sets:
        name = s.get("name", "").strip()
        if not name:
            continue
        
        mapping[name] = {
            "scryfall_code": s.get("code", ""),
            "scryfall_id": s.get("id", ""),
            "tcgplayer_id": s.get("tcgplayer_id"),
            "set_type": s.get("set_type", ""),
            "released_at": s.get("released_at", ""),
            "card_count": s.get("card_count", 0),
            "digital": s.get("digital", False),
            "foil_only": s.get("foil_only", False),
            "block_code": s.get("block_code"),
            "block": s.get("block"),
            "parent_set_code": s.get("parent_set_code"),
            "icon_svg_uri": s.get("icon_svg_uri"),
        }
    
    return mapping

def save_json(data: Dict, output_file: str, indent: int = 2):
    """Save data to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, sort_keys=True)
        print(f"Saved {len(data)} entries to {output_file}")
    except Exception as e:
        print(f"Error saving to {output_file}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch Magic: The Gathering set codes from Scryfall API"
    )
    parser.add_argument(
        "--output",
        default="set_code_map.json",
        help="Output file path (default: set_code_map.json)"
    )
    parser.add_argument(
        "--format",
        choices=["simple", "detailed"],
        default="simple",
        help="Output format: 'simple' (name->code) or 'detailed' (full info) (default: simple)"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a backup of existing output file before overwriting"
    )
    
    args = parser.parse_args()
    
    # Backup existing file if requested
    if args.backup:
        import shutil
        import os
        if os.path.exists(args.output):
            backup_name = f"{args.output}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(args.output, backup_name)
            print(f"Created backup: {backup_name}")
    
    # Fetch sets from Scryfall
    all_sets = fetch_scryfall_sets()
    magic_sets = filter_magic_sets(all_sets)
    
    # Create mapping based on format
    if args.format == "simple":
        mapping = create_simple_mapping(magic_sets)
    else:
        mapping = create_detailed_mapping(magic_sets)
    
    # Save to file
    save_json(mapping, args.output)
    
    print(f"\nDone! Generated {args.output} with {len(mapping)} set mappings")
    print(f"Format: {args.format}")

if __name__ == "__main__":
    main()

