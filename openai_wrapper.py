import re
import openai
import settings

openai.api_key = settings.OPENAI_API_KEY


async def bob_ross_chat(prompt: str):
    content_filtered = re.search(r'<[@0-9]+> (.*)', prompt)
    if content_filtered:
        filtered_prompt = content_filtered.group(1).strip()
    else:
        filtered_prompt = prompt.strip()

    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "From now on, you are going to act like the famous painter Bob Ross. Thank you."},
        {"role": "user", "content": filtered_prompt},
        {"role": "system", "content": "Keep the response size to a short paragraph."},
    ])

    return completion.choices[0].message.content


async def bob_ross_paint(prompt: str):
    image_data = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    return image_data.data[0].url