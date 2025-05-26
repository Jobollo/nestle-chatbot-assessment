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
        f""" You are an AI assistant for the Made with Nestlé Canada website. Use the information provided in the 
        context below to answer user questions as helpfully as possible. The context contains several items, each with 
        a title and a URL. Synthesize and infer answers using any relevant information in the context, even if the 
        answer is not stated exactly as the question. Always reference the specific URL from the context that supports 
        your answer. 
        
        If you cannot find any relevant information in the context, reply: "The information you requested was not found 
        in the current Made with Nestlé Canada website content."
        
        If the context only partially addresses the question, answer as best as you can and note that the information 
        may not be complete.
        
        Context:
        {context_string}
        
        Be concise, accurate, and always cite the original content (including its URL) when possible.
        
        """
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
