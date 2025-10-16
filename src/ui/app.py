"""
F1 Service System - Streamlit UI.
Modern, futuristic interface with Red Bull Racing theme (red & black).

Features:
- Circuit image display
- F1 regulations queries
- Real-time responses with LangSmith tracing
- Minimalistic, high-tech design
"""

import streamlit as st
from pathlib import Path
import sys
import time
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.orchestrator import get_orchestrator
from loguru import logger

# Configure page
st.set_page_config(
    page_title="F1 Service System",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Red Bull Racing Theme (Red & Black)
st.markdown("""
<style>
    /* Import F1 Font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    /* Main background - Dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Title styling - Futuristic */
    h1 {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #dc0000 0%, #ff4444 50%, #dc0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 30px rgba(220, 0, 0, 0.5);
    }
    
    /* Subtitle */
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        text-align: center;
        color: #888888;
        letter-spacing: 2px;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Chat input box - Futuristic red glow */
    .stChatInput {
        background: rgba(20, 20, 20, 0.8) !important;
        border: 2px solid #dc0000 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(220, 0, 0, 0.3) !important;
    }
    
    .stChatInput input {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem !important;
        font-weight: 500;
    }
    
    .stChatInput input::placeholder {
        color: #666666 !important;
    }
    
    /* Chat messages - Modern cards */
    .stChatMessage {
        background: rgba(20, 20, 20, 0.6) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(220, 0, 0, 0.2) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Chat avatars ONLY - 300% bigger (target avatar container, not content images) */
    [data-testid="stChatMessageAvatarContainer"] img {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50%;
        border: 3px solid #dc0000;
        box-shadow: 0 0 20px rgba(220, 0, 0, 0.5);
    }
    
    /* User message - Red accent */
    [data-testid="stChatMessageContent"]:has(.user-message) {
        border-left: 4px solid #dc0000 !important;
    }
    
    /* Assistant message - Dark with subtle glow */
    [data-testid="stChatMessageContent"]:has(.assistant-message) {
        border-left: 4px solid #444444 !important;
    }
    
    /* Message text - Increased size and padding by 300% with Formula 1 font */
    .user-message, .assistant-message {
        font-family: 'Formula1', sans-serif;
        font-size: 2.0rem !important;
        line-height: 1.6;
        color: #e0e0e0;
        font-weight: 400;
        padding: 3.8rem !important;
    }
    
    /* Default message text */
    .stMarkdown {
        font-family: 'Formula1', 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e0e0e0;
        font-weight: 400;
    }
    
    /* Images - Futuristic frame */
    .stImage {
        border-radius: 15px;
        border: 2px solid #dc0000;
        box-shadow: 0 0 30px rgba(220, 0, 0, 0.4);
        overflow: hidden;
    }
    
    /* Buttons - Red Bull style */
    .stButton button {
        background: linear-gradient(135deg, #dc0000 0%, #aa0000 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 4px 15px rgba(220, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        box-shadow: 0 6px 25px rgba(220, 0, 0, 0.6);
        transform: translateY(-2px);
    }
    
    /* Sidebar - Dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f0f 0%, #1a0000 100%);
        border-right: 2px solid #dc0000;
    }
    
    /* Metrics - Racing style */
    .stMetric {
        background: rgba(20, 20, 20, 0.8);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(220, 0, 0, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stMetric label {
        color: #888888 !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #dc0000 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 2rem;
    }
    
    /* Loading spinner - Red */
    .stSpinner > div {
        border-top-color: #dc0000 !important;
    }
    
    /* Expander - Modern style */
    .streamlit-expanderHeader {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid rgba(220, 0, 0, 0.3);
        border-radius: 8px;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        color: #ffffff;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #dc0000;
        box-shadow: 0 0 15px rgba(220, 0, 0, 0.3);
    }
    
    /* Info box - Futuristic */
    .stAlert {
        background: rgba(220, 0, 0, 0.1);
        border: 1px solid rgba(220, 0, 0, 0.3);
        border-radius: 10px;
        color: #ffffff;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Code blocks - Terminal style */
    code {
        background: rgba(0, 0, 0, 0.6) !important;
        color: #dc0000 !important;
        border: 1px solid rgba(220, 0, 0, 0.3) !important;
        border-radius: 4px;
        padding: 2px 6px;
        font-family: 'Courier New', monospace;
    }
    
    /* Scrollbar - Red theme */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #dc0000 0%, #aa0000 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #ff0000 0%, #cc0000 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Racing stripe decoration */
    .racing-stripe {
        height: 4px;
        background: linear-gradient(90deg, 
            transparent 0%, 
            #dc0000 20%, 
            #dc0000 80%, 
            transparent 100%);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(220, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Initialize orchestrator
@st.cache_resource
def init_orchestrator():
    """Initialize orchestrator singleton."""
    logger.info("Initializing orchestrator for Streamlit UI")
    return get_orchestrator()


def display_welcome():
    """Display welcome screen with F1 branding."""
    # Load F1 logo as background
    logo_path = Path(__file__).parent / "f1-logo.avif"
    
    if logo_path.exists():
        import base64
        with open(logo_path, "rb") as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode()
        
        # Fullscreen background logo with centered title
        st.markdown(f"""
        <div style='
            position: relative;
            width: 100%;
            height: 300px;
            background-image: url(data:image/avif;base64,{img_base64});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 15px;
            overflow: hidden;
        '>
            <div style='
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, rgba(10,10,10,0.85) 0%, rgba(26,0,0,0.85) 100%);
            '></div>
            <h1 style='
                position: relative;
                z-index: 10;
                margin: 0;
                padding: 0;
            '>F1 SERVICE SYSTEM</h1>
        </div>
        <div class="racing-stripe"></div>
        """, unsafe_allow_html=True)
    else:
        # Fallback without background image
        st.markdown("""
        <h1>F1 SERVICE SYSTEM</h1>
        <div class="racing-stripe"></div>
        """, unsafe_allow_html=True)
    
    # Welcome message in columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Load Max Verstappen image for READY TO ASSIST frame
        max_img_path = Path(__file__).parent / "max.avif"
        max_img_html = ""
        if max_img_path.exists():
            import base64
            with open(max_img_path, "rb") as img_file:
                max_bytes = img_file.read()
                max_base64 = base64.b64encode(max_bytes).decode()
                max_img_html = f'<img src="data:image/avif;base64,{max_base64}" style="width: 90%; height: 800px; object-fit: cover; object-position: center top; margin-bottom: 1.5rem;">'
        
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem; background: rgba(20,20,20,0.6); 
                    border-radius: 15px; border: 1px solid rgba(220,0,0,0.3);'>
            {max_img_html}
            <h3 style='color: #dc0000; font-family: Orbitron; margin-bottom: 1rem;'>
                READY TO ASSIST
            </h3>
            <p style='color: #cccccc; font-size: 1.1rem; line-height: 1.8;'>
                • Query F1 circuit layouts and maps<br>
                • Access official FIA regulations<br>
                • Get instant, accurate answers<br>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add Max's theme music button
        music_path = Path(__file__).parent.parent.parent / "music" / "tu-tu-tu-du-max-verstappen.mp3"
        if music_path.exists():
            if st.button("It's Verstappen Time", use_container_width=True):
                st.audio(str(music_path), format="audio/mp3", autoplay=True)


def display_circuit_image(image_path: str, location: str):
    """Display circuit image with futuristic styling."""
    try:
        image = Image.open(image_path)
        
        # Display with caption - 90% width to fit on one page
        st.image(
            image,
            caption=f"🏁 {location.replace('_', ' ')} Circuit",
            width=int(image.width * 0.9)
        )
        
    except Exception as e:
        st.error(f"Failed to load circuit image: {e}")


def format_response_with_metadata(result: dict):
    """Format response with metadata display."""
    content = result.get('content', '')
    tools_used = result.get('tools_used', [])
    metadata = result.get('metadata', {})
    tool_results = result.get('tool_results', {})
    
    # Filter out image paths from content (remove lines containing circuit map paths)
    if content:
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            # Skip lines that look like file paths or source references
            if not any(keyword in line.lower() for keyword in [
                'f1_2025_circuit_maps',
                '_circuit.webp',
                'source:',
                'image source:',
                'path:',
                '/volumes/',
                'retrieved from:',
                'circuit.webp'
            ]):
                filtered_lines.append(line)
        content = '\n'.join(filtered_lines).strip()
    
    # Display main content (filtered)
    if content:
        st.markdown(f"<div class='assistant-message'>{content}</div>", unsafe_allow_html=True)
    
    # Display circuit image if available
    if 'get_circuit_image' in tool_results:
        circuit_result = tool_results['get_circuit_image']
        if circuit_result.get('type') == 'image':
            image_path = circuit_result.get('content')
            location = circuit_result.get('metadata', {}).get('location', 'Unknown')
            
            st.markdown("<div style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
            display_circuit_image(image_path, location)
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Metadata expander - Futuristic details
    with st.expander("🔍 Technical Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Tools Used",
                len(tools_used),
                delta=None
            )
        
        with col2:
            st.metric(
                "Iterations",
                metadata.get('iterations', 0),
                delta=None
            )
        
        with col3:
            model = metadata.get('model', 'N/A')
            st.metric(
                "Model",
                model.split('-')[0].upper() if model != 'N/A' else 'N/A',
                delta=None
            )
        
        # Tools breakdown
        if tools_used:
            st.markdown("**Tools Executed:**")
            for tool in tools_used:
                st.markdown(f"• `{tool}`")
        
        # Citations if available
        if 'query_regulations' in tool_results:
            reg_result = tool_results['query_regulations']
            citations = reg_result.get('metadata', {}).get('citations', [])
            
            if citations:
                st.markdown(f"**Citations:** {len(citations)} regulation sources")


def main():
    """Main Streamlit application."""
    
    # Display welcome header
    display_welcome()
    
    # Initialize orchestrator
    try:
        orchestrator = init_orchestrator()
    except Exception as e:
        st.error(f"❌ Failed to initialize orchestrator: {e}")
        st.stop()
    
    # Initialize chat history in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize conversation history for orchestrator (simple user/assistant pairs)
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Load custom avatar images
    user_avatar_path = Path(__file__).parent / "user-icon.png"
    chatbot_avatar_path = Path(__file__).parent / "chatbot-icon.png"
    
    user_avatar = str(user_avatar_path) if user_avatar_path.exists() else None
    chatbot_avatar = str(chatbot_avatar_path) if chatbot_avatar_path.exists() else None
    
    # Display chat history
    for message in st.session_state.messages:
        avatar = user_avatar if message["role"] == "user" else chatbot_avatar
        with st.chat_message(message["role"], avatar=avatar):
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'>{message['content']}</div>",
                           unsafe_allow_html=True)
            else:
                # Assistant message with full formatting
                format_response_with_metadata(message.get('result', {}))
    
    # Chat input
    if prompt := st.chat_input("Ask about F1 circuits or regulations..."):
        # Add user message to chat history (for display)
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)
        
        # Process query with orchestrator
        with st.chat_message("assistant", avatar=chatbot_avatar):
            with st.spinner("Processing...🏎️💨💨"):
                start_time = time.time()
                
                try:
                    # Call orchestrator WITH conversation history for context
                    result = orchestrator.process_query(
                        prompt,
                        conversation_history=st.session_state.conversation_history
                    )
                    elapsed_time = time.time() - start_time
                    
                    # Add response time to metadata
                    if 'metadata' not in result:
                        result['metadata'] = {}
                    result['metadata']['response_time'] = round(elapsed_time, 2)
                    
                    # Display response
                    format_response_with_metadata(result)
                    
                    # Add to chat history (for display with full metadata)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.get('content', ''),
                        "result": result
                    })
                    
                    # Add to conversation history (simple format for orchestrator context)
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": prompt
                    })
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": result.get('content', '')
                    })
                    
                    # Limit conversation history to last 20 messages (10 exchanges)
                    # to prevent token overflow
                    if len(st.session_state.conversation_history) > 20:
                        st.session_state.conversation_history = (
                            st.session_state.conversation_history[-20:]
                        )
                    
                except Exception as e:
                    error_msg = f"Error processing query: {str(e)}"
                    st.error(error_msg)
                    logger.error(error_msg)
    
    # Sidebar - System info
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #dc0000; font-family: Orbitron;'>SYSTEM</h2>
            <div class="racing-stripe"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # System status
        st.markdown("**Status:** 🟢 Online")
        st.markdown(f"**Model:** {orchestrator.model}")
        st.markdown(f"**Tools:** {len(orchestrator.tools)}")
        
        # Query count
        query_count = len([m for m in st.session_state.messages if m['role'] == 'user'])
        st.markdown(f"**Queries:** {query_count}")
        
        # Memory status
        memory_count = len(st.session_state.get('conversation_history', []))
        memory_indicator = "🧠 Active" if memory_count > 0 else "💤 Empty"
        st.markdown(f"**Memory:** {memory_indicator} ({memory_count // 2} exchanges)")
        
        st.markdown("<div class='racing-stripe' style='margin: 2rem 0;'></div>",
                   unsafe_allow_html=True)
        
        # Example queries
        st.markdown("**Quick Commands:**")
        
        if st.button("🏁 Show Monaco Circuit", use_container_width=True):
            st.session_state.example_query = "Show me the Monaco circuit"
            st.rerun()
        
        if st.button("📋 Points System", use_container_width=True):
            st.session_state.example_query = "How many points for 1st place?"
            st.rerun()
        
        if st.button("⚡ DRS Rules", use_container_width=True):
            st.session_state.example_query = "What are the DRS rules?"
            st.rerun()
        
        st.markdown("<div class='racing-stripe' style='margin: 2rem 0;'></div>",
                   unsafe_allow_html=True)
        
        # Clear chat button (clears both display and conversation memory)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.rerun()
        
        # Footer
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0; color: #666666; font-size: 0.8rem;'>
            <p>F1 Service System v1.0</p>
            <p style='margin-top: 0.5rem;'>Powered by OpenAI & AWS Bedrock</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Handle example queries from sidebar
    if 'example_query' in st.session_state:
        example = st.session_state.example_query
        del st.session_state.example_query
        
        # Add to messages and process
        st.session_state.messages.append({
            "role": "user",
            "content": example
        })
        st.rerun()


if __name__ == "__main__":
    main()
