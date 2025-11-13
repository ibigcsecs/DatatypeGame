import streamlit as st
import random
import string

st.set_page_config(page_title="Memory Cell Simulator", layout="wide")
st.title("💾 Interactive Memory Cell Simulator (Indexed Memory Cells)")

# --- Generate random data ---
integers = random.sample(range(1, 50), 7)
reals = [round(random.uniform(1, 99), 2) for _ in range(7)]
characters = random.sample(string.ascii_uppercase, 6)
data_items = integers + reals + characters
random.shuffle(data_items)

if "data_items" not in st.session_state:
    st.session_state.data_items = [str(x) for x in data_items]

st.markdown("""
### 🧠 Instructions
Drag each data value into its correct memory cell:
- 🔢 **Integer Cells** → Whole numbers (e.g., 3, 45)
- 💧 **Real Cells** → Decimal values (e.g., 7.25)
- 🔤 **Character Cells** → Single letters (e.g., 'K')
""")

# --- HTML and JS ---

html_code = f"""
<style>
body {{
  font-family: 'Segoe UI', sans-serif;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 20px;
  justify-items: center;
  align-items: start;
  margin-top: 20px;
}}
.box {{
  width: 95%;
  min-height: 220px;
  border: 3px solid #ccc;
  border-radius: 12px;
  padding: 10px;
  text-align: center;
  background-color: #fefefe;
  box-shadow: 0 0 10px rgba(0,0,0,0.05);
  position: relative;
  overflow: hidden;
}}
#available {{
  grid-column: span 2;
  background: linear-gradient(145deg, #e3f2fd, #f9f9f9);
  border-color: #90caf9;
}}
.item-container {{
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  margin: 4px auto;
  width: fit-content;
}}
.item {{
  display: inline-block;
  padding: 8px 12px;
  border-radius: 8px;
  background-color: #4c8bf5;
  color: white;
  cursor: grab;
  user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.item:hover {{
  transform: scale(1.05);
  box-shadow: 0 0 8px rgba(0,0,0,0.3);
}}
.index-label {{
  opacity: 0;
  font-size: 13px;
  font-weight: 600;
  color: #444;
  background-color: #e8f0fe;
  border-radius: 6px;
  padding: 4px 6px;
  animation: fadeIn 0.8s ease forwards;
}}
.correct {{
  background-color: #28a745 !important;
}}
.wrong {{
  background-color: #dc3545 !important;
}}
@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateX(-5px); }}
  to {{ opacity: 1; transform: translateX(0); }}
}}
/* Glow effect for correct cell */
.glow {{
  box-shadow: 0 0 20px 5px #4c8bf5 inset;
  animation: glowFade 1.5s ease;
}}
@keyframes glowFade {{
  from {{ box-shadow: 0 0 20px 5px #4c8bf5 inset; }}
  to {{ box-shadow: none; }}
}}
/* Animated line (bus) */
.bus-line {{
  position: absolute;
  height: 3px;
  background: linear-gradient(to right, #4c8bf5, transparent);
  top: 50%;
  left: 0;
  width: 0;
  animation: moveLine 1s ease forwards;
}}
@keyframes moveLine {{
  from {{ width: 0; opacity: 0; }}
  to {{ width: 100%; opacity: 1; }}
}}
</style>

<div class="grid">
  <div id="available" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🎯 Available Data</h3>
    {"".join([f'<div id="item-{i}" class="item-container"><div class="item" draggable="true" ondragstart="drag(event)">{v}</div></div>' for i, v in enumerate(st.session_state.data_items)])}
  </div>

  <div id="integers" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🔢 Integer Memory Cells</h3>
  </div>

  <div id="reals" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>💧 Real Memory Cells</h3>
  </div>

  <div id="characters" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🔤 Character Memory Cells</h3>
  </div>
</div>

<script>
const cellIndexes = {{ integers: 0, reals: 0, characters: 0 }};

function allowDrop(ev) {{
  ev.preventDefault();
}}

function drag(ev) {{
  ev.dataTransfer.setData("text", ev.target.outerHTML);
  ev.dataTransfer.setData("id", ev.target.id);
}}

function drop(ev) {{
  ev.preventDefault();
  var htmlData = ev.dataTransfer.getData("text");
  var tempDiv = document.createElement("div");
  tempDiv.innerHTML = htmlData;
  var dragged = tempDiv.firstChild;
  var val = dragged.innerText;
  var targetBox = ev.target.closest('.box');
  var targetId = targetBox.id;

  let type = "unknown";
  if (/^-?\\d+$/.test(val)) type = "integers";
  else if (/^-?\\d*\\.\\d+$/.test(val)) type = "reals";
  else if (/^[A-Za-z]$/.test(val)) type = "characters";

  // Bus animation line
  let bus = document.createElement('div');
  bus.classList.add('bus-line');
  targetBox.appendChild(bus);
  setTimeout(() => bus.remove(), 1200);

  if (type === targetId) {{
    targetBox.classList.add('glow');
    setTimeout(() => targetBox.classList.remove('glow'), 1500);

    let idx = cellIndexes[targetId]++;
    let wrapper = document.createElement('div');
    wrapper.classList.add('item-container');

    let indexLabel = document.createElement('div');
    indexLabel.classList.add('index-label');
    indexLabel.innerText = idx;

    wrapper.appendChild(indexLabel);
    wrapper.appendChild(dragged);

    targetBox.appendChild(wrapper);
  }} else {{
    let avail = document.getElementById("available");
    let wrapper = document.createElement('div');
    wrapper.classList.add('item-container');
    wrapper.appendChild(dragged);
    avail.appendChild(wrapper);

    dragged.classList.add("wrong");
    setTimeout(() => dragged.classList.remove("wrong"), 800);
  }}
}}
</script>
"""

st.components.v1.html(html_code, height=750)