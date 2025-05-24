
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("cultural_journey_updated.csv")

df = load_data()

# Session state initialization
if "journey_started" not in st.session_state:
    st.session_state.journey_started = False
if "site_index" not in st.session_state:
    st.session_state.site_index = 0
if "collected_sites" not in st.session_state:
    st.session_state.collected_sites = []


if not st.session_state.journey_started:
    st.title("🧭 Start Your Cultural Time Travel Journey")
    st.markdown(
        """
        Welcome to your immersive exploration of India’s cultural heritage. 
        Discover timeless destinations, rich narratives, and hidden gems curated just for you.

        Click below to begin your journey!
        """
    )
    if st.button("Begin Journey"):
        st.session_state.df_filtered = df.reset_index(drop=True)  # show all sites
        st.session_state.journey_started = True
        st.rerun()
else:
    df_filtered = st.session_state.df_filtered
    if st.session_state.site_index < len(df_filtered):
        site = df_filtered.iloc[st.session_state.site_index]

        # Title with clickable link to gov report
        site_title = f"[{site['location']}]({site['gov_report_url']})"
        st.markdown(f"## {site_title}")

        # Side-by-side layout: bigger image, smaller description
        img_col, desc_col = st.columns([4, 2])  # 4:2 = 2/3 of screen for image

        with img_col:
            st.image(site["image_url"], use_container_width=True)

        with desc_col:
            try:
                import requests
                description_text = requests.get(site["description_url"]).text
                st.markdown(description_text)
            except:
                st.warning("Description not available.")


        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🪔 Collect Artifact"):
                st.session_state.collected_sites.append({
                    "location": site["location"],
                    "image": site["artifact_image_url"],
                })
        with col2:
            if st.button("Continue to Next Site"):
                st.session_state.site_index += 1
                st.rerun()

    else:
        st.title("🧳 Your Cultural Revival Route")

        if st.session_state.collected_sites:
            st.markdown("## 🧳 Collected Artifacts")

            for i in range(0, len(st.session_state.collected_sites), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(st.session_state.collected_sites):
                        item = st.session_state.collected_sites[i + j]
                        with cols[j]:
                            st.image(item["image"], caption=item["location"], use_container_width=True)
        else:
            st.info("You didn't collect any artifacts along the way.")

        # Restart option
        if st.button("🔄 Restart Journey"):
            st.session_state.site_index = 0
            st.session_state.journey_started = False
            st.session_state.collected_sites = []
            st.rerun()
