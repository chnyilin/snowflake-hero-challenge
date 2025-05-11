import streamlit as st
import pandas as pd
import altair as alt

# ----- App Config -----
st.set_page_config(layout="wide")

# ----- App State -----
if "story" not in st.session_state:
    st.session_state.story = None
if "story_selected" not in st.session_state:
    st.session_state.story_selected = False
if "start_clicked" not in st.session_state:
    st.session_state.start_clicked = False
if "era_index" not in st.session_state:
    st.session_state.era_index = 0
if "collected" not in st.session_state:
    st.session_state.collected = []
if "carbon" not in st.session_state:
    st.session_state.carbon = 0
if "carbon_log" not in st.session_state:
    st.session_state.carbon_log = []

# ----- Story Selection -----
if not st.session_state.story_selected:
    st.title("📚 Choose Your Journey")
    st.session_state.story = st.selectbox(
        "Select your storyline:",
        ["Time Traveler", "Monk's Pilgrimage", "Return Artifacts"]
    )
    if st.button("Begin Journey"):
        st.session_state.start_clicked = True

    if st.session_state.start_clicked:
        story_map = {
            "Time Traveler": "data/eras_time_traveler.csv",
            "Monk's Pilgrimage": "data/eras_monk_journey.csv",  # Add later
            "Return Artifacts": "data/eras_artifact_return.csv"  # Add later
        }
        try:
            df = pd.read_csv(story_map[st.session_state.story])
            st.session_state.df = df
            st.session_state.story_selected = True
        except FileNotFoundError:
            st.error("❌ Story data not found. Please check your CSV files in /data/")
            st.stop()

# ----- Journey Section -----
elif st.session_state.story_selected and st.session_state.df is not None:
    df = st.session_state.df

    if st.session_state.era_index < len(df):
        row = df.iloc[st.session_state.era_index]

        # ---- Layout: 2 columns (city image + artifact) ----
        st.markdown(f"<h1 style='text-align:center;'>{row['era']} — {row['location']}</h1>", unsafe_allow_html=True)
        city_col, artifact_col = st.columns([3, 1])
        with city_col:
            st.image(row['image_url'], use_container_width=True)
        with artifact_col:
            st.image(row['artifact_image_url'], caption=row['artifact_name'], use_container_width=True)

        # ---- Description below ----
        st.markdown(f"<p style='font-size:18px'>{row['description']}</p>", unsafe_allow_html=True)
        st.caption(row['artifact_description'])

        # ---- Carbon Tracker ----
        st.session_state.carbon += 25  # +25 kg CO2 per location
        st.session_state.carbon_log.append(st.session_state.carbon)
        st.metric("🌱 Carbon Footprint", f"{st.session_state.carbon} kg CO₂")

        # ---- Eco Actions ----
        eco_actions = {
            "Pick up trash": -3,
            "Use public transport": -5,
            "Avoid plastic": -2
        }
        choice = st.selectbox("Choose a responsible action to reduce your impact:", list(eco_actions.keys()))
        if st.button("Do it"):
            st.session_state.carbon += eco_actions[choice]
            st.success(f"✅ Action taken: {choice} (-{abs(eco_actions[choice])} kg CO₂)")
            st.session_state.carbon_log.append(st.session_state.carbon)

        # ---- Buttons ----
        if st.button("➕ Collect Artifact"):
            st.session_state.collected.append({
                "location": row['location'],
                "artifact": row['artifact_name']
            })

        if st.button("➡️ Next Era"):
            st.session_state.era_index += 1

    else:
        st.success("🎉 You've completed your journey!")

        # Responsible Traveler Badge
        if st.session_state.carbon < 80:
            st.balloons()
            st.success("🏆 You've earned the Responsible Traveler badge!")

    # ---- Collected Artifacts ----
    st.markdown("---")
    st.subheader("🧺 Collected Artifacts")
    if st.session_state.collected:
        for item in st.session_state.collected:
            st.write(f"📍 {item['location']}: {item['artifact']}")
    else:
        st.info("You haven't collected any artifacts yet.")

    # ---- Carbon Footprint Chart ----
    st.markdown("---")
    st.subheader("📈 Your Carbon Footprint Over Time")
    df_chart = pd.DataFrame({"Era": list(range(1, len(st.session_state.carbon_log)+1)), "Carbon": st.session_state.carbon_log})
    chart = alt.Chart(df_chart).mark_line(point=True).encode(
        x="Era",
        y="Carbon"
    ).properties(width=700)
    st.altair_chart(chart, use_container_width=True)
