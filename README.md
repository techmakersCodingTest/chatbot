# Instructions
This package is in charge of chatbot, what it does is create a backend with langchain, in this backed there is information about the amazon bedrock which you will have to set up permissions before (you are not able to do it through CDK), once done you have to create a knowledge base and connect it directly to the s3 created in the CDK repository.
This code uses the backend to create the connection between the LLM and the memory (in order for it to have a state), it also incorporates the connection between the LLM and the knowledgeBase. Finally it uses streamlit to run a front end that displays the front end of the chatbot.
You'll have to download python and all langchain and streamlit related dependencies in order to run it.
To run it just run
```sh
streamlit run chatbot_frontend.py
```
