from crewai.tools import tool
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

@tool
def summarizer_tool(markdown_text):
    """Summarizes markdown text into 3 concise bullet points."""

    system_prompt = """"You are an expert content editor. Summarize the provided news article concisely for automated delivery to Slack and Google Sheets.

                Rules:

                Extract the primary story and key facts into 3 concise bullet points (under 120 words total).

                Ignore web scraping artifacts, headers, footers, navigation links, or Jina Reader tags.

                Output ONLY the summary bullets. Do NOT include any introductory or concluding remarks."""


    message = [{
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": markdown_text
    }
    ]

    response = client.chat.completions.create(
        messages= message,
        model="llama-3.3-70b-versatile"
    )

    # print(response.choices[0].message.content)  #test
    return response.choices[0].message.content