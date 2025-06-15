import streamlit as st
import random
import time
from openai import OpenAI

# Load OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Full population of real NYC neighborhoods
REAL_NEIGHBORHOOD_POOL = [
    "Harlem", "Astoria", "Flushing", "Bushwick", "SoHo", "TriBeCa", "Williamsburg",
    "Bedford-Stuyvesant", "Greenpoint", "Chelsea", "Chinatown", "East Village", "Upper East Side",
    "Upper West Side", "Lower East Side", "Morningside Heights", "Long Island City", "Jackson Heights",
    "Riverdale", "Flatbush", "Crown Heights", "Ditmas Park", "Red Hook", "DUMBO", "Park Slope",
    "Forest Hills", "Inwood", "NoHo", "Kips Bay", "St. George", "Gowanus", "Bay Ridge", "Ridgewood",
    "Roosevelt Island", "Battery Park City", "Hell's Kitchen", "Sunnyside", "Canarsie", "Woodside",
    "Midwood", "Carroll Gardens", "Maspeth", "Jamaica", "Rego Park", "Bayside", "Fort Greene",
    "Gravesend", "Sheepshead Bay", "Borough Park", "Corona", "Marine Park", "Elmhurst"
]

# Generate AI-created fake neighborhood name
def generate_fake_neighborhood():
    prompt = """
Invent one plausible-sounding, entirely fictional New York City neighborhood name. 
It should resemble real NYC neighborhoods (e.g., SoHo, Riverdale, Flatbush) but must not exist.

Respond with only the name. No punctuation or explanation.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=10
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT error: {e}"

# Create a new game
def new_game():
    # Handle cooldown
    # Countdown timer display
    if "cooldown_time" in st.session_state:
        remaining = st.session_state["cooldown_time"] - time.time()
        if remaining > 0:
            st.warning("⏳ Cooldown active! Try again soon.")
    
            # Display a countdown using session state + rerun
            if "last_count" not in st.session_state:
                st.session_state.last_count = int(remaining)

        st.markdown(f"**Please wait: {int(remaining)} seconds**")
        time.sleep(1)
        st.session_state.last_count -= 1
        st.experimental_rerun()

    real_selection = random.sample(REAL_NEIGHBORHOOD_POOL, 29)
    fake = generate_fake_neighborhood()
    all_options = real_selection + [fake]
    random.shuffle(all_options)

    st.session_state.fake = fake
    st.session_state.options = all_options
    st.session_state.selected = None
    st.session_state.revealed = False

# Initialize app
st.title("Find the Fake NYC Neighborhood")
st.write("Out of the 30 neighborhoods listed below, **one is completely made up** by AI. Can you spot the fake?")

# Countdown timer display
if "cooldown_time" in st.session_state:
    remaining = st.session_state["cooldown_time"] - time.time()
    if remaining > 0:
        st.warning("⏳ Cooldown active! Try again soon.")
        with st.empty():
            while remaining > 0:
                mins, secs = divmod(int(remaining), 60)
                st.markdown(f"**Please wait: {mins:02}:{secs:02}**")
                time.sleep(1)
                remaining = st.session_state["cooldown_time"] - time.time()
            st.experimental_rerun()

# Start or restart the game
if "options" not in st.session_state or st.button("New Game"):
    new_game()

# Don't continue if in cooldown state
if st.session_state.get("cooldown_active", False):
    st.stop()

# Show options
st.subheader("Neighborhoods")
selected = st.radio("Which one do you think is fake?", st.session_state.options, index=0)
st.session_state.selected = selected

# Submit guess
if st.button("Submit Guess"):
    st.session_state.revealed = True
    if st.session_state.selected == st.session_state.fake:
        st.success("Correct! You found the fake neighborhood.")
    else:
        st.error(f"Wrong! The fake neighborhood was: **{st.session_state.fake}**.")
        st.session_state["cooldown_time"] = time.time() + 30  # Set 30s cooldown

# Reveal all options
if st.session_state.revealed:
    st.markdown("### Full List (with answer revealed):")
    for name in st.session_state.options:
        if name == st.session_state.fake:
            st.markdown(f"- **{name}** _(fake)_")
        else:
            st.markdown(f"- {name}")
