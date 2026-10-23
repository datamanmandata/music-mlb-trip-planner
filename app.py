from datetime import datetime, timedelta
from dotenv import load_dotenv
import math
import os
import pandas as pd
import requests
import streamlit as st

load_dotenv()
TM_KEY = os.getenv("TICKETMASTER_API_KEY")

st.set_page_config(
    page_title="Music & MLB Trip Planner", page_icon="⚾", layout="wide"
)

st.title("🎵⚾ Music & MLB Travel Assistant")
st.write(
    "Find overlapping tour dates and regular-season home baseball games by searching for a specific artist or a target city!"
)

# --- Exhaustive City to MLB Team & Ballpark Mapping (All 30 Teams) ---
city_target_mapping = {
    "Atlanta": {
        "mlb_team": "Atlanta Braves",
        "stadium": "Truist Park",
        "lat": 33.8907,
        "lon": -84.4678,
        "tm_city": "Atlanta",
    },
    "Baltimore": {
        "mlb_team": "Baltimore Orioles",
        "stadium": "Oriole Park at Camden Yards",
        "lat": 39.2839,
        "lon": -76.6215,
        "tm_city": "Baltimore",
    },
    "Boston": {
        "mlb_team": "Boston Red Sox",
        "stadium": "Fenway Park",
        "lat": 42.3467,
        "lon": -71.0972,
        "tm_city": "Boston",
    },
    "Chicago (Cubs)": {
        "mlb_team": "Chicago Cubs",
        "stadium": "Wrigley Field",
        "lat": 41.9484,
        "lon": -87.6553,
        "tm_city": "Chicago",
    },
    "Chicago (White Sox)": {
        "mlb_team": "Chicago White Sox",
        "stadium": "Guaranteed Rate Field",
        "lat": 41.8299,
        "lon": -87.6338,
        "tm_city": "Chicago",
    },
    "Cincinnati": {
        "mlb_team": "Cincinnati Reds",
        "stadium": "Great American Ball Park",
        "lat": 39.0974,
        "lon": -84.5071,
        "tm_city": "Cincinnati",
    },
    "Cleveland": {
        "mlb_team": "Cleveland Guardians",
        "stadium": "Progressive Field",
        "lat": 41.4962,
        "lon": -81.6852,
        "tm_city": "Cleveland",
    },
    "Denver": {
        "mlb_team": "Colorado Rockies",
        "stadium": "Coors Field",
        "lat": 39.7559,
        "lon": -104.9942,
        "tm_city": "Denver",
    },
    "Detroit": {
        "mlb_team": "Detroit Tigers",
        "stadium": "Comerica Park",
        "lat": 42.3390,
        "lon": -83.0485,
        "tm_city": "Detroit",
    },
    "Houston": {
        "mlb_team": "Houston Astros",
        "stadium": "Minute Maid Park",
        "lat": 29.7573,
        "lon": -95.3555,
        "tm_city": "Houston",
    },
    "Kansas City": {
        "mlb_team": "Kansas City Royals",
        "stadium": "Kauffman Stadium",
        "lat": 39.0517,
        "lon": -94.4803,
        "tm_city": "Kansas City",
    },
    "Los Angeles (Angels)": {
        "mlb_team": "Los Angeles Angels",
        "stadium": "Angel Stadium",
        "lat": 33.8003,
        "lon": -117.8827,
        "tm_city": "Anaheim",
    },
    "Los Angeles (Dodgers)": {
        "mlb_team": "Los Angeles Dodgers",
        "stadium": "Dodger Stadium",
        "lat": 34.0739,
        "lon": -118.2400,
        "tm_city": "Los Angeles",
    },
    "Miami": {
        "mlb_team": "Miami Marlins",
        "stadium": "loanDepot park",
        "lat": 25.7781,
        "lon": -80.2196,
        "tm_city": "Miami",
    },
    "Milwaukee": {
        "mlb_team": "Milwaukee Brewers",
        "stadium": "American Family Field",
        "lat": 43.0280,
        "lon": -87.9712,
        "tm_city": "Milwaukee",
    },
    "Minneapolis": {
        "mlb_team": "Minnesota Twins",
        "stadium": "Target Field",
        "lat": 44.9817,
        "lon": -93.2777,
        "tm_city": "Minneapolis",
    },
    "New York (Mets)": {
        "mlb_team": "New York Mets",
        "stadium": "Citi Field",
        "lat": 40.7571,
        "lon": -73.8458,
        "tm_city": "New York",
    },
    "New York (Yankees)": {
        "mlb_team": "New York Yankees",
        "stadium": "Yankee Stadium",
        "lat": 40.8296,
        "lon": -73.9262,
        "tm_city": "New York",
    },
    "Oakland / Sacramento": {
        "mlb_team": "Oakland Athletics",
        "stadium": "Sutter Health Park",
        "lat": 38.5804,
        "lon": -121.5095,
        "tm_city": "Sacramento",
    },
    "Philadelphia": {
        "mlb_team": "Philadelphia Phillies",
        "stadium": "Citizens Bank Park",
        "lat": 39.9061,
        "lon": -75.1665,
        "tm_city": "Philadelphia",
    },
    "Phoenix": {
        "mlb_team": "Arizona Diamondbacks",
        "stadium": "Chase Field",
        "lat": 33.4455,
        "lon": -112.0667,
        "tm_city": "Phoenix",
    },
    "Pittsburgh": {
        "mlb_team": "Pittsburgh Pirates",
        "stadium": "PNC Park",
        "lat": 40.4469,
        "lon": -80.0057,
        "tm_city": "Pittsburgh",
    },
    "San Diego": {
        "mlb_team": "San Diego Padres",
        "stadium": "Petco Park",
        "lat": 32.7073,
        "lon": -117.1566,
        "tm_city": "San Diego",
    },
    "San Francisco": {
        "mlb_team": "San Francisco Giants",
        "stadium": "Oracle Park",
        "lat": 37.7786,
        "lon": -122.3893,
        "tm_city": "San Francisco",
    },
    "Seattle": {
        "mlb_team": "Seattle Mariners",
        "stadium": "T-Mobile Park",
        "lat": 47.5914,
        "lon": -122.3325,
        "tm_city": "Seattle",
    },
    "St. Louis": {
        "mlb_team": "St. Louis Cardinals",
        "stadium": "Busch Stadium",
        "lat": 38.6226,
        "lon": -90.1928,
        "tm_city": "St. Louis",
    },
    "St. Petersburg": {
        "mlb_team": "Tampa Bay Rays",
        "stadium": "Tropicana Field",
        "lat": 27.7682,
        "lon": -82.6534,
        "tm_city": "St. Petersburg",
    },
    "Arlington (Texas)": {
        "mlb_team": "Texas Rangers",
        "stadium": "Globe Life Field",
        "lat": 32.7513,
        "lon": -97.0825,
        "tm_city": "Arlington",
    },
    "Toronto": {
        "mlb_team": "Toronto Blue Jays",
        "stadium": "Rogers Centre",
        "lat": 43.6414,
        "lon": -79.3894,
        "tm_city": "Toronto",
    },
    "Washington DC": {
        "mlb_team": "Washington Nationals",
        "stadium": "Nationals Park",
        "lat": 38.8730,
        "lon": -77.0074,
        "tm_city": "Washington",
    },
}

# --- Sidebar Controls ---
st.sidebar.header("Search Mode")
search_mode = st.sidebar.radio(
    "Choose How to Search", options=["By Artist", "By City"]
)

if search_mode == "By Artist":
    artist_input = st.sidebar.text_input(
        "Artist/Band Name", value="Lizzy McAlpine"
    )
else:
    selected_city = st.sidebar.selectbox(
        "Target City",
        options=sorted(list(city_target_mapping.keys())),
        index=0,
    )
    target_info = city_target_mapping[selected_city]
    st.sidebar.info(
        f"📍 **Local Team:** {target_info['mlb_team']}\n🏟️ **Ballpark:** {target_info['stadium']}"
    )

st.sidebar.subheader("Advanced Filters")
weekend_only = st.sidebar.checkbox(
    "Weekend Concerts Only (Fri-Sun)",
    value=False,
    help="Restrict concerts to Friday, Saturday, or Sunday.",
)

mlb_teams_list = sorted([info["mlb_team"] for info in city_target_mapping.values()])

selected_teams = []
if search_mode == "By Artist":
    selected_teams = st.sidebar.multiselect(
        "Filter by Specific Teams (Home or Away)",
        options=mlb_teams_list,
        default=[],
        help="Leave empty to include all teams, or select specific teams to track.",
    )
else:
    restrict_to_local_team = st.sidebar.checkbox(
        f"Only show games featuring the {target_info['mlb_team']}",
        value=True,
        help="Uncheck to see any opponent playing at this ballpark during the homestand.",
    )

st.sidebar.subheader("Filter Tolerances")
date_window_days = st.sidebar.slider(
    "Date Window (± Days)",
    min_value=0,
    max_value=7,
    value=3,
    help="Allow a game to be this many days before or after the concert date.",
)
max_distance_miles = st.sidebar.slider(
    "Max Distance Between Venues (Miles)",
    min_value=5,
    max_value=100,
    value=30,
    help="Maximum geographic distance between the concert venue and the MLB stadium.",
)

search_btn = st.sidebar.button("Find Trip Matches")


# --- Helper Functions ---
def calculate_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return 0.0
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


team_city_mapping = {
    "New York Yankees": "New York",
    "New York Mets": "New York",
    "Chicago Cubs": "Chicago",
    "Chicago White Sox": "Chicago",
    "Los Angeles Dodgers": "Los Angeles",
    "Los Angeles Angels": "Los Angeles",
    "San Francisco Giants": "San Francisco",
    "Oakland Athletics": "San Francisco",
    "Atlanta Braves": "Atlanta",
    "Boston Red Sox": "Boston",
    "Seattle Mariners": "Seattle",
    "Texas Rangers": "Dallas",
    "Houston Astros": "Houston",
    "St. Louis Cardinals": "St. Louis",
    "San Diego Padres": "San Diego",
    "Philadelphia Phillies": "Philadelphia",
    "Washington Nationals": "Washington",
    "Baltimore Orioles": "Baltimore",
    "Toronto Blue Jays": "Toronto",
    "Minnesota Twins": "Minneapolis",
    "Colorado Rockies": "Denver",
    "Arizona Diamondbacks": "Phoenix",
    "Miami Marlins": "Miami",
    "Tampa Bay Rays": "St. Petersburg",
    "Cincinnati Reds": "Cincinnati",
    "Cleveland Guardians": "Cleveland",
    "Detroit Tigers": "Detroit",
    "Kansas City Royals": "Kansas City",
    "Milwaukee Brewers": "Milwaukee",
    "Pittsburgh Pirates": "Pittsburgh",
}


def standardize_city(city_name):
    return team_city_mapping.get(city_name, city_name)


def parse_event_data(event, default_city="Unknown City"):
    name = event.get("name")
    date_str = event.get("dates", {}).get("start", {}).get("localDate")
    status_code = (
        event.get("dates", {}).get("status", {}).get("code", "unknown")
    )
    is_sold_out = (
        "Yes" if status_code in ["offsale", "cancelled", "postponed"] else "No"
    )
    ticket_url = event.get("url", "")

    venue_info = event.get("_embedded", {}).get("venues", [{}])[0]
    venue_name = venue_info.get("name", "Unknown Venue")
    city = venue_info.get("city", {}).get("name", default_city)

    location = venue_info.get("location", {})
    lat = float(location.get("latitude", 0)) if location else 0.0
    lon = float(location.get("longitude", 0)) if location else 0.0

    if date_str:
        return {
            "Artist": name,
            "Date": date_str,
            "City": city,
            "Venue": venue_name,
            "Sold Out": is_sold_out,
            "Ticket URL": ticket_url,
            "Lat": lat,
            "Lon": lon,
        }
    return None


def get_concerts_by_artist(artist_name):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "keyword": artist_name,
        "classificationName": "Music",
        "apikey": TM_KEY,
        "size": 50,
    }
    response = requests.get(url, params=params)
    concerts = []
    if response.status_code == 200:
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        for event in events:
            parsed = parse_event_data(event)
            if parsed:
                concerts.append(parsed)
    return concerts


def get_concerts_by_city(city_name):
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "city": city_name,
        "classificationName": "Music",
        "apikey": TM_KEY,
        "size": 199,
    }
    response = requests.get(url, params=params)
    concerts = []
    if response.status_code == 200:
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        for event in events:
            parsed = parse_event_data(event, default_city=city_name)
            if parsed:
                concerts.append(parsed)
    return concerts


@st.cache_data
def get_mlb_schedule(start_date, end_date):
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={start_date}&endDate={end_date}&hydrate=venue"
    response = requests.get(url)
    games_data = []
    if response.status_code == 200:
        data = response.json()
        dates_list = data.get("dates", [])
        for date_entry in dates_list:
            game_date = date_entry.get("date")
            for game in date_entry.get("games", []):
                if game.get("gameType") != "R":
                    continue
                teams = game.get("teams", {})
                home_team = teams.get("home", {}).get("team", {}).get("name")
                away_team = teams.get("away", {}).get("team", {}).get("name")
                venue = game.get("venue", {})
                stadium_name = venue.get("name", "Unknown Stadium")
                coordinates = venue.get("location", {}).get("defaultCoordinates", {})
                venue_lat = coordinates.get("latitude", 0.0)
                venue_lon = coordinates.get("longitude", 0.0)

                games_data.append(
                    {
                        "Game Date": game_date,
                        "Home Team": home_team,
                        "Away Team": away_team,
                        "Stadium": stadium_name,
                        "Lat": float(venue_lat) if venue_lat else 0.0,
                        "Lon": float(venue_lon) if venue_lon else 0.0,
                    }
                )
    return pd.DataFrame(games_data)


# --- Main Execution ---
if search_btn:
    if not TM_KEY:
        st.error("Missing Ticketmaster API key.")
    else:
        with st.spinner("Scouting tour dates and game schedules..."):
            if search_mode == "By Artist":
                concerts = get_concerts_by_artist(artist_input)
            else:
                concerts = get_concerts_by_city(target_info["tm_city"])

            if not concerts:
                st.warning(
                    f"No concerts found for '{artist_input if search_mode == 'By Artist' else selected_city}'."
                )
            else:
                df_concerts = pd.DataFrame(concerts).drop_duplicates(
                    subset=["Artist", "Date"]
                )

                if weekend_only:
                    df_concerts["DateTime"] = pd.to_datetime(df_concerts["Date"])
                    df_concerts = df_concerts[
                        df_concerts["DateTime"].dt.dayofweek.isin([4, 5, 6])
                    ]

                if df_concerts.empty:
                    st.warning(
                        "No concerts match your filters (e.g., weekend filter)."
                    )
                else:
                    min_date = df_concerts["Date"].min()
                    max_date = df_concerts["Date"].max()
                    df_mlb = get_mlb_schedule(min_date, max_date)

                    if df_mlb.empty:
                        st.warning(
                            "Found concerts, but could not retrieve MLB schedule for that window."
                        )
                    else:
                        raw_matches = []
                        for _, concert in df_concerts.iterrows():
                            c_date_obj = datetime.strptime(
                                concert["Date"], "%Y-%m-%d"
                            ).date()
                            c_city = standardize_city(concert["City"]).lower()
                            c_day_name = c_date_obj.strftime("%A")

                            window_start = (
                                c_date_obj - timedelta(days=date_window_days)
                            ).strftime("%Y-%m-%d")
                            window_end = (
                                c_date_obj + timedelta(days=date_window_days)
                            ).strftime("%Y-%m-%d")

                            date_subset = df_mlb[
                                (df_mlb["Game Date"] >= window_start)
                                & (df_mlb["Game Date"] <= window_end)
                            ]

                            if search_mode == "By City":
                                stadium_keyword = target_info[
                                    "stadium"
                                ].split()[0]
                                date_subset = date_subset[
                                    date_subset["Stadium"].str.contains(
                                        stadium_keyword, case=False, na=False
                                    )
                                ]

                            for _, game in date_subset.iterrows():
                                home_team = game["Home Team"]
                                away_team = game["Away Team"]

                                if (
                                    search_mode == "By Artist"
                                    and selected_teams
                                ):
                                    if (
                                        home_team not in selected_teams
                                        and away_team not in selected_teams
                                    ):
                                        continue

                                if (
                                    search_mode == "By City"
                                    and restrict_to_local_team
                                    and target_info["mlb_team"] != home_team
                                ):
                                    continue

                                game_city_raw = home_team
                                game_city = standardize_city(
                                    game_city_raw
                                ).lower()

                                distance = calculate_distance(
                                    concert["Lat"],
                                    concert["Lon"],
                                    game["Lat"],
                                    game["Lon"],
                                )

                                cities_match = (
                                    c_city in game_city or game_city in c_city
                                )
                                gps_match = (
                                    concert["Lat"] != 0.0
                                    and game["Lat"] != 0.0
                                    and distance <= max_distance_miles
                                )

                                if search_mode == "By City" or (
                                    cities_match or gps_match
                                ):
                                    g_date_obj = datetime.strptime(
                                        game["Game Date"], "%Y-%m-%d"
                                    ).date()
                                    g_day_name = g_date_obj.strftime("%A")
                                    game_date_formatted = (
                                        f"{game['Game Date']} ({g_day_name})"
                                    )

                                    raw_matches.append(
                                        {
                                            "Artist": concert["Artist"],
                                            "Concert Date": f"{concert['Date']} ({c_day_name})",
                                            "Concert Venue": concert["Venue"],
                                            "Concert City": concert["City"],
                                            "Sold Out": concert["Sold Out"],
                                            "Ticket URL": concert["Ticket URL"],
                                            "Matchup": f"{away_team} @ {home_team}",
                                            "Ballpark": game["Stadium"],
                                            "Game Date Display": game_date_formatted,
                                            "Est. Distance (mi)": (
                                                round(distance, 1)
                                                if (
                                                    concert["Lat"] != 0.0
                                                    and game["Lat"] != 0.0
                                                )
                                                else "Matched via Metro City"
                                            ),
                                        }
                                    )

                        st.subheader(
                            f"🎯 Overlap Results ({search_mode} Search)"
                        )
                        if raw_matches:
                            df_raw = pd.DataFrame(raw_matches)

                            df_grouped = (
                                df_raw.groupby(
                                    [
                                        "Artist",
                                        "Concert Date",
                                        "Concert Venue",
                                        "Concert City",
                                        "Sold Out",
                                        "Ticket URL",
                                        "Matchup",
                                        "Ballpark",
                                        "Est. Distance (mi)",
                                    ]
                                )
                                .agg(
                                    {
                                        "Game Date Display": lambda x: ", ".join(
                                            sorted(x)
                                        )
                                    }
                                )
                                .reset_index()
                            )

                            df_grouped.rename(
                                columns={
                                    "Game Date Display": "Available Game Date(s)"
                                },
                                inplace=True,
                            )

                            st.data_editor(
                                df_grouped,
                                column_config={
                                    "Ticket URL": st.column_config.LinkColumn(
                                        "Tickets",
                                        display_text="🔗 Ticketmaster",
                                    )
                                },
                                hide_index=True,
                                use_container_width=True,
                            )
                            st.balloons()
                        else:
                            st.info(
                                "No valid matches found with your current filters. Try adjusting your date window, mileage range, or team/city options!"
                            )