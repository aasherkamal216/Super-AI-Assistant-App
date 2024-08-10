from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_community.document_loaders import YoutubeLoader, WebBaseLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
import streamlit as st

def groq_chatbot(model_params, question, api_key, chat_history):
    llm = ChatGroq(model=model_params['model'], api_key=api_key,
                temperature=model_params["temperature"],
                max_tokens=model_params['max_tokens']
                )
    
    system_template = (
    """Given a chat history and the latest user question 
    which might reference context in the chat history, 
    Answer the user question in a polite and professional manner."""
)   
    prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "Questioin: {question}")
    ]
)
    chain = prompt | llm | StrOutputParser()

    return chain.stream({"question": question, "chat_history": chat_history})


def get_prompt():
    prompt = ChatPromptTemplate.from_template("""
Answer the following user questions as best you can. Use the available tools to find the answer.
You have access to the following tools:\n
{tools}\n\n
To use a tool, please use the following format:
```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```
If one tool doesn't give the relavant information, use another tool.
When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
                                              
```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```
Begin!
                                              
Previous conversation history:
{chat_history}
New input: {input}

{agent_scratchpad}
""")
    return prompt


def create_groq_agent(model_params, api_key, tools, question, chat_history):

    llm = ChatGroq(model=model_params['model'], api_key=api_key,
                    temperature=model_params["temperature"],
                    )
    prompt = get_prompt()

    agent = create_react_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=7)
    st_callback = StreamlitCallbackHandler(st.container())

    response = agent_executor.invoke({"input":question, "chat_history":chat_history}, {"callbacks": [st_callback]})
    return response['output']


def get_tools(selected_tools):
    # Define all available tools
    tools = {
        "Wikipedia": Tool(
            name="Wikipedia",
            func=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500).run,
            description="A useful tool for searching the Internet to find information on world events, issues, dates, years, etc."
        ),
        "ArXiv": Tool(
            name="ArXiv",
            func=ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500).run,
            description="A useful tool for searching scientific and research papers."
        ),
        "DuckDuckGo Search": Tool(
            name="DuckDuckGo Search",
            func=DuckDuckGoSearchRun().run,
            description="Useful for when you need to search the internet to find latest information, facts and figures that another tool can't find."
        )
    }

    # Filter and return only the tools selected by the user
    return [tools[tool_name] for tool_name in selected_tools]


def summarizer_model(model_params, api_key, url):
    llm = ChatGroq(model=model_params['model'], api_key=api_key,
            temperature=model_params["temperature"],
            max_tokens=model_params['max_tokens']
            )
    
    if "youtube.com" in url:
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
    else:
        loader = WebBaseLoader(web_path=url)

    data = loader.load()

    prompt_template = """Provide a summary of the following content in proper markdown:
    Content:\n{text}"""

    prompt = PromptTemplate(input_variables=["text"], template=prompt_template)

    chain = load_summarize_chain(llm=llm, chain_type="stuff", prompt=prompt)
    output = chain.run(data)
    return output