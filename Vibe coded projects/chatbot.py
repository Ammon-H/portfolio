import streamlit as st
import os
from pathlib import Path
import re
import datetime


# Load .env from parent folders (search upwards)
def _load_dotenv_upwards(filename: str = '.env', max_levels: int = 5) -> Path | None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return None
    p = Path(__file__).resolve().parent
    for _ in range(max_levels + 1):
        candidate = p / filename
        if candidate.exists():
            try:
                load_dotenv(dotenv_path=candidate)
                return candidate
            except Exception:
                return None
        if p.parent == p:
            break
        p = p.parent
    return None

# Try to load .env up to 3 levels above this script (private_chatbot -> AI -> ...)
_found = _load_dotenv_upwards('.env', max_levels=3)
if _found:
    print(f"Loaded .env from: {_found}")

# Attempt to import groq; handle missing package gracefully
try:
    import groq
except Exception:
    groq = None

# Optional: ICS support
try:
    from ics import Calendar as ICSCalendar, Event as ICSEvent
except Exception:
    ICSCalendar = None
    ICSEvent = None


# Self-contained calendar storage and local command handling (separate from seer_core)
try:
    from dateutil import parser as _dateparser
except Exception:
    _dateparser = None

CALENDAR_FILE = Path(__file__).parent / 'chat_calendar.json'


def _load_calendar():
    if not CALENDAR_FILE.exists():
        return []
    try:
        import json
        return json.loads(CALENDAR_FILE.read_text(encoding='utf-8'))
    except Exception:
        return []


def _save_calendar(events):
    try:
        import json
        CALENDAR_FILE.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding='utf-8')
        return True
    except Exception:
        return False


def _parse_datetime(text: str):
    if _dateparser is not None:
        try:
            return _dateparser.parse(text, fuzzy=True)
        except Exception:
            return None
    # Fallback: accept ISO format
    try:
        return datetime.datetime.fromisoformat(text)
    except Exception:
        return None


def handle_local_command(speech: str):
    """
    Returns (handled: bool, reply: str).
    Handles:
      - current time
      - current date
      - add event
      - show events
    """
    low = speech.lower()

    # --- TIME ---
    if re.search(r"\b(what\s*time\s*is\s*it|what['s ]*the time|current time|tell me the time)\b", low):
        now = datetime.datetime.now().strftime("%I:%M %p").lstrip("0")
        return True, f"The current time is {now}."


    # --- DATE ---
    if re.search(r"\b  (what\s*date\s*is\s*it|today['s]* date|current date|what['s ]*the date)\b", low):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return True, f"Today is {today}."

    # --- ADD EVENT ---
    if any(k in low for k in ("add event", "create event", "schedule", "add to calendar")):
        
        # 1. Parse datetime
        dt = _parse_datetime(speech)
        if dt is None:
            return True, (
                "I couldn't understand the date/time. Try:\n"
                "'add event called Meeting on 2025-11-11 at 3pm for 2 hours'"
            )

        # 2. Parse title
        mtitle = re.search(r"(?:called|titled)\s+(.+?)(?:\s+on|\s+at|$)", speech, re.I)
        title = mtitle.group(1).strip() if mtitle else "Untitled Event"

        # 3. Parse duration
        duration = 60
        if mh := re.search(r"for (\d+)\s*hours?", low):
            duration = int(mh.group(1)) * 60
        elif mm := re.search(r"for (\d+)\s*minutes?", low):
            duration = int(mm.group(1))

        # 4. Save
        events = _load_calendar()
        events.append({
            "title": title,
            "start": dt.isoformat(),
            "duration_minutes": duration
        })
        _save_calendar(events)

        return True, (
            f"Added event:\n"
            f"- **{title}**\n"
            f"- {dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"- {duration} minutes"
        )

    # --- SHOW EVENTS ---
    if any(k in low for k in (
        "show events", "upcoming events",
        "what's on my calendar", "show calendar", "list events"
    )):
        events = _load_calendar()
        now = datetime.datetime.now()
        upcoming = []

        for e in events:
            dt = _parse_datetime(e.get("start"))
            if dt and dt >= now:
                upcoming.append((dt, e.get("title", "Untitled Event")))

        if not upcoming:
            return True, "No upcoming events."

        upcoming.sort()
        lines = [
            f"- {dt.strftime('%Y-%m-%d %H:%M')} — {title}"
            for dt, title in upcoming[:20]
        ]
        return True, "Upcoming events:\n" + "\n".join(lines)

    # No local command matched
    return False, ""


GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if GROQ_API_KEY is not None:
    GROQ_API_KEY = GROQ_API_KEY.strip().strip('"\'')

GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')

st.set_page_config(page_title='Minimal Chatbot', layout='wide')
st.title('Minimal Chatbot')

if groq is None:
    st.error('The `groq` Python package is not installed. Install it (pip install groq) and restart the app.')
    st.stop()

if not GROQ_API_KEY:
    st.error('Missing GROQ_API_KEY environment variable. Add it to your shell or a .env file and restart.')
    st.write('GROQ_API_KEY (repr):', repr(os.getenv('GROQ_API_KEY')))
    st.stop()

# Create client
try:
    groq_client = groq.Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error('Failed to create Groq client: ' + str(e))
    st.stop()

if 'chat' not in st.session_state:
    st.session_state.chat = []

with st.sidebar:
    st.markdown('**Settings**')
    st.write('Model: ', GROQ_MODEL)
    if st.button('Clear chat'):
        st.session_state.chat = []
    # ICS export UI
    if ICSCalendar is not None:
        if st.button('Export ICS'):
            events = _load_calendar()
            cal = ICSCalendar()
            for e in events:
                try:
                    ev = ICSEvent()
                    ev.name = e.get('title', 'Untitled')
                    start = _parse_datetime(e.get('start'))
                    if start is None:
                        continue
                    ev.begin = start
                    dur = e.get('duration_minutes', 60)
                    ev.duration = datetime.timedelta(minutes=int(dur))
                    cal.events.add(ev)
                except Exception:
                    continue
            ics_data = cal.serialize()
            st.download_button('Download calendar (.ics)', data=ics_data, file_name='chat_calendar.ics', mime='text/calendar')
    else:
        st.write('ICS export: install `ics` package to enable')
# --- Manual Event Entry (no popup, expandable form) ---
st.subheader("Add Event to Calendar")

with st.expander("Add a New Event"):
    with st.form("add_event_form"):
        title = st.text_input("Event Title")
        date = st.date_input("Event Date")
        time = st.time_input("Event Time")
        duration = st.number_input("Duration (minutes)", min_value=1, value=60)

        submitted = st.form_submit_button("Save Event")

        if submitted:
            dt = datetime.datetime.combine(date, time)

            events = _load_calendar()
            events.append({
                "title": title if title.strip() else "Untitled Event",
                "start": dt.isoformat(),
                "duration_minutes": duration
            })

            success = _save_calendar(events)
            if success:
                st.success(f"Event '{title}' added for {dt.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.error("Failed to save event.")


prompt = st.chat_input('Say something')

if prompt:
    st.session_state.chat.append({'role': 'user', 'content': prompt})
    reply = None

    with st.spinner("Thinking..."):
        # Try local command
        try:
            handled, msg = handle_local_command(prompt)
            if handled:
                reply = msg
        except Exception as e:
            reply = f"[Local command error] {e}"

        # If not handled → call LLM
        if reply is None:
            try:
                resp = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=st.session_state.chat,
                    max_tokens=1024
                )
                reply = resp.choices[0].message.content
            except Exception as e:
                reply = f"[LLM error] {e}"

        st.session_state.chat.append({'role': 'assistant', 'content': reply})


for msg in st.session_state.chat:
    st.chat_message(msg['role']).write(msg['content'])

# If an ICS export was prepared, show a download button
if st.session_state.get('_ics_export'):
    st.download_button('Download calendar (.ics)', data=st.session_state['_ics_export'], file_name='chat_calendar.ics', mime='text/calendar')
