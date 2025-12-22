import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from gtts import gTTS

from app.agents.state import AgentState

# ------------------------------------------------------------------
# 1️⃣ ENV + LLM SETUP
# ------------------------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# ------------------------------------------------------------------
# 2️⃣ PATH RESOLUTION 
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

AUDIO_DIR = os.path.join(BASE_DIR, "data_samples")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ------------------------------------------------------------------
# 3️⃣ VOICE INTERACTION AGENT
# ------------------------------------------------------------------

def voice_interaction_node(state: AgentState) -> AgentState:
    """
    Generates a voice interaction transcript + MP3 audio
    for CRITICAL vehicle alerts only.
    """

    print("🎙️ [Voice Agent] Starting voice interaction node")

    # --------------------------------------------------------------
    # 3.1 PRIORITY GATE
    # --------------------------------------------------------------

    if state.get("priority_level") != "Critical":
        print("🟡 Not critical — skipping voice call")
        return state

    # --------------------------------------------------------------
    # 3.2 CONTEXT EXTRACTION (SAFE)
    # --------------------------------------------------------------

    vin = state.get("vin") or state.get("vehicle_id")
    owner = state.get("vehicle_metadata", {}).get("owner", "Customer")
    model = state.get("vehicle_metadata", {}).get("model", "Vehicle")
    diagnosis = state.get("diagnosis_report", "Critical fault detected")

    short_diagnosis = diagnosis.split("\n")[0]
    start_time = datetime.now()

    if not vin:
        print("❌ VIN missing — cannot generate audio")
        state["audio_available"] = False
        state["vin"] = None 
        return state

    # --------------------------------------------------------------
    # 3.3 LLM PROMPT
    # --------------------------------------------------------------

    prompt = f"""
You are an AI voice agent calling a vehicle owner.
... (rest of the prompt)
"""

    try:
        # ----------------------------------------------------------
        # 3.4 CALL LLM
        # ----------------------------------------------------------

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # Remove accidental markdown
        if content.startswith("```"):
            content = (
                content.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        transcript = json.loads(content)

        # ----------------------------------------------------------
        # 3.5 ADD TIMESTAMPS + COLLECT AI SPEECH
        # ----------------------------------------------------------
        
        current_time = start_time
        ai_lines = []
        
        for msg in transcript:
            if not isinstance(msg, dict):
                print(f"⚠️ Warning: Found non-dictionary item in transcript and skipped: {msg}")
                continue 
            
            msg["time"] = current_time.strftime("%H:%M:%S")
            current_time += timedelta(seconds=random.randint(5, 15))

            if msg.get("speaker") == "AI Agent":
                ai_lines.append(msg.get("text", ""))

        # ----------------------------------------------------------
        # 3.6 AUDIO GENERATION
        # ----------------------------------------------------------

        audio_filename = f"voice_recording_{vin}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        full_script = " ".join(ai_lines)

        tts = gTTS(text=full_script, lang="en", slow=False)
        tts.save(audio_path)

        print(f"🔊 Audio saved at local path: {audio_path}")

        # ----------------------------------------------------------
        # 3.7 SAVE TO AGENT STATE (Success Path)
        # ----------------------------------------------------------
        
        web_audio_path = f"/audio/{audio_filename}" 
        
        state["vin"] = vin 

        state["voice_transcript"] = transcript
        state["audio_file"] = audio_path 
        state["audio_url"] = web_audio_path 
        state["audio_available"] = True
        state["customer_decision"] = "BOOKED"
        state["scheduled_date"] = "Tomorrow 10:00 AM"

        print(f"✅ Voice interaction completed. Frontend URL: {web_audio_path}")

    except Exception as e:
        # ----------------------------------------------------------
        # 3.8 ERROR FALLBACK (FINAL CRITICAL FIX)
        # ----------------------------------------------------------
        print(f"❌ Voice Agent Failed: {e}")

        # Prepare safe fallback transcript
        state["voice_transcript"] = [
            {
                "id": 1,
                "speaker": "AI Agent",
                # Log the specific error that occurred
                "text": f"Voice interaction failed (LLM/JSON Error: {e.__class__.__name__}).",
                "time": "00:00:00"
            }
        ]
        
        # Nullify audio fields
        state["audio_available"] = False
        state["audio_url"] = None
        
        # 🚨 FINAL FIX: Ensure the VIN is saved back to the state 
        # using the 'vin' variable retrieved in section 3.2.
        # This prevents the subsequent KeyError in the FastAPI route.
        state["vin"] = vin 

    return state