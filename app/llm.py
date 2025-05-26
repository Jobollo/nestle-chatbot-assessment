import os
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def ask_openai_with_context(user_question, context_chunks):
    context_string = ''.join(
        f"- Title: {chunk['title']}\n  URL: {chunk['url']}\n  Content: {chunk['content']}\n\n"
        for chunk in context_chunks
    )

    system_prompt = (
        "You are an AI assistant for the Made with Nestlé Canada website. Answer user "
        "questions using only the information from the context below. Each context includes a "
        "title and a URL. When referencing a specific answer, always cite the corresponding URL "
        "from the context. If you cannot find the answer in the context, reply: 'The information "
        "you requested was not found in the current Made with Nestlé Canada website content.'\n\n"
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
