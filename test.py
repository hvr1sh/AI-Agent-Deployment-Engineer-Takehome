import os
import openai
from story_context import StoryContext
from model import Model
from dotenv import load_dotenv
import json
import base64
from judge import *
"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""


def save_base64_image(b64_str, filename="image.png"):
    # Decode the base64 string into bytes
    image_bytes = base64.b64decode(b64_str)

    # Write the bytes to an image file
    with open(filename, "wb") as f:
        f.write(image_bytes)

    return filename

def main():
    load_dotenv()
    prompt = input("What kind of story do you want to hear?: ")
    num_sections = input("How many sections?: ")
    
    context = StoryContext()
    context.reset_story_context()
    context.update_story_context(
        prompt=prompt, 
        num_sections=int(num_sections)
    )
    
    model = Model()
    judge = Judge()
    if judge.is_story_prompt(prompt):
        section_prompts = model.generate_story_outline(prompt, num_sections)
        context.update_story_context(
            section_prompts=section_prompts
        )
        
        feedback = judge.judge_outline(outline=section_prompts, original_prompt=prompt)
        context.update_story_context(feedback=feedback)
        sections = []
        for prompt in section_prompts:
            section = model.generate_story_section(prompt, sections)
            sections.append(section)
            
        context.update_story_context(dump=True, sections=sections)
        
        
        
        
        
        # for i, section in enumerate(sections):
        #     img = model.generate_image_from_text(section)
        #     save_base64_image(img, f"{i}.png")


if __name__ == "__main__":
    main()
    
    