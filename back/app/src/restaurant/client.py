import openai

from app.config import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY


async def get_item_description(item: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Can you describe {item} item? Limit your answer for 256 symbols",
                }
            ],
            temperature=1,
            max_tokens=64,
            top_p=0.8,
            frequency_penalty=0,
            presence_penalty=0,
        )
    except Exception:
        return "Currently unavailable"
    return response["choices"][0]["message"]["content"]  # type: ignore
