from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import uvicorn
from persistence.database import Database
from typing import Optional
from sqlalchemy import text
from fastapi import HTTPException
from dotenv import load_dotenv  # type: ignore
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Twinknowledge Interview API", version="1.0.0")

# Allow browser clients during local dev; tighten as needed in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def validate_answer(question: str, answer: str, user_answer: str, api_key: str) -> bool:
    client = OpenAI(api_key=api_key)

    prompt = f"""
    You are a strict validator for a quiz game.
    The question is: {question}
    The correct answer is: "{answer}".
    The user answered: "{user_answer}".

    Decide if the user's answer is essentially correct.
    Respond strictly in JSON: {{"is_correct": true}} or {{"is_correct": false}}.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},  # force JSON mode
        max_tokens=10,
    )

    content = response.choices[0].message.content
    data = json.loads(content)
    return data["is_correct"]

@app.get("/ping")
def ping():
    """Health-check style endpoint.

    Returns a simple JSON payload to confirm the server is responsive.
    """
    return {"message": "pong"}

@app.get("/question/")
def get_random_question(round: Optional[str] = None, value: Optional[str] = None):
    """
    Returns a random question filtered by optional round and value, sourced from Postgres.
    """
    db = Database.get_for(os.getenv("DB_NAME"))
    value_int = int(value)

    sql = """
    SELECT id AS question_id, "Round" AS round, "Category" AS category, "Value" AS value, "Question" AS question
    FROM public.questions
    WHERE "Round" = :round AND "Value" = :value
    ORDER BY random()
    LIMIT 1
    """
    result = db.execute(sql, {"round": round, "value": value_int})

    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="No questions match the given filters.")

    return dict(row._mapping)

class VerifyAnswerRequest(BaseModel):
    question_id: int
    user_answer: str

@app.post("/verify-answer/")
def verify_answer(payload: VerifyAnswerRequest):
    db = Database.get_for(os.getenv("DB_NAME"))

    row = db.execute("""
        SELECT * FROM public.questions
        WHERE "id" = :id
        LIMIT 1
    """, {"id": payload.question_id}).fetchone()
    row = dict(row._mapping)

    question = row["Question"]
    answer = row["Answer"]

    print(f"""
        Question: {question}
        answer: {answer}
        User answer: {payload.user_answer}
    """)

    return {"is_correct":  validate_answer(question, answer, payload.user_answer,os.getenv("OPENAI_KEY"))}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )


