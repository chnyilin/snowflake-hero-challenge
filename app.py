import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np
import plotly.graph_objects as go
import random

st.set_page_config(layout="wide")

# ---- Data Load ----
@st.cache_data
def load_data():
    df = pd.read_csv("state_tourist_attractions.csv")
    return df

df = load_data()

# ---- Session State ----
if "journey_started" not in st.session_state:
    st.session_state.journey_started = False
if "site_index" not in st.session_state:
    st.session_state.site_index = 0
if "collected_sites" not in st.session_state:
    st.session_state.collected_sites = []
if "df_filtered" not in st.session_state:
    st.session_state.df_filtered = None
if "selected_state" not in st.session_state:
    st.session_state.selected_state = None

# ---- Step 1: Investment Heatmap ----
if not st.session_state.journey_started:
    st.title("🇮🇳 Swadesh Darshan 2.0: Personalized Trip Generator for India’s Hidden Cultural Gems")

    option = st.radio(
        "Choose Investment per Tourist Type:",
        ("Domestic", "Foreign", "Both (Total)")
    )

    metric_map = {
        "Domestic": "INVESTMENT_PER_DOMESTIC_TOURIST",
        "Foreign": "INVESTMENT_PER_FOREIGN_TOURIST",
        "Both (Total)": "INVESTMENT_PER_TOTAL_TOURIST"
    }
    metric_column = metric_map[option]

    # For heatmap, one row per state
    state_metrics = df.drop_duplicates(subset=["STATE"]).copy()

    # GeoJSON loading (replace with your file path)
    with open("india_states.geojson", "r") as f:
        india_geojson = json.load(f)

    # Build a DataFrame with all states from the geojson
    geojson_states = [f["properties"]["NAME_1"] for f in india_geojson["features"]]
    all_states_df = pd.DataFrame({"GEO_STATE": geojson_states})

    # Make sure your state_metrics DataFrame is ready (as in your metric selection code)
    state_metrics = df.drop_duplicates(subset=["STATE"]).copy()
    state_metrics["GEO_STATE"] = state_metrics["STATE"].str.title()
    # Assign a "No Data" value for NaNs

    # Merge so all states are present for plotting (states with no data get NaN)
    plot_df = all_states_df.merge(state_metrics, on="GEO_STATE", how="left")

    vmin = np.percentile(state_metrics[metric_column], 1)
    vmax = np.percentile(state_metrics[metric_column], 99)

    plot_df["_PLOT_METRIC"] = plot_df[metric_column].fillna(-100).astype(float)

    # Assume plot_df is ready, with _PLOT_METRIC filled with -100 for missing data
    # Find min/max of your real data (excluding -100)
    valid = plot_df["_PLOT_METRIC"] != -100
    real_min = plot_df.loc[valid, "_PLOT_METRIC"].min()
    real_max = plot_df.loc[valid, "_PLOT_METRIC"].max()

    # Build the colorscale: gray for -100, then Viridis for the rest
    colorscale = [
        [0, "lightgray"],    # -100
        [0.00001, "rgb(68,1,84)"],   # Start of Viridis (or pick from plotly.colors.sequential.Viridis)
        [1, "rgb(253,231,37)"],      # End of Viridis
    ]

    # Normalize your _PLOT_METRIC to [0, 1] so -100 is 0, real data is (value-real_min)/(real_max-real_min)
    def norm_val(val):
        if val == -100:
            return 0
        else:
            return (val - real_min) / (real_max - real_min) * (1-0.00001) + 0.00001

    plot_df["_PLOT_METRIC_NORM"] = plot_df["_PLOT_METRIC"].apply(norm_val)

    fig = go.Figure(go.Choropleth(
        geojson=india_geojson,
        locations=plot_df["GEO_STATE"],
        z=plot_df["_PLOT_METRIC_NORM"],
        featureidkey="properties.NAME_1",
        colorscale=colorscale,
        marker=dict(line=dict(width=0.5, color="black")),
        colorbar_title="Metric",
        zmin=0,
        zmax=1,
        hovertext=plot_df["GEO_STATE"] + "<br>" + 
            plot_df[metric_column].astype(str).replace("-100","No data"),
        hoverinfo="text"
    ))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        title=f"State-wise {option} Investment per Tourist"
    )
    st.plotly_chart(fig, use_container_width=True)

    selected_states = st.multiselect(
        "Select states to explore (add one or more):",
        plot_df["GEO_STATE"].tolist()
    )

    hidden_gems = st.checkbox("Show only *Hidden Gem* states (high investment, low footfall)?")

    # Compute thresholds for hidden gems
    invest_thresh = plot_df[metric_column].quantile(0.8)
    footfall_col = "TOTAL_2019"  # Or DOMESTIC_2019 or your preferred footfall
    footfall_thresh = plot_df[footfall_col].quantile(0.2)

    if hidden_gems:
        gem_states = plot_df[
            (plot_df[metric_column] >= invest_thresh) &
            (plot_df[footfall_col] <= footfall_thresh)
        ]["GEO_STATE"].dropna().unique().tolist()
        state_options = gem_states
    else:
        state_options = plot_df["GEO_STATE"].dropna().unique().tolist()

    # After state selection and before "Begin Cultural Journey!" button
    if selected_states:
        # Collect attractions for all selected states (flattened, not by state)
        attractions = df[df["STATE"].str.title().isin(selected_states)].sort_values(
            by="SANCTIONEDCOST", ascending=False
        ).reset_index(drop=True)

        # Fill up to 10 per state, and pad globally if needed (for short states)
        if len(attractions) < len(selected_states) * 10:
            # Fill with random from all_sites if not enough total
            all_sites = df[["NAMEOFEXPERIENCE", "SANCTIONEDCOST", "DESCRIPTIONURL", "IMAGEURL", "STATE"]].copy()
            num_needed = len(selected_states) * 10 - len(attractions)
            fill_choices = all_sites.sample(n=num_needed, replace=True)
            attractions = pd.concat([attractions, fill_choices]).reset_index(drop=True)


    if st.button("Begin Cultural Journey!") and len(selected_states) > 0:
        st.session_state.df_filtered = attractions
        st.session_state.journey_started = True
        st.session_state.site_index = 0
        st.session_state.collected_sites = []
        st.session_state.selected_states = selected_states  # plural!
        st.rerun()

# ---- Step 3: Journey Mode ----
else:
    df_filtered = st.session_state.df_filtered
    state_list = ", ".join(st.session_state.selected_states)
    st.title(f"🧭 Your Journey Through {state_list}")
    if st.session_state.site_index < len(df_filtered):
        site = df_filtered.iloc[st.session_state.site_index]

        # Title with clickable link to gov report
        gov_url = site.get("GOVREPORTURL", "")
        if isinstance(gov_url, str) and not gov_url.startswith("http"):
            gov_url = "https://" + gov_url  # Or "http://", as appropriate
        site_title = f"[{site['NAMEOFEXPERIENCE']}]({site['GOVREPORTURL']})"
        st.markdown(f"## {site_title}")

        img_col, desc_col = st.columns([4, 2])
        with img_col:
            st.image(site["IMAGEURL"], use_container_width=True)

        with desc_col:
            try:
                import requests
                description_text = requests.get(site["DESCRIPTIONURL"]).text
                st.markdown(description_text)
            except:
                st.warning("Description not available.")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ Add to Trip"):
                st.session_state.collected_sites.append({
                    "location": site["NAMEOFEXPERIENCE"],
                    "image": site["IMAGEURL"],
                })
        with col2:
            if st.button("Continue to Next Site"):
                st.session_state.site_index += 1
                st.rerun()

    else:
        st.title("🧳 Your Personalized Cultural Journey")

        if st.session_state.collected_sites:
            for i in range(0, len(st.session_state.collected_sites), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(st.session_state.collected_sites):
                        item = st.session_state.collected_sites[i + j]
                        with cols[j]:
                            st.image(item["image"], caption=item["location"], use_container_width=True)
        else:
            st.info("You didn't collect any artifacts along the way.")

        # Download option
        if st.session_state.collected_sites:
            bucket_df = pd.DataFrame(st.session_state.collected_sites)
            csv = bucket_df.to_csv(index=False)
            st.download_button("Download Travel Plan as CSV", data=csv, file_name="artifact_bucket.csv")

        # Restart option
        if st.button("🔄 Restart Journey"):
            st.session_state.site_index = 0
            st.session_state.journey_started = False
            st.session_state.collected_sites = []
            st.rerun()
