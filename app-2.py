
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("cultural_preservation_sample.csv")

df = load_data()

if "site_index" not in st.session_state:
    st.session_state.site_index = 0
if "chosen_years" not in st.session_state:
    st.session_state.chosen_years = []

# Main loop
if st.session_state.site_index < len(df):
    site = df.iloc[st.session_state.site_index]

    st.title(f"📍 {site['location']} — {site['artifact_name']}")
    st.image(site["image_url"], caption=site["cultural_theme"], use_column_width=True)

    st.subheader("🕰 Choose a Year to Preserve This Site In")
    years = [site["year_1"], site["year_2"], site["year_3"]]
    descriptions = [site["year_1_description"], site["year_2_description"], site["year_3_description"]]
    visitors = [site["year_1_visitors"], site["year_2_visitors"], site["year_3_visitors"]]

    col1, col2, col3 = st.columns(3)
    buttons = []
    for i, col in enumerate([col1, col2, col3]):
        with col:
            st.markdown(f"### {years[i]}")
            st.write(descriptions[i])
            st.write(f"🧍 Visitors: {visitors[i]:,}")
            if st.button(f"Preserve {years[i]}", key=f"year_{i}"):
                st.session_state.chosen_years.append({
                    "location": site["location"],
                    "year": years[i],
                    "description": descriptions[i],
                    "theme": site["cultural_theme"],
                    "gov_support": site["gov_support_program"],
                    "season": site["best_season"]
                })
                st.session_state.site_index += 1
                st.experimental_rerun()
else:
    st.title("🧳 Your Cultural Revival Route")
    for entry in st.session_state.chosen_years:
        st.subheader(f"{entry['location']} — Preserved in {entry['year']}")
        st.write(entry["description"])
        st.caption(f"Theme: {entry['theme']} | Season: {entry['season']} | Support: {entry['gov_support']}")

    st.success("🎉 You've completed your journey!")
