import streamlit as st
import requests
import json
from groq import Groq
import os

# load environment variables
from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Helper to extract content
def _extract_message_content(response):
    """Return the content string from a chat completion response.

    The Groq SDK (and similar clients) may return `response.choices` as a list
    of choice objects or as a single choice-like object. The choice itself may
    expose a `message` attribute (object) or be a dict with nested keys. This
    helper normalizes those shapes and returns the first choice's content.
    """
    choices = getattr(response, "choices", None)

    # normalize to the first choice object
    if isinstance(choices, (list, tuple)):
        choice = choices[0]
    else:
        choice = choices

    # case: SDK object with .message (which itself may have .content)
    if hasattr(choice, "message"):
        msg = getattr(choice, "message")
        if hasattr(msg, "content"):
            return msg.content
        if isinstance(msg, dict) and "content" in msg:
            return msg["content"]

    # case: plain dict-like choice
    if isinstance(choice, dict):
        msg = choice.get("message")
        if isinstance(msg, dict) and "content" in msg:
            return msg["content"]
        if "text" in choice:
            return choice["text"]
        if "content" in choice:
            return choice["content"]

    # try a couple of fallbacks against the response shape
    try:
        # response.choices[0].message.content when choices is indexable
        return response.choices[0].message.content
    except Exception:
        pass

    # last resort: stringify the whole response so the caller can at least
    # surface something for debugging
    return str(response)

def generate_syllabus(main_topic):
    syllabus_prompt = f"""
    You are a curriculum designer. Create a logical 10-step learning path for the topic: '{main_topic}'.
    Each step should be a specific sub-topic title.
    Output ONLY a JSON object with the key 'chapters' and a list of 10 strings.
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", # Updated to a common Groq model name
        messages=[{"role": "user", "content": syllabus_prompt}],
        response_format={"type": "json_object"}
    )
    data = json.loads(_extract_message_content(response))
    return data['chapters']

SYSTEM_PROMPT = """
You are an educator. Output a JSON object with a key 'items' containing 5 unique facts and 1 quiz.
JSON Format: 
{
  "items": [
    {"type": "fact", "text": "The fact..."},
    {"type": "quiz", "question": "...", "options": ["A", "B", "C", "D"], "correct_index": 0}
  ]
}
"""

def build_course_json(topic, chapters):
    # This list will hold all our data instead of a database
    full_curriculum = []

    for chapter in chapters:
        print(f"Generating content for: {chapter}...")
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {topic}. Chapter: {chapter}"}
            ],
            response_format={"type": "json_object"}
        )
        
        rawdata = json.loads(_extract_message_content(response))
        
        # Extract items and add metadata to each
        items = rawdata.get('items', [])
        for item in items:
            item['chapter'] = chapter  # Tag which chapter this belongs to
            full_curriculum.append(item)

    # Define the filename
    filename = topic.replace(" ", "_").lower() + "_curriculum.json"
    
    # Write the entire list to a JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(full_curriculum, f, indent=4)
    
    print(f"Success! Saved to {filename}")
    return full_curriculum

def main():
    topic = "Health and Exercise"
    chapters = generate_syllabus(topic)
    curriculum_data = build_course_json(topic, chapters)
    # Now curriculum_data is a standard Python list you can use immediately

if __name__ == "__main__":
    main()