import streamlit as st
import random
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

# Function to generate a fake-sounding but fictional NYC neighborhood via GPT
def generate_fake_neighborhood():
    prompt = """
Invent one plausible-sounding, entirely fictional New York City neighborhood name. 
It should resemble the naming conventions of real NYC neighborhoods (e.g., SoHo, Riverdale, Kips Bay, Flatbush), 
but must not be a real neighborhood.

Respond with only the name — no explanation, punctuation, or formatting.
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

# Game logic
def new_game():
    real_selection = random.sample(REAL_NEIGHBORHOOD_POOL, 29)
    fake = generate_fake_neighborhood()
    all_options = real_selection + [fake]
    random.shuffle(all_options)
    st.session_state.fake = fake
    st.session_state.options = all_options
    st.session_state.selected = None
    st.session_state.revealed = False

# UI Start
st.title("Find the Fake NYC Neighborhood")
st.write("Out of the 30 neighborhoods listed below, **one is completely made up** by AI. Can you spot the fake?")

# Start or restart the game
if "options" not in st.session_state or st.button("New Game"):
    new_game()

# Let user select a neighborhood
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

# Reveal all after guessing
if st.session_state.revealed:
    st.markdown("### Full List (with answer revealed):")
    for name in st.session_state.options:
        if name == st.session_state.fake:
            st.markdown(f"- **{name}** _(fake)_")
        else:
            st.markdown(f"- {name}")
