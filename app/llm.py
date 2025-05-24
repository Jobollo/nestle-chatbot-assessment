import os
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def ask_openai_with_context(user_question, context_chunks):
    context_string = ''.join(f'- {chunk}\n' for chunk in context_chunks)

    system_prompt = (
        "You are an AI assistant for the Made with Nestlé Canada website (https://www.madewithnestle.ca/). "
        "Your task is to answer user questions using only the information provided in the context below, "
        "which comes from the official site. When possible, include specific recipe names or article titles "
        "and provide the relevant website URL as a reference in your answer. "
        "If the answer cannot be found in the context, try to clarify what the user is asking or looking for.\n\n"
        f"Context:\n{context_string}\n"
        "Be concise, accurate, and reference the original content where appropriate."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            temperature=0.3,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
