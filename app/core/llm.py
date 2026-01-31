from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="arcee-ai/trinity-large-preview:free",
    temperature=0.3,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key="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"
)
