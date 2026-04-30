"""
voice_input.py
--------------
Streamlit component that embeds a Web Speech API microphone button.
Returns transcribed text via streamlit query params or component value.
"""

import streamlit.components.v1 as components


def voice_input_component(key: str = "voice") -> str:
    """
    Render an embedded voice input button using the Web Speech API.
    Returns the transcribed text string (empty string if nothing spoken).
    """
    html = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Georgia', serif; background: transparent; display: flex;
         align-items: center; gap: 12px; padding: 4px; }

  #mic-btn {
    width: 52px; height: 52px; border-radius: 50%;
    border: 2px solid #C9A84C;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    cursor: pointer; display: flex; align-items: center;
    justify-content: center; transition: all 0.3s ease;
    box-shadow: 0 2px 12px rgba(201,168,76,0.3);
    flex-shrink: 0;
  }
  #mic-btn:hover { transform: scale(1.08); box-shadow: 0 4px 20px rgba(201,168,76,0.5); }
  #mic-btn.listening {
    background: linear-gradient(135deg, #8B0000 0%, #C41E3A 100%);
    border-color: #FF6B6B;
    animation: pulse 1.2s infinite;
  }
  @keyframes pulse {
    0%, 100% { box-shadow: 0 2px 12px rgba(255,107,107,0.4); }
    50% { box-shadow: 0 2px 24px rgba(255,107,107,0.8); transform: scale(1.05); }
  }

  #mic-icon { font-size: 22px; }

  #status-area { display: flex; flex-direction: column; gap: 2px; }
  #status { font-size: 11px; color: #C9A84C; font-style: italic; letter-spacing: 0.5px; }
  #transcript-display {
    font-size: 13px; color: #E8D5A3; max-width: 300px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }

  #copy-btn {
    padding: 6px 14px; background: #C9A84C; color: #0a0a0a;
    border: none; border-radius: 4px; cursor: pointer;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; display: none; transition: all 0.2s;
    flex-shrink: 0;
  }
  #copy-btn:hover { background: #E8D5A3; }
  #copy-btn.visible { display: block; }

  #not-supported {
    color: #FF6B6B; font-size: 12px; display: none;
  }
</style>
</head>
<body>

<button id="mic-btn" title="Click to speak">
  <span id="mic-icon">🎙️</span>
</button>

<div id="status-area">
  <span id="status">Click mic to speak</span>
  <span id="transcript-display"></span>
</div>

<button id="copy-btn">Use This →</button>
<span id="not-supported"></span>

<script>
const micBtn = document.getElementById('mic-btn');
const micIcon = document.getElementById('mic-icon');
const statusEl = document.getElementById('status');
const transcriptDisplay = document.getElementById('transcript-display');
const copyBtn = document.getElementById('copy-btn');
const notSupported = document.getElementById('not-supported');

let recognition = null;
let finalTranscript = '';
let isListening = false;

// Check browser support
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
  notSupported.style.display = 'inline';
  notSupported.textContent = '⚠️ Voice not supported in this browser. Use Chrome.';
  micBtn.disabled = true;
  micBtn.style.opacity = '0.4';
} else {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.lang = 'en-US';
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening = true;
    micBtn.classList.add('listening');
    micIcon.textContent = '⏺️';
    statusEl.textContent = 'Listening…';
    transcriptDisplay.textContent = '';
    copyBtn.classList.remove('visible');
    finalTranscript = '';
  };

  recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const t = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += t;
      } else {
        interim += t;
      }
    }
    transcriptDisplay.textContent = finalTranscript || interim;
  };

  recognition.onerror = (event) => {
    statusEl.textContent = `Error: ${event.error}. Try again.`;
    stopListening();
  };

  recognition.onend = () => {
    stopListening();
    if (finalTranscript.trim()) {
      statusEl.textContent = 'Got it! Press "Use This →" to send.';
      copyBtn.classList.add('visible');
    } else {
      statusEl.textContent = 'Nothing captured. Try again.';
    }
  };
}

function stopListening() {
  isListening = false;
  micBtn.classList.remove('listening');
  micIcon.textContent = '🎙️';
}

micBtn.addEventListener('click', () => {
  if (!recognition) return;
  if (isListening) {
    recognition.stop();
  } else {
    try {
      recognition.start();
    } catch (e) {
      statusEl.textContent = 'Please wait a moment and try again.';
    }
  }
});

copyBtn.addEventListener('click', () => {
  if (finalTranscript.trim()) {
    // Send to Streamlit via postMessage
    window.parent.postMessage({
      type: 'streamlit:setComponentValue',
      value: finalTranscript.trim()
    }, '*');
    statusEl.textContent = '✓ Sent to concierge';
    copyBtn.classList.remove('visible');
    transcriptDisplay.textContent = '';
    finalTranscript = '';
  }
});
</script>
</body>
</html>
"""
    return components.html(html, height=70, scrolling=False)
