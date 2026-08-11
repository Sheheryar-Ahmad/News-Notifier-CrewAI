from tools.search_tool import search_tool, reset_search_state
from tools.scrape_tool import scrape_first_article, reset_scrape_state
from tools.summarizer_tool import summarizer_tool
from tools.sheets_tool import sheets_tool
from tools.slack_tool import send_to_slack
from crewai import Agent, Task, Crew, LLM, Process
import os
import litellm

# Groq rejects cache_breakpoint in message dicts (CrewAI LiteLLM path bug)
_original_completion = litellm.completion


def _patched_completion(*args, **kwargs):
    messages = kwargs.get("messages")
    if messages:
        kwargs["messages"] = [
            {k: v for k, v in msg.items() if k != "cache_breakpoint"}
            if isinstance(msg, dict)
            else msg
            for msg in messages
        ]
    return _original_completion(*args, **kwargs)


litellm.completion = _patched_completion

# gemini_llm = LLM(
#     api_key=os.getenv("GEMINI_API_KEY"),
#     model="gemini-2.5-flash-lite",
#     temperature=0.3,
# )

hf_llm = LLM(
    api_key=os.getenv("HUGGINGFACE_API_KEY"),
    model="huggingface/Qwen/Qwen2.5-7B-Instruct",
    temperature=0.3
)

gemini_llm = LLM(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini/gemini-3.1-flash-lite",
    temperature=0.3,
)

groq_llm = LLM(
    api_key=os.getenv("GROQ_API_KEY"),
    model="groq/llama-3.1-8b-instant",
    temperature=0.2,
)

researcher = Agent(
    role="Web Research Specialist",
    goal="Find the single best and most recent news article URL about {topic}.",
    backstory="You search once, return URLs, and stop.",
    tools=[search_tool],
    max_iter=2,
    max_retry_limit=1,
    allow_delegation=False,
    llm=groq_llm,
)

scraper = Agent(
    role="Data Extraction Specialist",
    goal="Extract article text from the search results using one tool call.",
    backstory=(
        "You call scrape_first_article exactly once with the URLs from the "
        "previous task, then immediately return that output as your final answer."
    ),
    tools=[scrape_first_article],
    max_iter=2,
    max_retry_limit=1,
    allow_delegation=False,
    llm=groq_llm,
)

editor = Agent(
    role="Senior Content Editor",
    goal=(
        "Summarize the scraped article into 3 bullet points for Slack and "
        "Google Sheets."
    ),
    backstory=(
        "You receive raw article text from the scraper. You need to summarize the article into 3 bullet points and under 120 words"
    ),
    # tools=[summarizer_tool],
    max_iter=2,
    max_retry_limit=1,
    allow_delegation=False,
    llm=gemini_llm,
)

distributor = Agent(
    role = "Google Sheets Specialist",
    goal = "Send the date, summarized text and URL of the article into google sheets.",
    backstory = "You recieve the summary and URL of an article.You will use sheets_tool and generate the current date using that tool." \
    "Then you will use the sheets_tool to save the date, summary and URL into google sheets",
    tools=[sheets_tool],
    max_iter=2,
    max_retry_limit=1,
    allow_delegaion=False,
    llm=hf_llm
)

slack = Agent(
    role="Slack Expert",
    goal="Send the summarized text and URL of the article to the Slack channel",
    backstory="You recieve the summary and URL of an article from a previous task." \
    "Your job is to to use the send_to_slack tool and send the summary and URL of the article to the slack channel",
    tools=[send_to_slack],
    max_iter=2,
    max_retry_limit=1,
    allow_delegaion=False,
    llm=gemini_llm
)

search_task = Task(
    description=(
        "Search the web for trending news on: {topic}. "
        "Use search_tool exactly once, then stop. You return the 3 URLs you found in your search and hand them to the next agent."
    ),
    expected_output="A list of up to 3 article URLs with titles.",
    agent=researcher,
)

scrape_task = Task(
    description=(
        "Using the search results from the previous task, call "
        "scrape_first_article exactly once. Pass the full search output "
        "as the argument. Return the scraped "
        "article text as your final answer. "
        "Also give the URL of the article in your answer"
    ),
    expected_output="Markdown text of the article.",
    agent=scraper,
    context=[search_task],
)

edit_task = Task(
    description=(
        "Using the scraped article text from the previous task, summarize the text into 3 bullet points"
    ),
    expected_output=(
        "Exactly 3 concise bullet points (under 120 words total) with no "
        "introductory or concluding text."
        "Also give the URL of the article in your answer"
    ),
    agent=editor,
    context=[scrape_task],
)

sheets_task = Task(
    description=("You recieve summary and URL of an article from the previous task," 
    "Use the sheets_tool to log the Date, Summary and URL into a google sheet."
    ),
    expected_output=("The Current Date, Summary and URL of the article are successfully" \
    "saved in the google sheet"),
    agent=distributor,
    context=[edit_task]
)

slack_task = Task(
    description=(
        "You recieve the Summary and the URL of an article from a previous task." \
        "You have to use the send_to_slack tool to send the Summary and the URL of the article to the Slack channel."
    ),
    expected_output=(
        "The Summary and URL of the article are sent to the Slack channel."
    ),
    agent=slack,
    context=[edit_task]
)

news_crew = Crew(
    agents=[researcher, scraper, editor, distributor, slack],
    tasks=[search_task, scrape_task, edit_task, sheets_task, slack_task],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    reset_search_state()
    reset_scrape_state()

    result = news_crew.kickoff(inputs={"topic": "Snakes"})

    # print("### FINAL RESULT ###")
    # print(result)
