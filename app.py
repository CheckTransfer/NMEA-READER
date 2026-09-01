import re
import streamlit as st

st.set_page_config(
    page_title="NMEA GPS Telematics Decoder", page_icon="📡", layout="wide"
)

st.title("📡 NMEA-0183 Telematics & GPS Decoder")
st.write(
    "Paste your raw NMEA GPS strings below to decode coordinates, speed, time, and signal quality."
)

default_nmea = "$GPRMC,074500.00,A,5218.6105,N,00445.6226,E,0.00,0.00,250726,,,A*55\n$GPGGA,074500.00,5218.6105,N,00445.6226,E,1,12,0.9,0.0,M,0.0,M,,*59"

raw_nmea = st.text_area(
    "Raw NMEA Input Data:", value=default_nmea, height=150
)


def dm_to_dd(dm_str, direction):
    if not dm_str:
        return 0.0
    try:
        if direction in ["N", "S"]:
            deg = float(dm_str[:2])
            minutes = float(dm_str[2:])
        else:
            deg = float(dm_str[:3])
            minutes = float(dm_str[3:])

        dd = deg + (minutes / 60.0)
        if direction in ["S", "W"]:
            dd = -dd
        return round(dd, 6)
    except ValueError:
        return 0.0


if st.button("Decode Telemetry Data", type="primary"):
    if raw_nmea.strip():
        parsed = {}

        for line in raw_nmea.strip().split("\n"):
            line = line.strip()
            parts = line.split(",")

            if "$GPRMC" in parts[0] and len(parts) >= 10:
                t = parts[1]
                status = parts[2]
                lat = dm_to_dd(parts[3], parts[4])
                lon = dm_to_dd(parts[5], parts[6])
                speed_knots = float(parts[7]) if parts[7] else 0.0
                d = parts[9]

                parsed["time"] = f"{t[:2]}:{t[2:4]}:{t[4:6]} UTC" if len(t) >= 6 else t
                parsed["date"] = f"20{d[4:6]}-{d[2:4]}-{d[:2]}" if len(d) == 6 else d
                parsed["lat"] = lat
                parsed["lon"] = lon
                parsed["speed_knots"] = speed_knots
                parsed["speed_kmh"] = round(speed_knots * 1.852, 2)
                parsed["valid"] = (
                    "Active / Valid" if status == "A" else "Void / Invalid"
                )

            elif "$GPGGA" in parts[0] and len(parts) >= 9:
                parsed["sats"] = parts[7]
                parsed["hdop"] = parts[8]

        st.success("Data successfully decoded!")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Date & Time", parsed.get("time", "N/A"), parsed.get("date", ""))
        c2.metric("Latitude", parsed.get("lat", 0.0))
        c3.metric("Longitude", parsed.get("lon", 0.0))
        c4.metric(
            "Speed",
            f"{parsed.get('speed_kmh', 0)} km/h",
            f"{parsed.get('speed_knots', 0)} knots",
        )

        st.markdown("---")
        st.subheader("Decoded Details")
        st.json(parsed)
