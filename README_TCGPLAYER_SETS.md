# Extracting TCGPlayer Set Codes

The TCGPlayer mass entry page (https://www.tcgplayer.com/massentry) is a React application that loads set codes dynamically via JavaScript. To extract the set codes:

## Method 1: Browser Console Script

1. Open https://www.tcgplayer.com/massentry in your browser
2. Open Developer Tools (F12)
3. Select "Magic: The Gathering" as the product line
4. Open the Console tab
5. Copy and paste the contents of `extract_sets_browser.js` into the console
6. Press Enter to run it

The script will:
- Try to find the element at the XPath you specified
- Extract any set codes it finds
- Show alternative methods if the XPath doesn't work

## Method 2: Network Tab Inspection

1. Open Developer Tools (F12)
2. Go to the Network tab
3. Filter by "XHR" or "Fetch"
4. Select "Magic: The Gathering" as the product line
5. Look for API calls that might contain set data
6. Click on the request to see the response

Common API endpoints TCGPlayer might use:
- `mpapi.tcgplayer.com`
- `infinite-api.tcgplayer.com`
- `mp-search-api.tcgplayer.com`

## Method 3: React DevTools

1. Install React DevTools browser extension
2. Open the Components tab
3. Navigate to the component that renders the set codes
4. Inspect the component's props/state to find set data

## What to Look For

Set codes in TCGPlayer are typically:
- 3-4 character abbreviations (e.g., "AFR", "MH2", "STX")
- Found in data attributes like `data-set-code`, `data-code`, or `data-set`
- In select/dropdown option values
- In the text content of specific elements

## Next Steps

Once you have the set codes from TCGPlayer, we can:
1. Compare them with Scryfall set codes
2. Create a mapping between TCGPlayer set names/codes and Scryfall codes
3. Update the `set_code_map.json` to include TCGPlayer-specific mappings if needed

