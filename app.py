import streamlit as st

# Initialize app state
if "screen" not in st.session_state:
    st.session_state.screen = "start"
if "travel_log" not in st.session_state:
    st.session_state.travel_log = []

# Screen 1: Choose Your Journey
if st.session_state.screen == "start":
    st.title("✨ Choose Your Journey")
    traveler = st.selectbox("Who are you?", ["Alien", "Ancient Monk", "Time Traveler"])
    season = st.selectbox("When are you traveling?", ["Winter", "Summer", "Monsoon"])
    interests = st.multiselect("What interests you?", ["Festivals", "Temples", "Folk Arts", "Dance", "Architecture"])

    if st.button("🛫 Begin Your Journey"):
        st.session_state.traveler = traveler
        st.session_state.season = season
        st.session_state.interests = interests
        st.session_state.screen = "explore"

# Screen 2: Explore India
elif st.session_state.screen == "explore":
    st.title(f"🌏 Welcome to India, {st.session_state.traveler}!")
    st.write(f"🗓 Season: {st.session_state.season}")
    st.write(f"🎨 Interests: {', '.join(st.session_state.interests)}")

    st.subheader("📍 Destinations for You")

    # Dummy data for now
    places = [
        {"name": "Varanasi", "highlight": "Ganga Aarti", "image": "https://upload.wikimedia.org/wikipedia/commons/7/77/Ganga_Aarti.jpg"},
        {"name": "Hampi", "highlight": "Stone Temples", "image": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Vittala_Temple%2C_Hampi.jpg"},
        {"name": "Kolkata", "highlight": "Durga Puja", "image": "https://upload.wikimedia.org/wikipedia/commons/0/05/Durga_Puja_Kolkata.jpg"}
    ]

    for place in places:
        st.image(place["image"], caption=place["name"], use_column_width=True)
        st.markdown(f"**Highlight**: {place['highlight']}")
        if st.button(f"➕ Add {place['name']} to My Travel Plan", key=place["name"]):
            if place["name"] not in st.session_state.travel_log:
                st.session_state.travel_log.append(place["name"])

    st.markdown("---")
    st.subheader("🧳 Your Travel Log")
    st.write(st.session_state.travel_log)
