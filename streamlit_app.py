import html
import math
from datetime import datetime, timedelta

import streamlit as st


st.set_page_config(page_title="iRamble", page_icon="🗣️", layout="wide")


def initialise():
    if "rooms" not in st.session_state:
        st.session_state.rooms = [None] * 9
    if "selected" not in st.session_state:
        st.session_state.selected = None


def wedge(cx, cy, radius, start, end):
    start_r, end_r = math.radians(start), math.radians(end)
    x1, y1 = cx + radius * math.cos(start_r), cy + radius * math.sin(start_r)
    x2, y2 = cx + radius * math.cos(end_r), cy + radius * math.sin(end_r)
    return f"M {cx} {cy} L {x1:.1f} {y1:.1f} A {radius} {radius} 0 0 1 {x2:.1f} {y2:.1f} Z"


def circle_svg(room, number):
    if room is None:
        return f"""<svg viewBox='0 0 240 240' role='img' aria-label='Empty conversation circle {number}'>
          <circle cx='120' cy='120' r='102' fill='#fffdf9' stroke='#bdc8c7' stroke-width='2'/>
          <text x='120' y='108' text-anchor='middle' fill='#52646a' font-size='34'>+</text>
          <text x='120' y='143' text-anchor='middle' fill='#52646a' font-size='14' font-weight='700'>Reserve a talk</text>
        </svg>"""

    seconds = max(0, (room["starts"] - datetime.now()).total_seconds())
    opacity = 0.28 + 0.72 * min(1, seconds / 1800)
    taken = room["seats"]
    paths = []
    for seat in range(12):
        colour = "#174d50" if seat == 0 else ("#247b77" if seat < taken else "#fffdf9")
        paths.append(f"<path d='{wedge(120, 120, 104, -90 + seat * 30 + 1, -90 + (seat + 1) * 30 - 1)}' fill='{colour}' opacity='{opacity:.2f}'/>")
    minutes, secs = divmod(int(seconds), 60)
    status = "LIVE" if seconds == 0 else f"{minutes:02d}:{secs:02d}"
    topic = html.escape(room["topic"][:30] + ("…" if len(room["topic"]) > 30 else ""))
    return f"""<svg viewBox='0 0 240 240' role='img' aria-label='{topic}, {taken} of 12 seats filled'>
      {''.join(paths)}
      <circle cx='120' cy='120' r='61' fill='#f7f7f4'/>
      <text x='120' y='105' text-anchor='middle' fill='#213139' font-size='13' font-weight='700'>{topic}</text>
      <text x='120' y='130' text-anchor='middle' fill='#a44336' font-size='12' font-weight='700'>{status}</text>
      <text x='120' y='151' text-anchor='middle' fill='#52646a' font-size='11'>{taken}/12 seats</text>
    </svg>"""


def choose_room(index):
    room = st.session_state.rooms[index]
    if room is None:
        st.session_state.selected = index
    elif room["seats"] < 12:
        room["seats"] += 1
    else:
        st.toast("This conversation circle is full.")


initialise()

st.title("iRamble")
st.caption("Reserve a small conversation circle. The host begins the topic; up to 11 listeners can join.")

st.markdown("""
<style>
  .room-svg svg { width: 100%; max-width: 240px; display: block; margin: 0 auto; }
  div[data-testid="stButton"] button { width: 100%; }
</style>
""", unsafe_allow_html=True)

if st.session_state.selected is not None:
    index = st.session_state.selected
    st.subheader(f"Reserve circle {index + 1}")
    with st.form("reserve-room"):
        topic = st.text_input("What do you want to talk about?", placeholder="For example: How do you stay motivated?")
        minutes = st.number_input("Start in how many minutes?", min_value=1, max_value=240, value=15)
        left, right = st.columns(2)
        reserve = left.form_submit_button("Reserve talk", type="primary")
        cancel = right.form_submit_button("Cancel")
    if reserve and topic.strip():
        st.session_state.rooms[index] = {"topic": topic.strip(), "starts": datetime.now() + timedelta(minutes=int(minutes)), "seats": 1}
        st.session_state.selected = None
        st.rerun()
    if cancel:
        st.session_state.selected = None
        st.rerun()
    st.divider()

for row in range(3):
    columns = st.columns(3)
    for col in range(3):
        index = row * 3 + col
        room = st.session_state.rooms[index]
        with columns[col]:
            st.markdown(f"<div class='room-svg'>{circle_svg(room, index + 1)}</div>", unsafe_allow_html=True)
            if room is None:
                st.button("Reserve this circle", key=f"reserve-{index}", on_click=choose_room, args=(index,))
            elif room["seats"] < 12:
                st.button(f"Join a listener seat ({12 - room['seats']} open)", key=f"join-{index}", on_click=choose_room, args=(index,))
            else:
                st.button("Circle full", key=f"full-{index}", disabled=True)

st.divider()
st.caption("Prototype note: circles currently live only in your browser session. A real iRamble needs sign-in, a database, real-time room updates, and a voice service for shared conversations.")
