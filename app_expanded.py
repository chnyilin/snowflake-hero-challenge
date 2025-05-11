
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("cultural_journey_updated.csv")

df = load_data()

if "site_index" not in st.session_state:
    st.session_state.site_index = 0
if "selected_month" not in st.session_state:
    st.session_state.selected_month = None
if "chosen_sites" not in st.session_state:
    st.session_state.chosen_sites = []
if "carbon_total" not in st.session_state:
    st.session_state.carbon_total = 0

# Season filtering
month_to_season = {
    "January": "Winter", "February": "Winter", "March": "Spring", "April": "Summer",
    "May": "Summer", "June": "Monsoon", "July": "Monsoon", "August": "Monsoon",
    "September": "Post-monsoon", "October": "Autumn", "November": "Winter", "December": "Winter"
}

if st.session_state.selected_month is None:
    st.title("🧭 Start Your Cultural Time Travel Journey")
    month = st.selectbox("Choose your travel month", list(month_to_season.keys()))
    if st.button("Begin Journey"):
        st.session_state.selected_month = month_to_season[month]
        df_filtered = df[df['best_season'] == st.session_state.selected_month]
        st.session_state.df_filtered = df_filtered.reset_index(drop=True)
        st.rerun()
else:
    df_filtered = st.session_state.df_filtered
    if st.session_state.site_index < len(df_filtered):
        site = df_filtered.iloc[st.session_state.site_index]

        st.title(f"{site['location']} — {site['artifact_name_2023']}")
        st.image(site["image_url"], use_column_width=True)

        st.subheader("🕰 Choose a Year to Preserve")
        years = [site["year_1"], site["year_2"], site["year_3"]]
        descriptions = [site["year_1_description"], site["year_2_description"], site["year_3_description"]]
        visitors = [site["year_1_visitors"], site["year_2_visitors"], site["year_3_visitors"]]
        artifact_names = [site["artifact_name_1530"], site["artifact_name_2023"], site["artifact_name_2045"]]
        artifact_images = [site["artifact_image_url_1530"], site["artifact_image_url_2023"], site["artifact_image_url_2045"]]

        col1, col2, col3 = st.columns(3)
        for i, col in enumerate([col1, col2, col3]):
            with col:
                st.markdown(f"### {years[i]}")
                st.write(descriptions[i])
                st.image(artifact_images[i], caption=artifact_names[i], use_column_width=True)
                st.write(f"🧍 Visitors: {visitors[i]:,}")
                if st.button(f"Preserve {years[i]}", key=f"year_{i}"):
                    st.session_state.chosen_sites.append({
                        "location": site["location"],
                        "year": years[i],
                        "description": descriptions[i],
                        "artifact": artifact_names[i],
                        "theme": site["cultural_theme"],
                        "gov_support": site["gov_support_program"],
                        "season": site["best_season"],
                        "carbon": site["carbon_impact"],
                        "days": site["travel_days"],
                        "lat": site["lat"],
                        "lon": site["lon"]
                    })
                    st.session_state.carbon_total += site["carbon_impact"]
                    st.session_state.site_index += 1
                    st.rerun()
    else:
        st.title("🧳 Your Cultural Revival Route")
        total_days = sum(site["days"] for site in st.session_state.chosen_sites)
        for site in st.session_state.chosen_sites:
            st.subheader(f"{site['location']} — Preserved in {site['year']}")
            st.write(site["description"])
            st.caption(f"🪔 Artifact: {site['artifact']} | Theme: {site['theme']} | Season: {site['season']} | Support: {site['gov_support']}")
        st.markdown("---")
        st.success(f"🌿 Total Estimated Carbon Footprint: {st.session_state.carbon_total} kg CO₂")
        st.info(f"📅 Total Travel Time: {total_days} days")

        st.markdown("A map view and optimized route planner will be available in the next version.")
