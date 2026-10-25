
import json
import tempfile
from pathlib import Path

import streamlit as st
from src.voice import process_audio

ROOT = Path(__file__).resolve().parent
KB_DIR = ROOT / "kb"

st.set_page_config(
    page_title="VoiceOps | ZentroMart",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: #070c12;
    color: #e7edf5;
}
[data-testid="stSidebar"] {
    background: #0b121c;
    border-right: 1px solid #1b2a39;
}
.block-container {
    padding-top: 2rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #f2f7ff;
}
p, label, .stCaption {
    color: #a9bacb;
}
div[data-testid="stMetric"] {
    background: #0d1722;
    border: 1px solid #203345;
    border-radius: 12px;
    padding: 16px;
}
.stButton > button,
.stDownloadButton > button {
    background: #00df83;
    color: #04110c;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    min-height: 42px;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #00ff99;
    color: #04110c;
}
div[data-testid="stFileUploader"] {
    background: #0c1621;
    border: 1px dashed #31516a;
    border-radius: 12px;
    padding: 12px;
}
.vo-card {
    background: #0c1621;
    border: 1px solid #203345;
    border-radius: 13px;
    padding: 18px;
    margin-bottom: 12px;
}
.vo-green {
    color: #00ef91;
    font-weight: 700;
}
.vo-muted {
    color: #92a6ba;
    font-size: 13px;
}
hr {
    border-color: #203345;
}
</style>
""", unsafe_allow_html=True)


# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎧 VoiceOps")
    st.caption("ZentroMart Support Agent")
    st.divider()

    page = st.radio(
        "Navigation",
        ["Home", "Process Audio", "Knowledge Base", "History", "Settings"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### 🟢 Smarter Support")
    st.caption("Powered by RAG + Voice AI")
    st.markdown("---")
    st.markdown("### 🛒 ZentroMart")
    st.caption("Better Products. Happier You.")


# ---------- Home ----------
if page == "Home":
    st.markdown(
        '<p class="vo-green">● SYSTEM DASHBOARD</p>',
        unsafe_allow_html=True,
    )
    st.title("VoiceOps")
    st.write(
        "Turn customer questions into accurate, "
        "policy-grounded answers — with voice."
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, subtitle in [
        (c1, "🎙️", "Audio Transcription", "Speech to text"),
        (c2, "📚", "RAG Retrieval", "Relevant policy chunks"),
        (c3, "🤖", "AI Response", "Grounded answers"),
        (c4, "🔊", "Voice Synthesis", "Spoken replies"),
    ]:
        with col:
            st.markdown(
                f'<div class="vo-card"><h3>{icon}</h3>'
                f'<b>{title}</b><p class="vo-muted">'
                f'{subtitle}</p></div>',
                unsafe_allow_html=True,
            )

    st.subheader("Customer Support Workspace")
    left, right = st.columns([0.9, 1.1], gap="large")

    with left:
        st.markdown("### 1 · Upload Customer Audio")
        uploaded = st.file_uploader(
            "Choose a customer recording",
            type=["wav", "mp3", "m4a", "flac", "ogg"],
            key="home_audio",
        )

        if uploaded:
            st.audio(uploaded)
            st.caption(f"Selected file: {uploaded.name}")

        st.markdown("### 2 · Process")
        st.caption(
            "Run transcription, retrieval, answer generation, "
            "and voice synthesis."
        )

        if st.button(
            "▶  Process Audio",
            type="primary",
            use_container_width=True,
            key="home_process",
            disabled=uploaded is None,
        ):
            try:
                suffix = Path(uploaded.name).suffix.lower()

                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / f"customer{suffix}"
                    input_path.write_bytes(uploaded.getvalue())

                    with st.spinner(
                        "VoiceOps is processing the recording..."
                    ):
                        result = process_audio(input_path)

                st.session_state.result = result
                st.session_state.history.insert(0, {
                    "filename": uploaded.name,
                    "transcript": result.get("transcript", ""),
                    "reply": result.get("reply", ""),
                    "reply_audio": result.get("reply_audio", ""),
                    "chunks_file": result.get("chunks_file", ""),
                })
                st.success("Processing completed.")
            except Exception as exc:
                st.error(f"Processing failed: {exc}")

        st.markdown("### Recent Sessions")
        if not st.session_state.history:
            st.caption("Your processed sessions will appear here.")
        else:
            for item in st.session_state.history[:5]:
                st.markdown(
                    f"**{item['filename']}**  \n"
                    f"<span class='vo-green'>● Processed</span>",
                    unsafe_allow_html=True,
                )

    with right:
        st.markdown("### Live Results")
        result = st.session_state.result

        if not result:
            st.info(
                "Upload a recording and select Process Audio "
                "to view the transcript, response, and sources."
            )
        else:
            st.markdown(
                '<p class="vo-green">✓ PROCESSING COMPLETE</p>',
                unsafe_allow_html=True,
            )

            st.markdown("#### Customer Transcript")
            st.markdown(
                '<div class="vo-card">'
                + str(result.get("transcript", "No transcript returned."))
                + '</div>',
                unsafe_allow_html=True,
            )

            st.markdown("#### AI Support Response")
            st.markdown(
                '<div class="vo-card">'
                + str(result.get("reply", "No response returned."))
                + '</div>',
                unsafe_allow_html=True,
            )

            reply_path = Path(result.get("reply_audio", ""))
            if reply_path.is_file():
                st.markdown("#### 🔊 Generated Voice Reply")
                audio_bytes = reply_path.read_bytes()
                st.audio(audio_bytes, format="audio/wav")
                st.download_button(
                    "Download Reply Audio",
                    data=audio_bytes,
                    file_name="customer_reply.wav",
                    mime="audio/wav",
                )
            else:
                st.caption("No reply audio file was found.")

            st.markdown("#### 📚 Retrieved Knowledge Sources")
            chunks_path = Path(result.get("chunks_file", ""))

            if chunks_path.is_file():
                try:
                    chunks = json.loads(
                        chunks_path.read_text(encoding="utf-8")
                    )
                    st.json(chunks)
                except (json.JSONDecodeError, OSError):
                    st.text(
                        chunks_path.read_text(
                            encoding="utf-8",
                            errors="replace",
                        )
                    )
            else:
                st.caption("No saved chunks file was found.")


# ---------- Process Audio ----------
elif page == "Process Audio":
    st.title("🎙️ Process Customer Audio")
    st.write("Upload one recording to run the VoiceOps pipeline.")

    uploaded = st.file_uploader(
        "Customer recording",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        key="process_audio_page",
    )

    if uploaded:
        st.audio(uploaded)

        if st.button("▶  Run VoiceOps", type="primary"):
            try:
                suffix = Path(uploaded.name).suffix.lower()

                with tempfile.TemporaryDirectory() as temp_dir:
                    input_path = Path(temp_dir) / f"customer{suffix}"
                    input_path.write_bytes(uploaded.getvalue())

                    with st.spinner("Processing audio..."):
                        result = process_audio(input_path)

                st.session_state.result = result
                st.session_state.history.insert(0, {
                    "filename": uploaded.name,
                    "transcript": result.get("transcript", ""),
                    "reply": result.get("reply", ""),
                    "reply_audio": result.get("reply_audio", ""),
                    "chunks_file": result.get("chunks_file", ""),
                })
                st.success("Done!")

                st.subheader("Customer Transcript")
                st.write(result.get("transcript", ""))

                st.subheader("AI Response")
                st.write(result.get("reply", ""))

                reply_path = Path(result.get("reply_audio", ""))
                if reply_path.is_file():
                    st.subheader("Voice Reply")
                    st.audio(reply_path.read_bytes(), format="audio/wav")

                chunks_path = Path(result.get("chunks_file", ""))
                if chunks_path.is_file():
                    st.subheader("Retrieved Sources")
                    try:
                        st.json(json.loads(
                            chunks_path.read_text(encoding="utf-8")
                        ))
                    except json.JSONDecodeError:
                        st.text(chunks_path.read_text(encoding="utf-8"))

            except Exception as exc:
                st.error(f"Processing failed: {exc}")


# ---------- Knowledge Base ----------
elif page == "Knowledge Base":
    st.title("📚 Knowledge Base")
    st.write("Company policy documents available to the agent.")

    documents = sorted(KB_DIR.glob("*.md")) if KB_DIR.exists() else []

    if not documents:
        st.warning("No Markdown documents were found in the kb folder.")
    else:
        st.caption(f"{len(documents)} Markdown document(s) found.")

        for document in documents:
            with st.expander(document.name):
                st.text(document.read_text(
                    encoding="utf-8",
                    errors="replace",
                ))


# ---------- History ----------
elif page == "History":
    st.title("🕘 Session History")
    st.write("Recordings processed during this browser session.")

    if not st.session_state.history:
        st.info("No sessions yet. Process an audio recording first.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(item["filename"], expanded=(i == 0)):
                st.markdown("**Transcript**")
                st.write(item["transcript"])
                st.markdown("**AI Response**")
                st.write(item["reply"])

                reply_path = Path(item["reply_audio"])
                if reply_path.is_file():
                    st.audio(reply_path.read_bytes(), format="audio/wav")


# ---------- Settings ----------
elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("VoiceOps configuration status.")

    st.markdown("### Configuration")
    st.write("**Agent:** Existing VoiceOps Python pipeline")
    st.write("**Knowledge base:** `kb/`")
    st.write("**Input:** WAV, MP3, M4A, FLAC, OGG")

    st.caption(
        "API keys remain in your local .env file. "
        "This page does not display secret values."
    )

    st.markdown("### Privacy")
    st.write(
        "Uploaded recordings are passed to the existing processing "
        "pipeline. Audio transcription and AI services may process "
        "data externally according to their provider configurations."
    )
