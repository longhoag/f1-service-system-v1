"""
Streamlit application for F1 Service System.
Main UI for displaying circuit images and regulation responses.
"""

import streamlit as st
from loguru import logger


def main():
    """
    Main Streamlit application entry point.
    """
    st.set_page_config(
        page_title="F1 Service System",
        page_icon="🏎️",
        layout="wide"
    )
    
    st.title("🏎️ F1 Service System")
    st.markdown("Ask about F1 circuits or regulations!")
    
    # User input
    user_query = st.text_input(
        "Your question:",
        placeholder="e.g., 'Show me the Miami circuit' or 'What are the DRS rules?'"
    )
    
    if st.button("Submit") and user_query:
        logger.info("Processing user query: {}", user_query)
        
        with st.spinner("Processing your query..."):
            # TODO: Call orchestrator to process query
            pass
        
        # Display results section
        st.divider()
        
        # TODO: Display circuit images if applicable
        # st.image(image_path, caption="Circuit Map")
        
        # TODO: Display regulation responses if applicable
        # st.markdown(response_text)


if __name__ == "__main__":
    main()
