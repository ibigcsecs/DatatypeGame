import streamlit as st
import random
import string

st.set_page_config(page_title="Data Type Sorter", layout="wide")
st.title("💾 Data Type Classification Simulator — Memory Cell Grid")

# --- Generate random data ---
integers = random.sample(range(1, 50), 7)
reals = [round(random.uniform(1, 99), 2) for _ in range(7)]
characters = random.sample(string.ascii_uppercase, 6)
data_items = integers + reals + characters
random.shuffle(data_items)

if "data_items" not in st.session_state:
    st.session_state.data_items = [str(x) for x in data_items]

st.markdown("""
### 🧩 Instructions
Drag each data value into the correct container:
- 🔢 **Integers** → Whole numbers (e.g., 7)
- 💧 **Reals** → Decimal numbers (e.g., 3.14)
- 🔤 **Characters** → Single letters (e.g., 'A')

Each correct drop shows an **index number** below it — just like memory cell locations.
""")

# --- HTML + JS ---
html_code = f"""
<style>
body {{
  background-color: #f0f2f6;
}}
.grid-container {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 20px;
  margin-top: 25px;
  padding: 10px;
}}
.box {{
  border: 3px solid #4c8bf5;
  border-radius: 12px;
  min-height: 240px;
  background-color: #ffffff;
  padding: 12px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
  text-align: center;
}}
.box:hover {{
  transform: scale(1.02);
}}
h3 {{
  background-color: #4c8bf5;
  color: white;
  padding: 8px;
  border-radius: 8px;
  font-size: 1.1rem;
}}
.item {{
  display: inline-block;
  margin: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: #4c8bf5;
  color: white;
  cursor: grab;
  user-select: none;
  font-weight: 500;
}}
.correct {{
  background-color: #28a745 !important;
}}
.wrong {{
  background-color: #dc3545 !important;
}}
.index-label {{
  display: block;
  font-size: 12px;
  color: #222;
  margin-top: 4px;
  font-weight: bold;
}}
</style>

<div class="grid-container">
  <div id="available" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🎯 Available Data</h3>
    {"".join([f'<div id="item-{i}" class="item" draggable="true" ondragstart="drag(event)">{v}</div>' for i, v in enumerate(st.session_state.data_items)])}
  </div>

  <div id="integers" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🔢 Integers</h3>
  </div>

  <div id="reals" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>💧 Reals</h3>
  </div>

  <div id="characters" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🔤 Characters</h3>
  </div>
</div>

<script>
let counters = {{
  integers: 0,
  reals: 0,
  characters: 0
}};

function allowDrop(ev) {{
  ev.preventDefault();
}}
function drag(ev) {{
  ev.dataTransfer.setData("text", ev.target.id);
}}
function drop(ev) {{
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text");
  var dragged = document.getElementById(data);
  var val = dragged.innerText;
  var targetBox = ev.target.closest('.box');
  if (!targetBox) return;
  var targetId = targetBox.id;

  let type = "unknown";
  if (/^-?\\d+$/.test(val)) {{
    type = "integers";
  }} else if (/^-?\\d*\\.\\d+$/.test(val)) {{
    type = "reals";
  }} else if (/^[A-Za-z]$/.test(val)) {{
    type = "characters";
  }}

  if (type === targetId) {{
    targetBox.appendChild(dragged);
    dragged.classList.remove("wrong");
    dragged.classList.add("correct");

    // Remove any old index label
    let oldLabel = dragged.querySelector(".index-label");
    if (oldLabel) oldLabel.remove();

    // Create and append new index label
    let indexNum = counters[targetId];
    let label = document.createElement("span");
    label.className = "index-label";
    label.textContent = "Index: " + indexNum;
    dragged.appendChild(label);

    // Increment counter
    counters[targetId]++;

  }} else {{
    // Wrong drop → return to Available box
    let avail = document.getElementById("available");
    avail.appendChild(dragged);
    dragged.classList.add("wrong");
    setTimeout(() => dragged.classList.remove("wrong"), 800);

    // Remove index label if it had one
    let oldLabel = dragged.querySelector(".index-label");
    if (oldLabel) oldLabel.remove();
  }}
}}
</script>
"""

st.components.v1.html(html_code, height=700)