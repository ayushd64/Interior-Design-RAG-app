# src/eval_prompts.py
from langchain_core.prompts import ChatPromptTemplate

# ─────────────────────────────────────────────────
# FAITHFULNESS
# "Is the answer grounded in the retrieved context?"
# ─────────────────────────────────────────────────
FAITHFULNESS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are evaluating if an ANSWER is 
    faithful to the provided CONTEXT.

    Faithfulness means: every claim in the answer 
    can be supported by the context.

    Scoring (reply with ONLY a number 0-100):
    - 100 = Every claim fully supported by context
    - 70  = Mostly supported, minor unsupported details
    - 40  = Some claims supported, some made up
    - 0   = Answer ignores context / fully hallucinated

    Reply with ONLY a number between 0 and 100.
    No explanation. Just the number.
    """),
    ("human", """CONTEXT:
{context}

ANSWER:
{answer}

Faithfulness score (0-100):""")
])

# ─────────────────────────────────────────────────
# ANSWER RELEVANCY
# "Does the answer address the question?"
# ─────────────────────────────────────────────────
RELEVANCY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are evaluating if an ANSWER 
    actually addresses the QUESTION asked.

    Relevancy means: the answer is on-topic and 
    directly responds to what was asked.

    Scoring (reply with ONLY a number 0-100):
    - 100 = Directly and completely answers the question
    - 70  = Answers but with some irrelevant content
    - 40  = Partially addresses the question
    - 0   = Off-topic / doesn't answer the question

    Reply with ONLY a number between 0 and 100.
    No explanation. Just the number.
    """),
    ("human", """QUESTION:
{question}

ANSWER:
{answer}

Relevancy score (0-100):""")
])

# ─────────────────────────────────────────────────
# CONTEXT PRECISION
# "Were the retrieved documents relevant?"
# ─────────────────────────────────────────────────
PRECISION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are evaluating if the RETRIEVED 
    CONTEXT was relevant to answering the QUESTION.

    Context precision means: the retrieved documents 
    actually contain information useful for the question.

    Scoring (reply with ONLY a number 0-100):
    - 100 = All context highly relevant to question
    - 70  = Most context relevant, some noise
    - 40  = Mixed - some relevant, some irrelevant
    - 0   = Context not relevant to question at all

    Reply with ONLY a number between 0 and 100.
    No explanation. Just the number.
    """),
    ("human", """QUESTION:
{question}

RETRIEVED CONTEXT:
{context}

Context precision score (0-100):""")
])

