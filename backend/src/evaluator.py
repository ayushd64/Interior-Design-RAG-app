# src/evaluator.py
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from src.eval_prompts import (
    FAITHFULNESS_PROMPT,
    RELEVANCY_PROMPT,
    PRECISION_PROMPT
)
from dotenv import load_dotenv
import os
import re

load_dotenv()

# ── Judge LLM (lower temp for consistent scoring) ─
_judge_llm = None

def _get_judge():
    """Lazy load the judge LLM"""
    global _judge_llm
    if _judge_llm is None:
        _judge_llm = ChatOllama(
            base_url    = os.getenv(
                "OLLAMA_BASE_URL",
                "http://127.0.0.1:11434"
            ),
            model       = os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            temperature = 0.0   # Deterministic scoring!
        )
    return _judge_llm

parser = StrOutputParser()

# ─────────────────────────────────────────────────
# Parse Score From LLM Response
# ─────────────────────────────────────────────────
def _parse_score(response: str) -> float:
    """
    Extract a 0-1 score from LLM response
    LLM returns 0-100, we convert to 0-1
    """
    # Find first number in response
    match = re.search(r'\d+', response)
    if not match:
        return 0.0
    
    score = int(match.group())
    # Clamp to 0-100 then convert to 0-1
    score = max(0, min(100, score))
    return round(score / 100, 2)

# ─────────────────────────────────────────────────
# Evaluate Single Q&A
# ─────────────────────────────────────────────────
def evaluate_single(
    question: str,
    answer  : str,
    contexts: list
) -> dict:
    """
    Run all 3 evaluations on one Q&A pair
    Returns dict with scores 0-1
    """
    judge = _get_judge()
    
    # Join contexts into one string
    context_text = "\n\n".join(contexts) if contexts else ""
    
    # If no context (e.g., off-topic), skip context-based metrics
    if not context_text:
        return {
            "faithfulness"     : None,
            "answer_relevancy" : None,
            "context_precision": None
        }
    
    # ── Faithfulness ──────────────────────────────
    faith_chain = FAITHFULNESS_PROMPT | judge | parser
    faith_resp  = faith_chain.invoke({
        "context": context_text,
        "answer" : answer
    })
    faithfulness = _parse_score(faith_resp)
    
    # ── Answer Relevancy ──────────────────────────
    rel_chain = RELEVANCY_PROMPT | judge | parser
    rel_resp  = rel_chain.invoke({
        "question": question,
        "answer"  : answer
    })
    relevancy = _parse_score(rel_resp)
    
    # ── Context Precision ─────────────────────────
    prec_chain = PRECISION_PROMPT | judge | parser
    prec_resp  = prec_chain.invoke({
        "question": question,
        "context" : context_text
    })
    precision = _parse_score(prec_resp)
    
    return {
        "faithfulness"     : faithfulness,
        "answer_relevancy" : relevancy,
        "context_precision": precision
    }

