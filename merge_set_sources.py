#!/usr/bin/env python3
"""
Script to merge set codes from multiple sources (Scryfall, TCGplayer)
and generate a consolidated set_code_map.json

This script:
1. Fetches sets from Scryfall API (primary source)
2. Optionally loads TCGplayer set mappings from a JSON file
3. Merges them intelligently, preferring TCGplayer names when available
4. Outputs the consolidated mapping

Usage:
    python merge_set_sources.py [--tcgplayer-file FILE] [--output OUTPUT_FILE]
"""

import json
import requests
import argparse
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from update_set_codes import fetch_scryfall_sets, filter_magic_sets

def load_tcgplayer_mapping(file_path: str) -> Optional[Dict[str, str]]:
    """Load TCGplayer set name to code mapping from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON formats
        if isinstance(data, dict):
            # Check if it's already in name->code format
            if all(isinstance(v, str) for v in data.values()):
                print(f"Loaded {len(data)} TCGplayer mappings (simple format)")
                return data
            # Check if it's in detailed format with tcgplayer_code
            elif all(isinstance(v, dict) and "tcgplayer_code" in v for v in data.values()):
                mapping = {}
                for name, info in data.items():
                    if "tcgplayer_code" in info:
                        mapping[name] = info["tcgplayer_code"]
                print(f"Loaded {len(mapping)} TCGplayer mappings (detailed format)")
                return mapping
        
        print(f"Warning: Unrecognized TCGplayer file format in {file_path}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"TCGplayer file not found: {file_path} (skipping)", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing TCGplayer JSON: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading TCGplayer file: {e}", file=sys.stderr)
        return None

def create_merged_mapping(
    scryfall_sets: List[Dict[str, Any]],
    tcgplayer_mapping: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Create merged mapping from Scryfall and TCGplayer sources.
    
    Strategy:
    1. Use Scryfall as base (set name -> scryfall code)
    2. If TCGplayer mapping exists, add those entries
    3. For conflicts, prefer TCGplayer names (since that's what appears in CSVs)
    4. Handle name variations and duplicates
    """
    mapping = {}
    
    # First pass: Add all Scryfall sets
    scryfall_name_to_code = {}
    for s in scryfall_sets:
        name = s.get("name", "").strip()
        code = s.get("code", "").strip()
        
        if name and code:
            # Handle duplicates - keep the first one (or prefer with release date)
            if name not in scryfall_name_to_code:
                scryfall_name_to_code[name] = code
            else:
                existing_code = scryfall_name_to_code[name]
                existing_set = next((x for x in scryfall_sets if x.get("code") == existing_code), None)
                current_set = s
                
                if existing_set and current_set.get("released_at") and existing_set.get("released_at"):
                    if current_set.get("released_at") > existing_set.get("released_at"):
                        scryfall_name_to_code[name] = code
    
    # Add Scryfall mappings
    mapping.update(scryfall_name_to_code)
    print(f"Added {len(scryfall_name_to_code)} sets from Scryfall")
    
    # Second pass: Add/override with TCGplayer mappings if available
    if tcgplayer_mapping:
        tcgplayer_added = 0
        tcgplayer_overrides = 0
        
        for tcg_name, tcg_code in tcgplayer_mapping.items():
            if tcg_name not in mapping:
                # New entry from TCGplayer
                mapping[tcg_name] = tcg_code
                tcgplayer_added += 1
            else:
                # Check if codes differ
                existing_code = mapping[tcg_name]
                if existing_code.lower() != tcg_code.lower():
                    # TCGplayer might use different code format, but we'll keep Scryfall code
                    # since that's what we use for API lookups
                    print(f"  Note: '{tcg_name}' has different codes: Scryfall={existing_code}, TCGplayer={tcg_code} (keeping Scryfall)")
                tcgplayer_overrides += 1
        
        print(f"Added {tcgplayer_added} new sets from TCGplayer")
        if tcgplayer_overrides > 0:
            print(f"Verified {tcgplayer_overrides} existing sets against TCGplayer")
    
    return mapping

def main():
    parser = argparse.ArgumentParser(
        description="Merge set codes from Scryfall and TCGplayer sources"
    )
    parser.add_argument(
        "--tcgplayer-file",
        help="Path to TCGplayer set mapping JSON file (optional)"
    )
    parser.add_argument(
        "--output",
        default="set_code_map.json",
        help="Output file path (default: set_code_map.json)"
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
    print("=" * 60)
    print("Fetching sets from Scryfall...")
    print("=" * 60)
    all_sets = fetch_scryfall_sets()
    magic_sets = filter_magic_sets(all_sets)
    
    # Load TCGplayer mapping if provided
    tcgplayer_mapping = None
    if args.tcgplayer_file:
        print("\n" + "=" * 60)
        print(f"Loading TCGplayer mappings from {args.tcgplayer_file}...")
        print("=" * 60)
        tcgplayer_mapping = load_tcgplayer_mapping(args.tcgplayer_file)
    
    # Merge mappings
    print("\n" + "=" * 60)
    print("Merging set mappings...")
    print("=" * 60)
    merged_mapping = create_merged_mapping(magic_sets, tcgplayer_mapping)
    
    # Save to file
    print("\n" + "=" * 60)
    print(f"Saving to {args.output}...")
    print("=" * 60)
    
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(merged_mapping, f, indent=2, ensure_ascii=False, sort_keys=True)
        print(f"\n✓ Successfully saved {len(merged_mapping)} set mappings to {args.output}")
    except Exception as e:
        print(f"\n✗ Error saving to {args.output}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total sets: {len(merged_mapping)}")
    if tcgplayer_mapping:
        print(f"  - From Scryfall: {len(magic_sets)}")
        print(f"  - From TCGplayer: {len(tcgplayer_mapping)}")
    else:
        print(f"  - All from Scryfall: {len(merged_mapping)}")
    print(f"\nOutput file: {args.output}")

if __name__ == "__main__":
    main()

