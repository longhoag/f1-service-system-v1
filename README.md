# f1-service-system-v1
This is the planned pipeline:

1. User input query
2. Then, it would go to a LLM model openai, LLM agent
3. If the context of the query related to "showing the race circuit of miami" for exmaple, it would invoke tools to retrieve the webp image from the f1_2025_circuit_maps folder 
4. If the context is realted to regulations, it would invoke tools to send to Bedrock knowledge base + pinecone to do retrieval and generation 
5. All of the response will be shown to the UI
6. Use streamlit to build front end to show images of the circuits and response from the Bedrock knowledge base + pinecone 

Requirements for the project:
- use poetry for dependencies management 
- use loguru logger for logging instead of print to console
