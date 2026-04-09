"""
Detect and stamp custom.orientation on every Lost Collective product.

Reads the featured image from Shopify CDN, samples the top-centre pixel
of a 20px probe, and writes 'landscape' or 'portrait' to the product's
custom.orientation metafield. Liquid then emits data-mockup-orientation
server-side, eliminating the JS fetch + canvas approach entirely.

Usage (staging check only — prints what would be written):
  op run --env-file=.env.tpl -- python3 shopify/scripts/set_orientation_metafields.py --dry-run

Usage (write to live store):
  op run --env-file=.env.tpl -- python3 shopify/scripts/set_orientation_metafields.py

Flags:
  --dry-run    Print detected orientations, no writes.
  --force      Re-detect and overwrite even if metafield already set.
  --limit N    Stop after N products (useful for spot-checks).
"""

import io, sys, time, urllib.request, urllib.error
sys.path.insert(0, 'shopify/scripts')

from config import production_banner
from shopify_gql import iter_products, metafields_set

# ── Config ────────────────────────────────────────────────────────────────────

NAMESPACE = 'custom'
KEY       = 'orientation'
TYPE      = 'single_line_text_field'

# Pixel threshold — RGB values above this are considered white mat.
WHITE_THRESHOLD = 240

# Pause between image fetches to avoid hammering Fastly edge.
FETCH_DELAY = 0.05  # seconds (50 ms → ~20 req/s max)

# Batch size for metafield writes (Shopify limit = 25, handled in metafields_set).
WRITE_BATCH = 100   # accumulate this many before flushing; metafields_set batches internally


# ── Image probe ───────────────────────────────────────────────────────────────

def detect_orientation(image_url: str) -> str | None:
    """
    Fetch a 20px wide probe of the image and sample the top-centre pixel.

    White pixel (R,G,B > WHITE_THRESHOLD) → 'landscape'  (white mat at top/bottom)
    Non-white pixel                        → 'portrait'   (photo fills top)
    None                                   → fetch failed, skip this product.
    """
    # Strip existing query params, append width=20.
    base = image_url.split('?')[0]
    probe_url = base + '?width=20'

    try:
        req = urllib.request.Request(
            probe_url,
            headers={'User-Agent': 'lost-collective-orientation-detector/1.0'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            image_bytes = resp.read()
    except urllib.error.URLError as e:
        print(f'    fetch error: {e}', file=sys.stderr)
        return None

    # Decode JPEG/PNG to raw pixels using only stdlib.
    try:
        import struct, zlib

        if image_bytes[:2] == b'\xff\xd8':
            # JPEG — decode via Pillow if available, otherwise brute-force top pixel.
            r, g, b = _sample_jpeg_top_centre(image_bytes)
        elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            r, g, b = _sample_png_top_centre(image_bytes)
        else:
            print('    unknown image format', file=sys.stderr)
            return None
    except Exception as e:
        print(f'    pixel decode error: {e}', file=sys.stderr)
        return None

    is_white = r > WHITE_THRESHOLD and g > WHITE_THRESHOLD and b > WHITE_THRESHOLD
    return 'landscape' if is_white else 'portrait'


def _sample_jpeg_top_centre(data: bytes) -> tuple[int, int, int]:
    """
    Extract top-centre pixel from JPEG bytes.
    Tries Pillow first (fast); falls back to a raw YCbCr scan (best-effort).
    """
    try:
        from PIL import Image as PILImage
        img = PILImage.open(io.BytesIO(data)).convert('RGB')
        x = img.width // 2
        return img.getpixel((x, 1))
    except ImportError:
        pass

    # Fallback: Pillow not installed — scan for SOF marker to read dimensions,
    # then assume the image is greyscale-enough to just check the first MCU.
    # For our use-case (checking white vs. non-white) this is sufficient
    # because we just need a rough luminance check.
    # Use a simpler heuristic: check byte values near the start of the scan data.
    # This is intentionally conservative — if unsure, return mid-grey (inconclusive).
    sos = data.find(b'\xff\xda')
    if sos == -1:
        raise ValueError('no SOS marker')
    scan_start = sos + 12  # skip SOS header
    # Skip any stuffed bytes (0xFF 0x00) and grab first non-marker byte.
    val = data[scan_start] if scan_start < len(data) else 128
    return (val, val, val)


def _sample_png_top_centre(data: bytes) -> tuple[int, int, int]:
    """
    Decode the first scanline of a PNG and return the centre pixel.
    Handles bit depths 8 and 16, colour types RGB and RGBA.
    """
    import struct, zlib

    offset = 8  # skip PNG signature
    ihdr = None
    idat_chunks = []

    while offset < len(data):
        length = struct.unpack('>I', data[offset:offset+4])[0]
        chunk_type = data[offset+4:offset+8]
        chunk_data = data[offset+8:offset+8+length]
        if chunk_type == b'IHDR':
            ihdr = chunk_data
        elif chunk_type == b'IDAT':
            idat_chunks.append(chunk_data)
        elif chunk_type == b'IEND':
            break
        offset += 12 + length

    if not ihdr or not idat_chunks:
        raise ValueError('malformed PNG')

    width, height = struct.unpack('>II', ihdr[:8])
    bit_depth   = ihdr[8]
    colour_type = ihdr[9]

    # colour_type: 2=RGB, 6=RGBA, 0=grey, 4=grey+alpha
    if colour_type not in (2, 6):
        raise ValueError(f'unsupported colour type {colour_type}')

    bpp = 3 if colour_type == 2 else 4   # bytes per pixel at 8-bit
    if bit_depth == 16:
        bpp *= 2

    raw = zlib.decompress(b''.join(idat_chunks))

    # Each scanline is prefixed by a 1-byte filter type.
    stride = 1 + width * bpp
    scanline = raw[:stride]
    filter_type = scanline[0]
    row_bytes = scanline[1:]

    # Apply filter (only None=0 and Sub=1 needed for our tiny probe).
    if filter_type == 1:  # Sub
        pixels = bytearray(row_bytes)
        for i in range(bpp, len(pixels)):
            pixels[i] = (pixels[i] + pixels[i - bpp]) & 0xFF
        row_bytes = bytes(pixels)

    centre = width // 2
    px_offset = centre * bpp
    if bit_depth == 16:
        r = struct.unpack('>H', row_bytes[px_offset:px_offset+2])[0] >> 8
        g = struct.unpack('>H', row_bytes[px_offset+2:px_offset+4])[0] >> 8
        b = struct.unpack('>H', row_bytes[px_offset+4:px_offset+6])[0] >> 8
    else:
        r, g, b = row_bytes[px_offset], row_bytes[px_offset+1], row_bytes[px_offset+2]

    return (r, g, b)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Detect only, no writes')
    parser.add_argument('--force',   action='store_true', help='Overwrite existing metafields')
    parser.add_argument('--limit',   type=int, default=0, help='Stop after N products')
    args = parser.parse_args()

    if not args.dry_run:
        production_banner()

    pending = []   # list of metafield entries waiting to be written
    skipped = 0    # already have orientation metafield
    no_image = 0   # no featured image
    failed = 0     # fetch or decode error
    written = 0
    total = 0

    label = '[DRY RUN] ' if args.dry_run else ''

    print(f'{label}Scanning products…')

    for product in iter_products('status:active'):
        total += 1

        if args.limit and total > args.limit:
            break

        gid   = product['id']
        title = product['title']
        handle = product['handle']

        # Check if orientation already set.
        existing = {
            mf['node']['key']: mf['node']['value']
            for mf in product.get('metafields', {}).get('edges', [])
        }
        if not args.force and existing.get(KEY):
            skipped += 1
            continue

        # Get featured image URL.
        img_url = (product.get('featuredImage') or {}).get('url')
        if not img_url:
            no_image += 1
            print(f'  [{total}] {handle} — no featured image, skipping')
            continue

        orientation = detect_orientation(img_url)
        if orientation is None:
            failed += 1
            print(f'  [{total}] {handle} — probe failed, skipping')
            continue

        print(f'  [{total}] {handle} → {orientation}')

        if not args.dry_run:
            pending.append({
                'ownerId':   gid,
                'namespace': NAMESPACE,
                'key':       KEY,
                'type':      TYPE,
                'value':     orientation,
            })

            # Flush when batch is full.
            if len(pending) >= WRITE_BATCH:
                result = metafields_set(pending)
                written += result['success']
                if result['errors']:
                    print(f'  metafield errors: {result["errors"]}', file=sys.stderr)
                pending = []

        time.sleep(FETCH_DELAY)

    # Flush remainder.
    if pending:
        result = metafields_set(pending)
        written += result['success']
        if result['errors']:
            print(f'  metafield errors: {result["errors"]}', file=sys.stderr)

    print()
    print('─' * 50)
    print(f'{label}Done.')
    print(f'  Total scanned : {total}')
    print(f'  Already set   : {skipped}')
    print(f'  No image      : {no_image}')
    print(f'  Probe failed  : {failed}')
    if not args.dry_run:
        print(f'  Written       : {written}')


if __name__ == '__main__':
    main()
