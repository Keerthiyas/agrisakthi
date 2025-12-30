import openai
import os

# Set your OpenAI API key (you can also set it in .env)
openai.api_key = os.getenv("OPENAI_API_KEY")


def recommend_crop(weed_name, weather=None, season=None, extra_instructions=None):
    """Use OpenAI to recommend crops and features given a detected weed.

    - `weed_name`: string name of detected weed
    - `weather`: optional dict with keys like temp, humidity, wind, rain
    - `season`: optional string like 'Winter', 'Monsoon', etc.
    - `extra_instructions`: optional additional context to include

    Returns the assistant text (string).
    """
    instructions = [f"You are an expert agronomist." ]
    user_prompt = f"Given the presence of '{weed_name}' weed, suggest the best crops that can be grown in this field and explain briefly why."
    if season:
        user_prompt += f" The current season is {season}."
    if weather:
        # format weather dict into a short summary
        wparts = []
        if 'temp' in weather:
            wparts.append(f"temperature {weather['temp']}°C")
        if 'humidity' in weather:
            wparts.append(f"humidity {weather['humidity']}%")
        if 'wind' in weather:
            wparts.append(f"wind {weather['wind']} m/s")
        if 'rain' in weather:
            wparts.append(f"rain {weather['rain']} mm")
        if wparts:
            user_prompt += " Current weather: " + ", ".join(wparts) + "."
    if extra_instructions:
        user_prompt += " " + extra_instructions

    # Build messages for chat completion
    messages = [
        {"role": "system", "content": "You are an expert agronomist who provides concise, practical crop recommendations and explains seasonal/weather considerations."},
        {"role": "user", "content": user_prompt}
    ]

    # Use ChatCompletion; fall back to a simpler completion if needed
    try:
        resp = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4'),
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        text = resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        # fall back to completion (older API) or return error message
        try:
            resp = openai.Completion.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4'),
                prompt=user_prompt,
                max_tokens=300,
                temperature=0.7,
            )
            text = resp['choices'][0]['text'].strip()
        except Exception as e2:
            text = f"OpenAI request failed: {e} / {e2}"

    return text
