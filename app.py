
import io
import time
import json
import os
import requests
import pandas as pd
import streamlit as st
import datetime as dt

def load_set_code_map():
    """Load set code mapping from JSON file, with fallback to empty dict"""
    try:
        with open('set_code_map.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.warning(f"Could not load set_code_map.json: {e}. Using empty mapping.")
        return {}

st.set_page_config(page_title="TCGplayer Pull List Organizer", page_icon="🧙", layout="wide")

# WOOBUL Collectibles brand color (dark teal/deep blue from logo)
WOOBUL_COLOR = "#1a5f7a"

# Inject custom CSS for brand colors
st.markdown(
    f"""
    <style>
        .stApp {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        }}
        h1 {{
            color: {WOOBUL_COLOR};
        }}
        .stButton > button {{
            background-color: {WOOBUL_COLOR};
            color: white;
        }}
        .stButton > button:hover {{
            background-color: #155a7a;
            border-color: {WOOBUL_COLOR};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar: Logo & Branding ----------
with st.sidebar:
    # Logo at the top - check multiple possible locations
    logo_paths = ["branding/500x500.png", "logo.png", "logo.jpg", "logo.jpeg", "logo.svg", "static/logo.png", "static/logo.jpg", "static/logo.svg", "assets/logo.png", "assets/logo.svg"]
    logo_found = False
    logo_path_used = None
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            logo_path_used = logo_path
            logo_found = True
            break
    
    if logo_found:
        # Display the logo with proper styling
        st.markdown(
            '<div style="text-align: center; padding: 15px 0; margin-bottom: 20px;">',
            unsafe_allow_html=True
        )
        st.image(logo_path_used, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Fallback: Show company name with branding if logo not found
        st.markdown(
            f"""
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid {WOOBUL_COLOR}; margin-bottom: 20px;">
                <h2 style="color: {WOOBUL_COLOR}; margin: 0; font-size: 28px; font-weight: bold; letter-spacing: 1px;">WOOBUL</h2>
                <p style="color: {WOOBUL_COLOR}; margin: 8px 0 0 0; font-size: 16px; font-weight: 500;">Collectibles</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # ---------- Sidebar: Buy Me a Coffee & Social Media ----------
    st.markdown(f'<h5 style="color: {WOOBUL_COLOR};">☕ Support this tool</h5>', unsafe_allow_html=True)
    st.markdown(
        """
        <p style="font-size: 13px; color: #666; line-height: 1.5; margin-bottom: 12px;">
        If you found this tool helpful, we'd appreciate any support to keep it running for others. 
        Every contribution helps cover hosting costs and keeps this service free for the community.
        </p>
        """,
        unsafe_allow_html=True
    )
    bmc_html = """
    <div style="transform: scale(0.50); transform-origin: left top;">
    <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="woobul_collectibles" data-color="#FFDD00" data-emoji=""  data-font="Poppins" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>
    </div>
    """
    st.components.v1.html(bmc_html, height=60)
    
    st.markdown("---")
    st.markdown(f'<h5 style="color: {WOOBUL_COLOR};">Follow us here:</h5>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <a href="https://www.instagram.com/woobul_collectibles/" target="_blank" style="text-decoration: none; color: #E4405F; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
                Instagram
            </a>
            <a href="https://www.tiktok.com/@woobul_collectibles" target="_blank" style="text-decoration: none; color: #000000; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                </svg>
                TikTok
            </a>
            <a href="https://www.youtube.com/@woobul-collectibles" target="_blank" style="text-decoration: none; color: #FF0000; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
                YouTube
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- Title & Description ----------
st.title("🧙 TCGplayer Pull List Organizer")
st.write("Upload a TCGplayer-style CSV and I'll add **Color** and **Foil** columns to your pull list. Magic cards get color data from Scryfall, and all cards get foil detection from the Condition field.")
st.caption("Color codes: **W, U, B, R, G, Gd** (multi-color), **C** (colorless/artifacts/Eldrazi), **L** (lands) | Foil cards marked with **\*** in checklist")
st.info("💡 **Currently for Magic: The Gathering only.** We'd love to hear from you if you'd like support for other TCGs!")

with st.expander("How it works"):
    st.markdown(
        """
        1. **Foil Detection**: For all products, we check the **Condition** column. If it contains "Foil", the product name is marked with an asterisk (*) in the checklist, and the CSV includes an "Is Foil" column.
        2. **Color Detection** (Magic cards only): For each row with **Product Line == 'Magic'**, we lookup by **Set + Collector Number** against Scryfall.
        3. If that fails, we fall back to **Set + Exact Name**.
        4. We fill a new **Color** column using `color_identity` and type hints:
           - Land → **L**
           - No color identity but Artifact/Eldrazi → **C**
           - 2+ color identity letters → **Gd**
           - Single W/U/B/R/G → that letter
        """
    )

# Load set code mapping from external JSON file
DEFAULT_SET_CODE_MAP = load_set_code_map()

# Default settings
throttle = 0.08
timeout = 20
max_rows = 0

st.subheader("1) Upload CSV")
uploaded = st.file_uploader("Choose your CSV", type=["csv"])

st.subheader("2) Configure Set Name → Set Code mapping (optional)")
st.caption("If your 'Set' values look different, edit or add to this mapping.")
mapping_text = st.text_area("Set code mapping (JSON)", json.dumps(DEFAULT_SET_CODE_MAP, indent=2), height=220)
try:
    user_map = json.loads(mapping_text)
    assert isinstance(user_map, dict)
except Exception as e:
    st.error(f"Invalid mapping JSON: {e}")
    user_map = DEFAULT_SET_CODE_MAP

def clean_cn(v):
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def color_from_card(card):
    ci = card.get("color_identity") or []
    typ = (card.get("type_line") or "")
    # Lands have empty color_identity by design
    if "Land" in typ:
        return "L"
    if not ci:
        # true colorless, artifacts, eldrazi, etc.
        if "Artifact" in typ or "Eldrazi" in typ:
            return "C"
        return "C" if (card.get("colors")==[] or "Colorless" in (card.get("color_indicator") or "")) else ""
    if len(ci) > 1:
        return "Gd"
    return {"W":"W","U":"U","B":"B","R":"R","G":"G"}.get(ci[0], "")

def fetch_card(set_code, cn, name):
    # 1) direct set+collector endpoint
    url = f"https://api.scryfall.com/cards/{set_code}/{cn}"
    r = requests.get(url, timeout=timeout)
    if r.status_code == 200:
        return r.json()
    # 2) search by set+cn
    r = requests.get("https://api.scryfall.com/cards/search", params={"q": f"e:{set_code} cn:{cn}"}, timeout=timeout)
    if r.status_code == 200 and (r.json().get("data") or []):
        return r.json()["data"][0]
    # 3) search by set+exact name (collector variants sometimes)
    r = requests.get("https://api.scryfall.com/cards/search", params={"q": f'!"{name}" e:{set_code}'}, timeout=timeout)
    if r.status_code == 200 and (r.json().get("data") or []):
        return r.json()["data"][0]
    return None

def is_foil(condition):
    """Check if condition indicates foil - returns '*' for foil, '' for non-foil"""
    if pd.isna(condition):
        return ""
    condition_str = str(condition).lower()
    return "*" if "foil" in condition_str else ""

def get_pokemon_holofoil_type(condition, product_line):
    """For Pokemon cards, detect if holofoil or reverse holofoil. Returns 'RH' for reverse, 'H' for holofoil, '' for non-foil"""
    if pd.isna(condition) or pd.isna(product_line):
        return ""
    product_line_str = str(product_line).strip()
    if product_line_str != "Pokemon":
        return ""
    condition_str = str(condition).lower()
    if "reverse holofoil" in condition_str:
        return "RH"
    if "holofoil" in condition_str:
        return "H"
    return ""

def fill_colors(df, set_map):
    df = df.copy()
    if "Color" not in df.columns:
        df["Color"] = ""
    
    # Add Foil column for all rows (for CSV export)
    if "Condition" in df.columns:
        df["Foil"] = df["Condition"].apply(is_foil)
        # Also create a Yes/No version for CSV clarity
        df["Is Foil"] = df["Condition"].apply(lambda x: "Yes" if "foil" in str(x).lower() else "No" if not pd.isna(x) else "No")
        # Add Pokemon holofoil type column
        if "Product Line" in df.columns:
            df["Pokemon Holofoil"] = df.apply(lambda row: get_pokemon_holofoil_type(row.get("Condition", ""), row.get("Product Line", "")), axis=1)
        else:
            df["Pokemon Holofoil"] = ""
    else:
        df["Foil"] = ""
        df["Is Foil"] = "No"
        df["Pokemon Holofoil"] = ""

    magic_mask = df["Product Line"].astype(str).str.strip().eq("Magic")
    candidates = df[magic_mask].copy()

    total = len(candidates)
    if max_rows and max_rows > 0:
        candidates = candidates.head(max_rows)
        total = len(candidates)

    progress = st.progress(0.0, text="Working…")
    status = st.empty()

    filled = 0
    skipped = 0

    for i, (idx, row) in enumerate(candidates.iterrows(), start=1):
        set_name = str(row.get("Set","")).strip()
        set_code = set_map.get(set_name)
        cn = clean_cn(row.get("Number",""))
        name = str(row.get("Product Name","")).strip()

        if not set_code or not cn:
            skipped += 1
            progress.progress(i/total, text=f"Skipping (missing set code or collector #): {name}")
            continue

        try:
            card = fetch_card(set_code, cn, name)
        except Exception:
            card = None

        if card:
            color = color_from_card(card)
            df.at[idx, "Color"] = color
            filled += 1
            progress.progress(i/total, text=f"Filled {filled} / {total} — {name} [{set_code} {cn}] → {color or '∅'}")
        else:
            skipped += 1
            progress.progress(i/total, text=f"No match found: {name} [{set_code} {cn}]")

        time.sleep(throttle)

    status.info(f"Done. Filled: {filled} | Skipped/Unknown: {skipped}")
    progress.empty()
    return df, filled, skipped

def make_printable_checklist(df):
    # Build checklist HTML
    cols = ["Product Name", "Quantity", "Color", "Number", "Set", "Product Line"]
    safe_df = df.copy()
    for c in cols:
        if c not in safe_df.columns:
            safe_df[c] = ""
    # Add Foil asterisk if not present
    if "Foil" not in safe_df.columns:
        safe_df["Foil"] = ""
    # Add Pokemon Holofoil column if not present
    if "Pokemon Holofoil" not in safe_df.columns:
        safe_df["Pokemon Holofoil"] = ""
    out = safe_df[cols + ["Foil", "Pokemon Holofoil"]].copy()
    
    # Calculate total cards to pull
    try:
        # Try to convert Quantity to numeric, handling any .0 floats
        qty_series = pd.to_numeric(out["Quantity"], errors='coerce').fillna(0)
        total_cards = int(qty_series.sum())
    except Exception:
        total_cards = 0
    total_unique_cards = len(out)

    date_str = dt.datetime.now().strftime("%Y-%m-%d")
    # HTML with print styles
    rows_html = "\n".join([
        f"<tr><td class='cb'>☐</td><td>{(r['Product Name'])}{r['Foil']}{' (' + r['Pokemon Holofoil'] + ')' if r['Pokemon Holofoil'] else ''}</td><td>{(r['Quantity'])}</td><td>{(r['Color'])}</td><td>{(r['Number'])}</td><td>{(r['Set'])}</td><td>{(r['Product Line'])}</td></tr>"
        for _, r in out.iterrows()
    ])

    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>TCGplayer Pull List Checklist {date_str}</title>
<style>
  @media print {{
    @page {{ size: A4 portrait; margin: 12mm; }}
  }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Arial, sans-serif; }}
  h1 {{ font-size: 18pt; margin: 0 0 10px; }}
  .meta {{ font-size: 10pt; color: #444; margin-bottom: 12px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 8px; font-size: 10.5pt; }}
  th {{ background: #f5f5f5; text-align: left; }}
  td.cb {{ width: 22px; text-align: center; font-weight: bold; }}
  .footer {{ margin-top: 14px; font-size: 9pt; color: #666; }}
</style>
</head>
<body>
<h1>TCGplayer Pull List Checklist</h1>
<div class="meta">Generated {date_str}</div>
<div class="meta" style="margin-bottom: 15px;">
  <strong>Total Cards to Pull: {total_cards}</strong> | <strong>Unique Items: {total_unique_cards}</strong>
</div>
<table>
  <thead>
    <tr><th>✓</th><th>Product Name*</th><th>Quantity</th><th>Color</th><th>Number</th><th>Set</th><th>Product Line</th></tr>
  </thead>
  <tbody>
{rows_html}
  </tbody>
</table>
<div class="footer">* = Foil card | (H) = Holofoil, (RH) = Reverse Holofoil (Pokemon) | Tip: Use your browser's Print dialog to save as PDF or print directly.</div>
</body>
</html>"""
    return html

# ---------- Main flow ----------
if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        # Remove the last row
        if len(df) > 0:
            df = df.iloc[:-1]
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        st.stop()

    st.write("### Preview")
    st.dataframe(df.head(20), use_container_width=True)

    required_cols = ["Product Line","Product Name","Set","Number"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing required column(s): {', '.join(missing)}")
        st.stop()

    if st.button("▶️ Fill Colors with Scryfall"):
        result_df, filled, skipped = fill_colors(df, user_map)
        # Store results in session state
        st.session_state['result_df'] = result_df
        st.session_state['filled'] = filled
        st.session_state['skipped'] = skipped

    # Show results and download buttons if they exist in session state
    if 'result_df' in st.session_state:
        result_df = st.session_state['result_df']
        filled = st.session_state.get('filled', 0)
        skipped = st.session_state.get('skipped', 0)

        # Show result preview
        st.write("### Result Preview")
        st.dataframe(result_df.head(20), use_container_width=True)

        # CSV download
        csv_buf = io.StringIO()
        result_df.to_csv(csv_buf, index=False)
        st.download_button(
            "📥 Download CSV with Colors",
            data=csv_buf.getvalue(),
            file_name="tcg_with_colors.csv",
            mime="text/csv",
        )

        # Printable checklist (HTML)
        st.write("### Printable Checklist")
        checklist_html = make_printable_checklist(result_df)
        st.download_button(
            "🖨️ Download Printable Checklist (HTML)",
            data=checklist_html.encode("utf-8"),
            file_name="mtg_checklist.html",
            mime="text/html",
        )
        st.caption("Open the HTML and use your browser's **Print** → **Save as PDF** for a clean PDF.")

        # JSON report
        report = {
            "filled": int(filled),
            "skipped_or_unknown": int(skipped),
            "rows": int(len(result_df)),
        }
        st.download_button(
            "📄 Download run report (JSON)",
            data=json.dumps(report, indent=2),
            file_name="run_report.json",
            mime="application/json",
        )

else:
    st.info("Upload a CSV to begin.")
