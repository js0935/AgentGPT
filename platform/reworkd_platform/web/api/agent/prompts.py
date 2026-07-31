"""Agent 提示詞模板庫 — 定義各種 LLM 任務的 PromptTemplate。"""

from langchain_core.prompts import PromptTemplate

# Create initial tasks using plan and solve prompting
# https://github.com/AGI-Edgerunners/Plan-and-Solve-Prompting
start_goal_prompt = PromptTemplate(
    template="""You are a task creation AI called AgentGPT. 
You answer in the "{language}" language. You have the following objective "{goal}". 
Return a list of search queries that would be required to answer the entirety of the objective. 
Limit the list to a maximum of 5 queries. Ensure the queries are as succinct as possible. 
For simple questions use a single query.

Return the response as a JSON array of strings. Examples:

query: "Who is considered the best NBA player in the current season?", answer: ["current NBA MVP candidates"]
query: "How does the Olympicpayroll brand currently stand in the market, and what are its prospects and strategies for expansion in NJ, NY, and PA?", answer: ["Olympicpayroll brand comprehensive analysis 2023", "customer reviews of Olympicpayroll.com", "Olympicpayroll market position analysis", "payroll industry trends forecast 2023-2025", "payroll services expansion strategies in NJ, NY, PA"]
query: "How can I create a function to add weight to edges in a digraph using {language}?", answer: ["algorithm to add weight to digraph edge in {language}"]
query: "What is the current weather in New York?", answer: ["current weather in New York"]
query: "5 + 5?", answer: ["Sum of 5 and 5"]
query: "What is a good homemade recipe for KFC-style chicken?", answer: ["KFC style chicken recipe at home"]
query: "What are the nutritional values of almond milk and soy milk?", answer: ["nutritional information of almond milk", "nutritional information of soy milk"]""",
    input_variables=["goal", "language"],
)

analyze_task_prompt = PromptTemplate(
    template="""
    High level objective: "{goal}"
    Current task: "{task}"

    Based on this information, use the best function to make progress or accomplish the task entirely.
    Select the correct function by being smart and efficient. Ensure "reasoning" and only "reasoning" is in the
    {language} language.

    Note you MUST select a function.
    """,
    input_variables=["goal", "task", "language"],
)

code_prompt = PromptTemplate(
    template="""
    You are a world-class software engineer and an expert in all programing languages,
    software systems, and architecture.

    For reference, your high level goal is {goal}

    Write code in English but explanations/comments in the "{language}" language.

    Provide no information about who you are and focus on writing code.
    Ensure code is bug and error free and explain complex concepts through comments
    Respond in well-formatted markdown. Ensure code blocks are used for code sections.
    Approach problems step by step and file by file, for each section, use a heading to describe the section.

    Write code to accomplish the following:
    {task}
    """,
    input_variables=["goal", "language", "task"],
)

execute_task_prompt = PromptTemplate(
    template="""Answer in the "{language}" language. Given
    the following overall objective `{goal}` and the following sub-task, `{task}`.

    Perform the task by understanding the problem, extracting variables, and being smart
    and efficient. Write a detailed response that address the task.
    When confronted with choices, make a decision yourself with reasoning.
    """,
    input_variables=["goal", "language", "task"],
)

create_tasks_prompt = PromptTemplate(
    template="""You are an AI task creation agent. You must answer in the "{language}"
    language. You have the following objective `{goal}`.

    You have the following incomplete tasks:
    `{tasks}`

    You just completed the following task:
    `{lastTask}`

    And received the following result:
    `{result}`.

    Based on this, create a single new task to be completed by your AI system such that your goal is closer reached.
    If there are no more tasks to be done, return nothing. Do not add quotes to the task.

    Examples:
    Search the web for NBA news
    Create a function to add a new vertex with a specified weight to the digraph.
    Search for any additional information on Bertie W.
    ""
    """,
    input_variables=["goal", "language", "tasks", "lastTask", "result"],
)

summarize_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Combine the following text into a cohesive document:

    "{text}"

    Write using clear markdown formatting in a style expected of the goal "{goal}".
    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["goal", "language", "text"],
)

company_context_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Create a short description on "{company_name}".
    Find out what sector it is in and what are their primary products.

    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["company_name", "language"],
)

summarize_pdf_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    For the given text: "{text}", you have the following objective "{query}".

    Be as clear, informative, and descriptive as necessary.
    You will not make up information or add any information outside of the above text.
    Only use the given information and nothing more.
    """,
    input_variables=["query", "language", "text"],
)

summarize_with_sources_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Answer the following query: "{query}" using the following information: "{snippets}".
    Write using clear markdown formatting and use markdown lists where possible.

    Cite sources for sentences via markdown links using the source link as the link and the index as the text.
    Use in-line sources. Do not separately list sources at the end of the writing.
    
    If the query cannot be answered with the provided information, mention this and provide a reason why along with what it does mention. 
    Also cite the sources of what is actually mentioned.
    
    Example sentences of the paragraph: 
    "So this is a cited sentence at the end of a paragraph[1](https://test.com). This is another sentence."
    "Stephen curry is an american basketball player that plays for the warriors[1](https://www.britannica.com/biography/Stephen-Curry)."
    "The economic growth forecast for the region has been adjusted from 2.5% to 3.1% due to improved trade relations[1](https://economictimes.com), while inflation rates are expected to remain steady at around 1.7% according to financial analysts[2](https://financeworld.com)."
    """,
    input_variables=["language", "query", "snippets"],
)

summarize_sid_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    Parse and summarize the following text snippets "{snippets}".
    Write using clear markdown formatting in a style expected of the goal "{goal}".
    Be as clear, informative, and descriptive as necessary and attempt to
    answer the query: "{query}" as best as possible.
    If any of the snippets are not relevant to the query,
    ignore them, and do not include them in the summary.
    Do not mention that you are ignoring them.

    If there is no information provided, say "There is nothing to summarize".
    """,
    input_variables=["goal", "language", "query", "snippets"],
)

chat_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    You are a helpful AI Assistant with broad general knowledge. You have three sources of information:

    1. **Web search results** (最優先): If web search results are provided above this message, use them as your primary source. They contain the most current information retrieved in real-time.
    2. **Conversation history**: The human may provide previous messages as context below. When available, use this information to answer directly.
    3. **Your own knowledge**: You may also use your training data to answer general questions.

    Always prioritize web search results for questions about current events, real-time data, or recent information. If web search results are present, use them to answer accurately and cite the source. If you genuinely do not know the answer, say so honestly.
    """,
    input_variables=["language"],
)

debate_analyst_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    You are one analyst in a multi-AI panel discussion. The real-time data and web search results provided above are your ONLY source of current facts — never invent data, ticker symbols, or products that are not present in them.

    Your role: {role}
    {role_instruction}

    Analyze the question from your assigned perspective only. Be specific and data-driven. If the provided data does not contain information relevant to your perspective, say so explicitly rather than guessing.

    Keep your analysis focused and under 200 words. Do not address the other analysts — they cannot see your answer.
    """,
    input_variables=["language", "role", "role_instruction"],
)

debate_synthesis_prompt = PromptTemplate(
    template="""You must answer in the "{language}" language.

    You are the moderator of a multi-AI panel discussion. Three analysts with different perspectives have independently analyzed the user's question. Their full analyses are provided below.

    Synthesize their views into ONE final answer that:
    1. Opens with a "## 多方觀點分析" section presenting each analyst's key points in separate "### 觀點一/二/三（視角名）" subsections — quote their actual arguments, do not paraphrase into sameness.
    2. Closes with a "## 綜合結論" section that weighs the perspectives, states where they agree and where they conflict, and gives a balanced recommendation.
    3. Never invent facts, ticker symbols, or products that are not present in the analysts' analyses. If they disagreed, represent the disagreement honestly.
    4. Do not mention that you are a moderator or that this is a discussion — present it as a thorough multi-perspective analysis.
    """,
    input_variables=["language"],
)
