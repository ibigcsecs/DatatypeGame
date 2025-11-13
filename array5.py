import streamlit as st
import random

st.set_page_config(page_title="💾 Data Type Memory Grid", layout="wide")
st.title("💾 Data Type Classification — Memory Grid Simulator")

# --- Generate random data ---
def generate_data():
    integers = random.sample(range(1, 50), 10)
    reals = [round(random.uniform(1, 99), 2) for _ in range(10)]
    data_items = integers + reals
    random.shuffle(data_items)
    return [str(x) for x in data_items]

# --- Session State Setup ---
if "data_items" not in st.session_state:
    st.session_state.data_items = generate_data()

st.markdown("""
### 🧩 Instructions
- Drag each data value into its **correct container**:
  - 🔢 **Integers** → Whole numbers  
  - 💧 **Reals** → Decimal numbers (max 5 values)  
- Each correct drop shows an **index number** (starting from 0) inside that container.  
- Integers auto-regenerate once all are placed.
""")

# --- HTML + JS Section ---
html_code = f"""
<style>
body {{
  background-color: #eef1f6;
  font-family: 'Segoe UI', sans-serif;
}}
.grid-layout {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 25px;
  padding: 20px;
}}
.box {{
  border: 3px solid #4c8bf5;
  border-radius: 12px;
  background-color: #ffffff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  min-height: 250px;
  padding: 12px;
  text-align: center;
  transition: transform 0.2s ease, background-color 0.3s ease;
}}
.box:hover {{
  transform: scale(1.02);
  background-color: #f8fbff;
}}
h3 {{
  background-color: #4c8bf5;
  color: white;
  padding: 8px;
  border-radius: 8px;
  font-size: 1.1rem;
  margin-top: 0;
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
  transition: transform 0.2s ease;
}}
.item:hover {{
  transform: scale(1.05);
}}
.correct {{
  background-color: #28a745 !important;
}}
.wrong {{
  background-color: #dc3545 !important;
}}
.limit {{
  background-color: #ffb703 !important;
}}
.index-label {{
  display: block;
  font-size: 12px;
  color: #222;
  margin-top: 4px;
  font-weight: bold;
  opacity: 0;
  animation: fadeIn 0.8s forwards;
}}
@keyframes fadeIn {{
  0% {{ opacity: 0; transform: translateY(-5px); }}
  100% {{ opacity: 1; transform: translateY(0); }}
}}
</style>

<div class="grid-layout">
  <div id="available" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🎯 Available Data</h3>
    {"".join([f'<div id="item-{i}" class="item" draggable="true" ondragstart="drag(event)">{v}</div>' for i, v in enumerate(st.session_state.data_items)])}
  </div>

  <div id="integers" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>🔢 Integers</h3>
  </div>

  <div id="reals" class="box" ondrop="drop(event)" ondragover="allowDrop(event)">
    <h3>💧 Reals (Max 5)</h3>
  </div>
</div>

<script>
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

  // Count current items in reals
  let realBox = document.getElementById("reals");
  let realCount = realBox.querySelectorAll('.item').length;

  // Determine type
  let type = "unknown";
  if (/^-?\\d+$/.test(val)) {{
    type = "integers";
  }} else if (/^-?\\d*\\.\\d+$/.test(val)) {{
    type = "reals";
  }}

  // Reject if reals limit reached
  if (targetId === "reals" && realCount >= 5) {{
    dragged.classList.add("limit");
    setTimeout(() => dragged.classList.remove("limit"), 800);
    return;
  }}

  // Correct drop
  if (type === targetId) {{
    targetBox.appendChild(dragged);
    dragged.classList.remove("wrong");
    dragged.classList.add("correct");

    // Remove any old index label
    let oldLabel = dragged.querySelector(".index-label");
    if (oldLabel) oldLabel.remove();

    // Compute index for that box
    let items = targetBox.querySelectorAll(".item");
    let index = items.length - 1;

    // Create and append label
    let label = document.createElement("span");
    label.className = "index-label";
    label.textContent = "Index: " + index;
    dragged.appendChild(label);
  }} 
  else {{
    // Wrong drop → return to available
    let avail = document.getElementById("available");
    avail.appendChild(dragged);
    dragged.classList.add("wrong");
    setTimeout(() => dragged.classList.remove("wrong"), 800);

    let oldLabel = dragged.querySelector(".index-label");
    if (oldLabel) oldLabel.remove();
  }}

  // Check if integers are exhausted
  checkIntegers();
}}

function checkIntegers() {{
  let availableItems = document.querySelectorAll("#available .item");
  let anyIntegers = false;
  availableItems.forEach(it => {{
    let val = it.innerText;
    if (/^-?\\d+$/.test(val)) {{
      anyIntegers = true;
    }}
  }});
  if (!anyIntegers) {{
    window.parent.postMessage({{ type: 'generate_integers' }}, '*');
  }}
}}

window.addEventListener('message', (event) => {{
  if (event.data.type === 'regenerate_done') {{
    location.reload();
  }}
}});
</script>
"""

st.components.v1.html(html_code, height=720)

# --- Handle regeneration ---
msg = st.experimental_get_query_params().get("msg")
if msg == ["generate_integers"]:
    new_ints = [str(x) for x in random.sample(range(51, 100), 5)]
    st.session_state.data_items.extend(new_ints)
    st.experimental_set_query_params(msg="regenerate_done")