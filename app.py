import streamlit as st
import google.generativeai as genai
import os
import time
import base64
import io
import math
import struct
import wave

# --- Helper: Generate alarm sound WAV ---
def generate_alarm_wav():
    sample_rate = 44100
    duration = 3.0  # seconds
    frequency = 987.77  # B5 note
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            pulse = 1 if (int(t * 10) % 2 == 0) else 0
            val = math.sin(2 * math.pi * frequency * t) * pulse
            val_int = int(val * 32767)
            wav_file.writeframes(struct.pack('h', val_int))
            
    return wav_buffer.getvalue()

# --- 1. Page Configuration & Styling ---
st.set_page_config(page_title="VibePilot Focus", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Space Grotesk', sans-serif;
        background: radial-gradient(circle at 50% 50%, #151630 0%, #0a0b14 100%) !important;
        color: #f1f1f6;
    }
    
    /* Glowing Title */
    .glowing-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 30%, #ff007f 70%, #7928ca 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 35px rgba(255, 0, 127, 0.2);
        text-align: center;
        margin-bottom: 2px;
        margin-top: -20px;
    }
    
    .glowing-subtitle {
        font-size: 1.1rem;
        color: #8b8ea9;
        text-align: center;
        margin-bottom: 35px;
    }
    
    /* Input Container Styling */
    .glass-card {
        background: rgba(22, 23, 45, 0.55);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    
    /* Inputs Styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #121324 !important;
        color: #f1f1f6 !important;
        border: 1px solid #2d2e4d !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
    }
    
    /* Primary Focus Button */
    div.stButton > button {
        background: linear-gradient(135deg, #ff007f 0%, #7928ca 50%, #00f2fe 100%);
        background-size: 200% auto;
        color: white !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 16px 32px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 24px rgba(121, 40, 202, 0.35) !important;
        transition: all 0.5s ease !important;
        letter-spacing: 1px;
        cursor: pointer;
        width: 100%;
        margin-top: 15px;
    }
    
    div.stButton > button:hover {
        background-position: right center;
        box-shadow: 0 12px 35px rgba(255, 0, 127, 0.55) !important;
        transform: translateY(-2px);
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Quotes card motivation */
    .quote-card {
        background: rgba(0, 212, 255, 0.05);
        border-left: 5px solid #00d4ff;
        border-radius: 4px 16px 16px 4px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.05);
    }
    .quote-font {
        font-size: 22px !important;
        font-style: italic;
        color: #00d4ff;
        line-height: 1.4;
        margin: 0;
    }
    
    /* Countdown Timer Display */
    .timer-card {
        background: rgba(14, 15, 25, 0.85);
        border: 1px solid rgba(0, 255, 136, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin: 25px 0;
        box-shadow: inset 0 0 20px rgba(0, 255, 136, 0.05), 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    .timer-font {
        font-size: 95px !important;
        text-align: center;
        color: #00ff88;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        text-shadow: 0 0 25px rgba(0, 255, 136, 0.35);
        margin: 0;
        letter-spacing: 2px;
    }
    
    /* Alarm message expired */
    .alarm-font {
        font-size: 40px !important;
        font-weight: 800;
        color: #ff4b4b;
        text-align: center;
        text-shadow: 0 0 20px rgba(255, 75, 75, 0.4);
        line-height: 1.3;
        margin-top: 20px;
    }
    
    /* System warning banners override */
    div[data-testid="stNotification"] {
        background-color: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid #ff4b4b !important;
        color: #f1f1f6 !important;
        border-radius: 12px !important;
    }
    
    /* Roadmap Card */
    .roadmap-card {
        background: rgba(121, 40, 202, 0.08) !important;
        border: 1px solid rgba(121, 40, 202, 0.25) !important;
        border-radius: 20px !important;
        padding: 25px !important;
        margin: 25px 0 !important;
        box-shadow: 0 8px 32px 0 rgba(121, 40, 202, 0.1) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .roadmap-title {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #ff007f !important;
        margin-bottom: 15px !important;
    }
    .roadmap-card p, .roadmap-card li {
        font-size: 16px !important;
        line-height: 1.6 !important;
        color: #d1d2e0 !important;
        margin-bottom: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="glowing-title">⚡ VibePilot: Focus Protocol</h1>', unsafe_allow_html=True)
st.markdown('<p class="glowing-subtitle">The Anti-Procrastination Agent | Vaporize Sloth. Take Action Now.</p>', unsafe_allow_html=True)

# --- 2. Secure API Connection ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    st.warning("⚠️ System Vault Locked: 'GEMINI_API_KEY' secret/environment variable is missing.")
else:
    genai.configure(api_key=api_key)

# --- 3. User Inputs ---
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
task_name = st.text_input("🎯 What is your mission?", placeholder="e.g., Code the landing page...")
minutes = st.number_input("⏱️ How many minutes do you need to focus?", min_value=1, max_value=240, value=25)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. The Action Engine ---
if st.button("🚀 ACTIVATE FOCUS PROTOCOL", use_container_width=True, type="primary"):
    if not task_name:
        st.error("Hold up! You need to enter a mission first.")
    elif not api_key:
        st.error("API Key missing. The AI brain is offline.")
    else:
        with st.spinner("VibeEngine generating custom psychological focus contract..."):
            try:
                # Ask Gemini for motivation and roadmap
                model = genai.GenerativeModel('gemini-3.5-flash')
                prompt = f"""
                You are VibePilot, a high-performance productivity coach.
                The user has exactly {minutes} minutes to complete this task: '{task_name}'.
                They are procrastinating.

                Provide two parts in your response, separated exactly by a triple dash: ---
                PART 1: A 2-sentence, highly aggressive, no-nonsense motivational command to shock the user into working right now. No pleasantries.
                PART 2: A 3-step distraction-busting roadmap (structured as timeline suggestions based on the {minutes}-minute window) showing what to do to avoid distractions and finish on time. Keep steps short, actionable, and formatted in clean markdown with emojis.
                """
                response = model.generate_content(prompt)
                
                # Split response into motivation quote and roadmap
                parts = response.text.split("---")
                motivation_text = parts[0].strip() if len(parts) > 0 else "Get to work!"
                roadmap_text = parts[1].strip() if len(parts) > 1 else "Focus and complete your mission on time."
                
                # Display Motivation
                st.markdown(f'<div class="quote-card"><p class="quote-font">"{motivation_text}"</p></div>', unsafe_allow_html=True)

                # Display Roadmap
                st.markdown('<div class="roadmap-card"><p class="roadmap-title">🗺️ DISTRACTION-BUSTER ROADMAP</p>', unsafe_allow_html=True)
                st.markdown(roadmap_text)
                st.markdown('</div>', unsafe_allow_html=True)

                # Start Live Timer
                timer_placeholder = st.empty()
                total_seconds = int(minutes * 60)
                
                for i in range(total_seconds, -1, -1):
                    mins, secs = divmod(i, 60)
                    time_format = f"{mins:02d}:{secs:02d}"
                    timer_placeholder.markdown(f'<div class="timer-card"><p class="timer-font">{time_format}</p></div>', unsafe_allow_html=True)
                    time.sleep(1)
                
                # Time's Up Alarm Trigger
                st.balloons()
                timer_placeholder.empty() # Clear the timer
                
                try:
                    # Generate and play the alarm audio in background
                    alarm_bytes = generate_alarm_wav()
                    audio_b64 = base64.b64encode(alarm_bytes).decode()
                    audio_html = f'<audio autoplay src="data:audio/wav;base64,{audio_b64}"></audio>'
                    st.markdown(audio_html, unsafe_allow_html=True)
                except Exception as audio_err:
                    st.error(f"Could not trigger alarm voice: {audio_err}")

                st.markdown(f'<p class="alarm-font">🚨 TIME IS UP 🚨<br>MISSION EXPIRED:<br>{task_name.upper()}</p>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"AI Connection Error: {e}")