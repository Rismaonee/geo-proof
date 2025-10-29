from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import json, os, requests

app = Flask(__name__)

LAST_LOCATION_FILE = "last_location.json"

# -------------
# REVERSE GEO
# -------------
def reverse_geocode(lat, lon):
    """
    Ask OpenStreetMap Nominatim for a human-readable address.
    Returns string like:
      "Jl. ABC No. 12, Kecamatan XXXX, Kota Bandung, Jawa Barat, Indonesia"
    or None if failed.
    """

    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "jsonv2",
            "lat": str(lat),
            "lon": str(lon),
            "zoom": "18",         # 18 = building-level if available
            "addressdetails": 1
        }

        # Nominatim requires a User-Agent identifying your app
        headers = {
            "User-Agent": "simple-location-logger/1.0"
        }

        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None

        data = resp.json()

        # data["display_name"] is usually a full address line
        display_name = data.get("display_name")
        if display_name:
            return display_name

        # fallback build your own from pieces if display_name missing
        addr = data.get("address", {})
        parts = [
            addr.get("road"),
            addr.get("house_number"),
            addr.get("neighbourhood"),
            addr.get("suburb"),
            addr.get("village"),
            addr.get("town"),
            addr.get("city"),
            addr.get("state"),
            addr.get("postcode"),
            addr.get("country"),
        ]
        # filter None / empty and join with commas
        cleaned = [p for p in parts if p]
        if cleaned:
            return ", ".join(cleaned)

        return None

    except Exception as e:
        # if anything breaks (no internet, etc.)
        return None

# -------------
# ROUTES
# -------------
@app.route("/")
def index():
    # serve your blank-white page that requests location
    return send_from_directory(".", "index.html")

@app.route("/report_location", methods=["POST"])
def report_location():
    data = request.get_json() or {}

    lat = data.get("lat")
    lon = data.get("lon")
    acc = data.get("accuracy")
    ts  = data.get("timestamp")
    is_last_known = bool(data.get("is_last_known", False))

    # reverse geocode (may return None if lookup fails)
    full_addr = None
    if lat is not None and lon is not None:
        full_addr = reverse_geocode(lat, lon)

    payload = {
        "lat": lat,
        "lon": lon,
        "accuracy_m": acc,
        "phone_timestamp": ts,
        "server_received_at": datetime.utcnow().isoformat() + "Z",
        "ua": request.headers.get("User-Agent"),
        "is_last_known": is_last_known,
        "full_address": full_addr  # <--- human-readable address
    }

    # save latest record to disk
    with open(LAST_LOCATION_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    # log to console
    print("[LOCATION]", payload)

    # return JSON back to phone (phone doesn't show it visually, but it's good for debug)
    return jsonify({
        "status": "ok",
        "saved": True,
        "is_last_known": is_last_known,
        "full_address": full_addr
    })

@app.route("/last")
def last():
    if os.path.exists(LAST_LOCATION_FILE):
        with open(LAST_LOCATION_FILE, "r") as f:
            return f.read(), 200, {"Content-Type":"application/json"}
    else:
        return jsonify({"error":"no location yet"}), 404

if __name__ == "__main__":
    # run local server, expose with ngrok http 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
