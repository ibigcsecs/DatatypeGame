import streamlit as st
import random
import string
import time
import pandas as pd
import os

st.set_page_config(page_title="Gamified Data Type Sorter — Stable Scoring + Leaderboard", layout="wide")
st.title("🧠 Data Type Classification Simulator — Stable Scoring + Leaderboard")

# --- Configuration ---
GAME_DURATION = 60  # seconds
RESULTS_FILE = "results.csv"

# --- Utilities ---
def generate_data():
    integers = random.sample(range(1, 100), 5)
    reals = [round(random.uniform(1, 99), 2) for _ in range(5)]
    characters = random.sample(string.ascii_uppercase, 4)
    booleans = [random.choice(["True", "False"]) for _ in range(3)]
    strings = [random.choice(["Hello", "IB", "Code", "CS", "Data"]) for _ in range(3)]
    items = integers + reals + characters + booleans + strings
    random.shuffle(items)
    return [str(x) for x in items]

def detect_type(value: str):
    if value in ["True", "False"]:
        return "booleans"
    try:
        if "." in value:
            float(value)
            return "reals"
        else:
            int(value)
            return "integers"
    except ValueError:
        if len(value) == 1 and value.isalpha():
            return "characters"
        return "strings"

def save_result(name, score, duration_played):
    record = {"Name": name, "Score": score, "TimeTaken(s)": duration_played, "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    df.to_csv(RESULTS_FILE, index=False)

def load_leaderboard(n=10):
    if not os.path.exists(RESULTS_FILE):
        return pd.DataFrame(columns=["Name","Score","TimeTaken(s)","Timestamp"])
    df = pd.read_csv(RESULTS_FILE)
    df_sorted = df.sort_values(by=["Score","TimeTaken(s)"], ascending=[False, True])
    return df_sorted.head(n)

# --- Session state init ---
if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "data_items" not in st.session_state:
    st.session_state.data_items = generate_data()
if "available" not in st.session_state:
    st.session_state.available = st.session_state.data_items.copy()
if "integers" not in st.session_state:
    st.session_state.integers = []
if "reals" not in st.session_state:
    st.session_state.reals = []
if "characters" not in st.session_state:
    st.session_state.characters = []
if "booleans" not in st.session_state:
    st.session_state.booleans = []
if "strings" not in st.session_state:
    st.session_state.strings = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# --- Top bar: Name input & start/reset controls ---
col1, col2, col3 = st.columns([3,2,1])

with col1:
    name = st.text_input("👤 Enter your name:", value=st.session_state.student_name)
    if name and not st.session_state.start_time:
        # set the name but don't auto-start until user presses Start
        st.session_state.student_name = name

with col2:
    if st.button("▶️ Start / Restart"):
        # reset game state
        st.session_state.data_items = generate_data()
        st.session_state.available = st.session_state.data_items.copy()
        st.session_state.integers = []
        st.session_state.reals = []
        st.session_state.characters = []
        st.session_state.booleans = []
        st.session_state.strings = []
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.game_over = False
        if name:
            st.session_state.student_name = name
        else:
            st.warning("Please enter your name before starting.")
            st.stop()

with col3:
    if st.button("⏹️ End Now"):
        if not st.session_state.start_time:
            st.info("Game hasn't started yet.")
        else:
            st.session_state.game_over = True

# ensure name present to play
if not st.session_state.student_name:
    st.info("Enter your name and press Start to begin.")
    st.stop()

# --- Timer logic ---
if st.session_state.start_time and not st.session_state.game_over:
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(GAME_DURATION - elapsed, 0)
    if remaining <= 0:
        st.session_state.game_over = True
else:
    elapsed = 0
    remaining = GAME_DURATION

# --- Game over handling ---
if st.session_state.game_over:
    total_time = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
    st.warning("⏰ Time’s up!" if remaining == 0 else "🛑 Game ended.")
    st.success(f"🏆 Final Score for {st.session_state.student_name}: {st.session_state.score}")
    # Save results (only once per end)
    if st.session_state.start_time is not None:
        # Save and then clear start_time so we don't keep saving on reruns
        save_result(st.session_state.student_name, st.session_state.score, min(total_time, GAME_DURATION))
        st.info("📁 Your result has been saved to results.csv.")
        st.session_state.start_time = None
    # Show leaderboard below, but allow restart
    st.markdown("---")

# --- Top status display ---
status_col1, status_col2 = st.columns([1,1])
with status_col1:
    st.info(f"⏱️ Time left: {remaining} sec")
with status_col2:
    st.success(f"⭐ Score: {st.session_state.score}")

# --- Main game UI (only if not game over) ---
if not st.session_state.game_over:
    st.markdown("### 🎯 Place each item into the correct container")
    st.markdown("Select the target container for an item and click **Place**. Correct placements give +1 point; incorrect placements return the item to Available.")

    # layout: available items on left, containers on right
    left_col, right_col = st.columns([1,2])

    with left_col:
        st.subheader("Available Data")
        # Show a small grid of available items and UI to place them quickly
        # To make it fast, we show each item with a selectbox of target types and a Place button
        for idx, item in enumerate(st.session_state.available.copy()):
            key_select = f"sel_{idx}_{item}"
            key_btn = f"btn_{idx}_{item}"
            cols = st.columns([2,1])
            cols[0].markdown(f"**{item}**")
            target = cols[1].selectbox("", options=["integers","reals","characters","booleans","strings"], index=0, key=key_select, label_visibility="collapsed")
            place = st.button("Place", key=key_btn)
            if place:
                chosen = target
                correct_type = detect_type(item)
                # remove from available
                if item in st.session_state.available:
                    st.session_state.available.remove(item)
                # if correct -> add to container and +1 score
                if chosen == correct_type:
                    st.session_state.score += 1
                    st.success(f"Correct! +1 point ({item} → {chosen})", icon="✅")
                    st.session_state[chosen].append(item)
                else:
                    # wrong -> return to available (do nothing except flash)
                    st.warning(f"Wrong container for {item}. It has been returned to Available.", icon="⚠️")
                    # Put back at end
                    st.session_state.available.append(item)
                # quick rerun to update timer/score display
                st.rerun()

    with right_col:
        st.subheader("Containers")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🔢 Integers")
            st.write(st.session_state.integers if st.session_state.integers else "_(empty)_")
        with c2:
            st.markdown("#### 💧 Reals")
            st.write(st.session_state.reals if st.session_state.reals else "_(empty)_")
        with c3:
            st.markdown("#### 🔤 Characters")
            st.write(st.session_state.characters if st.session_state.characters else "_(empty)_")

        c4, c5 = st.columns(2)
        with c4:
            st.markdown("#### ⚙️ Booleans")
            st.write(st.session_state.booleans if st.session_state.booleans else "_(empty)_")
        with c5:
            st.markdown("#### 🧾 Strings")
            st.write(st.session_state.strings if st.session_state.strings else "_(empty)_")

# --- Leaderboard (always visible) ---
st.markdown("---")
st.header("🏆 Leaderboard (Top 10)")
leaderboard_df = load_leaderboard(10)
if leaderboard_df.empty:
    st.info("No results yet. Play a round to generate leaderboard entries.")
else:
    st.dataframe(leaderboard_df.reset_index(drop=True))

# --- Button to download results.csv if exists ---
if os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "rb") as f:
        st.download_button("⬇️ Download full results.csv", data=f, file_name=RESULTS_FILE, mime="text/csv")
