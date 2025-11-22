from openai import OpenAI
import os
import json
import base64

class Model():
    def __init__(self, img_model="dall-e-2"):
        API_KEY = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo"
        self.img_model = img_model  # Options: "dall-e-2" (faster) or "dall-e-3" (higher quality)
        self.client = OpenAI(api_key=API_KEY)
        
    def call_text_model(self, prompt: str, max_tokens=3000, temperature=0.1) -> str:
        resp = self.client.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message["content"]  # type: ignore

    example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."
    
    



    def generate_story_outline(self, base_prompt: str, num_sections: int, feedback: json = {}, last_version: list = []):
        """
        Generate a structured outline for a story with `num_sections` sections.
        The LLM is instructed to return STRICT JSON only.

        The returned value is a list where each item represents one section and
        contains a section-specific prompt ready to be used when generating that
        section's story text.

        Output list example:
        [
            {
                "section_id": 1,
                "title": "The Mysterious Letter",
                "summary": "A strange letter arrives...",
                "prompt": "<prompt for section>"
            },
            ...
        ]
        """
        system_msg = (
                "You are an outline generator. "
                "Your job is to break a story into clear, structured sections. "
                "You must ONLY output valid JSON — no commentary, explanation, or markdown. "
                "Each section must contain: section_id, title, summary, and prompt. "
                "The 'prompt' field must be a natural-language instruction that will be given "
                "to a story-writing model later to generate that section's prose."
                "The prompts that you write will be be used to prompt another agent to write the actual story"
            )
        if not feedback:
            user_msg = f"""
                Create an outline for a story based on this premise:

                \"\"\"{base_prompt}\"\"\"

                The story must be divided into exactly {num_sections} sections.

                Output format (STRICT JSON):

                {{
                "sections": [
                    {{
                    "section_id": 1,
                    "title": "Short title",
                    "summary": "2–3 sentence summary of events in this section.",
                    "prompt": "A clear instruction that will be given to a story-writing model."
                    }},
                    {{
                    "section_id": 2,
                    "title": "Short title",
                    "summary": "2–3 sentence summary.",
                    "prompt": "Instruction for the second section."
                    }},
                    ...
                ]
                }}
            """

        else:
            user_msg = f"""
                Create an outline for a story based on this premise:

                \"\"\"{base_prompt}\"\"\"

                The story must be divided into exactly {num_sections} sections.

                Output format (STRICT JSON):

                {{
                "sections": [
                    {{
                    "section_id": 1,
                    "title": "Short title",
                    "summary": "2–3 sentence summary of events in this section.",
                    "prompt": "A clear instruction that will be given to a story-writing model."
                    }},
                    {{
                    "section_id": 2,
                    "title": "Short title",
                    "summary": "2–3 sentence summary.",
                    "prompt": "Instruction for the second section."
                    }},
                    ...
                ]
                
                    This is your previouse story that was written: 
                    \"\"\"{last_version}\"\"\"
                    
                    
                    Here is some feedback for what needs to be fixed:
                    \"\"\"{feedback}\"\"\"
                    
                }}
            """
            
            
        resp = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )

        # Extract response text (adjust if your SDK uses a different accessor)
        text = resp.output[0].content[0].text.strip()

        # Parse the JSON output from the model
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse outline JSON: {e}\n\nModel output:\n{text}")

        # Return the list of sections
        return data["sections"]
    
    def generate_story_section(self, section_prompt: str, previous_sections: list[str] = None, feedback: json = {}, last_version: str = None) -> str:
        
        if not feedback:
            if not previous_sections:
                merged_prompt = f"""
                    Write the beginning of a children's story for ages 5–10.
                    Keep it SHORT: 2–5 sentences.
                    Use simple, friendly language.

                    Start the story based on this instruction:
                    \"\"\"{section_prompt}\"\"\"

                    Only output the story text. No titles or commentary.
                """.strip()

            # With previous sections → continue story
            else:
                prev_text = "\n".join(previous_sections)

                merged_prompt = f"""
                    Write the next part of a children's story for ages 5–10.
                    Keep it SHORT: 2–5 sentences.
                    Use simple, friendly language.
                    Make the story flow naturally and smoothly from what happened earlier.

                    Earlier parts (do NOT repeat them):
                    \"\"\"{prev_text}\"\"\"

                    Continue the story based on this instruction:
                    \"\"\"{section_prompt}\"\"\"

                    Only output the story text. No titles or commentary.
                """.strip()
        else:
            if not previous_sections:
                merged_prompt = f"""
                    Write the beginning of a children's story for ages 5–10.
                    Keep it SHORT: 2–5 sentences.
                    Use simple, friendly language.
                    
                    This was your last attempt at it:
                    \"\"\"{last_version}\"\"\"
                    
                    Incorperate this feedback:
                    \"\"\"{feedback}\"\"\"

                    Start the story based on this instruction:
                    \"\"\"{section_prompt}\"\"\"

                    Only output the story text. No titles or commentary.
                """.strip()

            # With previous sections → continue story
            else:
                prev_text = "\n".join(previous_sections)

                merged_prompt = f"""
                    Write the next part of a children's story for ages 5–10.
                    Keep it SHORT: 2–5 sentences.
                    Use simple, friendly language.
                    Make the story flow naturally and smoothly from what happened earlier.

                    Earlier parts (do NOT repeat them):
                    \"\"\"{prev_text}\"\"\"
                    
                    This was your last attempt at it:
                    \"\"\"{last_version}\"\"\"
                    
                    Incorperate this feedback:
                    \"\"\"{feedback}\"\"\"

                    Continue the story based on this instruction:
                    \"\"\"{section_prompt}\"\"\"       

                    Only output the story text. No titles or commentary.
                """.strip()
            

        resp = self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": merged_prompt}]
        )

        story_text = resp.output[0].content[0].text.strip()
        return story_text
    
    def generate_image_from_text(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> str:
        """
        Generate an image from a text prompt using OpenAI image models.

        Args:
            prompt: Text description for the image
            size: Image size - "256x256", "512x512", or "1024x1024" (dall-e-2)
                  "1024x1024", "1024x1792", or "1792x1024" (dall-e-3)
            quality: "standard" (faster) or "hd" (higher quality, dall-e-3 only)

        Returns:
            Base64 encoded image string
        """
        # Create a child-friendly image prompt
        enhanced_prompt = f"A colorful, friendly, child-appropriate illustration of: {prompt}. Cartoon style, bright colors, safe for children ages 5-10. Do not include an text in the image. Only show Pictures."

        params = {
            "model": self.img_model,
            "prompt": enhanced_prompt,
            "size": size,
            "response_format": "b64_json",
            "n": 1
        }

        # Only add quality parameter for dall-e-3
        if self.img_model == "dall-e-3":
            params["quality"] = quality

        response = self.client.images.generate(**params)

        image_b64 = response.data[0].b64_json
        return image_b64

    def edit_story_section(self, original_section: str, edit_instruction: str, previous_sections: list[str] = None) -> str:
        """
        Edit an existing story section based on user instructions.

        Input:
            original_section: str
                The original text of the story section to be edited
            edit_instruction: str
                User's instruction for how to modify the section
            previous_sections: list[str] (optional)
                Previous sections of the story for context

        Output:
            str: The edited story section
        """

        context_text = ""
        if previous_sections:
            context_text = f"""
                Earlier parts of the story (for context):
                \"\"\"{chr(10).join(previous_sections)}\"\"\"
            """

        merged_prompt = f"""
            You are editing a children's story for ages 5–10.
            Keep it SHORT: 2–5 sentences.
            Use simple, friendly language.

            {context_text}

            Original section:
            \"\"\"{original_section}\"\"\"

            User's edit request:
            \"\"\"{edit_instruction}\"\"\"

            Apply the requested changes while maintaining the story's tone and flow.
            Only output the revised story text. No titles or commentary.
        """.strip()

        resp = self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": merged_prompt}]
        )

        edited_text = resp.output[0].content[0].text.strip()
        return edited_text

