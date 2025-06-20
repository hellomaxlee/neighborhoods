import streamlit as st
import random
import time
from openai import OpenAI
from streamlit_autorefresh import st_autorefresh

# Load OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Full pool of real NYC neighborhoods
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

# Generate a fake neighborhood via OpenAI
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

# Start a new game
def new_game():
    real_selection = random.sample(REAL_NEIGHBORHOOD_POOL, 29)
    fake = generate_fake_neighborhood()
    all_options = real_selection + [fake]
    random.shuffle(all_options)
    
    st.session_state.options = all_options
    st.session_state.fake = fake
    st.session_state.selected = None
    st.session_state.revealed = False

# Title and instructions
st.title("Find the Fake NYC Neighborhood")
st.write("Out of the 30 neighborhoods listed below, **one is completely made up**. Can you spot the fake?")

# Cooldown enforcement and auto-refresh
if "cooldown_until" in st.session_state:
    remaining = int(st.session_state["cooldown_until"] - time.time())
    if remaining > 0:
        st.warning("You guessed wrong. Please wait before trying again.")
        st.markdown(f"**Time remaining: {remaining} seconds**")
        st_autorefresh(interval=1000, limit=remaining + 1)
        st.stop()
    else:
        del st.session_state["cooldown_until"]
        st.session_state["revealed"] = False
        new_game()  # 🔁 Automatically start a fresh game after cooldown

# Start or reset game
if "options" not in st.session_state or st.button("New Game"):
    st.session_state["revealed"] = False
    new_game()

# Display options
selected = st.radio("Which neighborhood do you think is fake?", st.session_state.options, key="neighborhood_guess")
st.session_state.selected = selected

# Guess submission
if st.button("Submit Guess"):
    st.session_state.revealed = True
    if st.session_state.selected == st.session_state.fake:
        st.success("✅ Correct! You found the fake neighborhood.")
    else:
        st.error(f"❌ Incorrect. The fake neighborhood was: **{st.session_state.fake}**.")
        st.session_state["cooldown_until"] = time.time() + 60

# Reveal full list after guess
if st.session_state.get("revealed"):
    st.markdown("### Answer Key")
    for name in st.session_state.options:
        if name == st.session_state.fake:
            st.markdown(f"- **{name}** _(fake)_")
        else:
            st.markdown(f"- {name}")
