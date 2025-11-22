import json
from openai import OpenAI
import os

class Judge():
    def __init__(self):
            API_KEY = os.getenv("OPENAI_API_KEY")
            self.model = "gpt-3.5-turbo"
            self.client = OpenAI(api_key=API_KEY)
        
    def is_story_prompt(self, prompt: str) -> bool:
            '''
            Determine whether a user-provided prompt is requesting a fictional story.
            Input:
                prompt: str
                    Prompt provided by user
            
            Output:
                bool: True if the prompt is asking for a story
            '''
            merged_prompt = f"""
                Respond ONLY with '1' or '0'.

                '1' = the user is asking for a fictional or narrative story.
                '0' = anything else.

                User input:
                {prompt}
            """
            merged_prompt = merged_prompt.strip()

            resp = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": merged_prompt
                    }
                ]
            )

                # Extract text (adjust to your SDK shape)
            output = resp.output[0].content[0].text.strip()
            return output == "1"
    
    def judge_outline(self, outline: list, original_prompt: str) -> json:
            
        system_msg = ("""
            You are an expert story editor and quality assurance specialist for a children's book publisher (target audience 5-10 years old). Your task is to evaluate a series of proposed story sections. You must judge the outline on the following criteria:
            *   Age Appropriateness: Suitability of vocabulary, complexity, and emotional content for 5-10 year olds.
            *   Engagement & Pacing: Ability to hold attention, flow, and rhythm.
            *   Clarity & Cohesion: Ease of understanding the narrative and plot.
            *   Educational/Moral Value: Presence and clarity of a simple, positive lesson or educational concept
        """
        
            "You must ONLY output valid JSON — no commentary, explanation, or markdown. "
            "Each section must contain: scores and feedback. "
            "The 'feedback' field should contain general thoughts on the outline "
                
        )
        user_msg = f"""
            Here is the original prompt that generated the story sections. All sections must align with this prompt:
            ---
            {original_prompt}
            ---

           
            
            Here is the list of story sections, each with a title, summary, and a 'section prompt' that was used to generate it:
            ---
            {outline}
            ---
            
            Output format (STRICT JSON):
            
            {{
                "scores": {{
                    age_appropriateness: (int 0 - 5),
                    engagement: (int 0 - 5),
                    clarity: (int 0 - 5),
                    education: (int 0 - 5)     
                }}
                "feedback": "Overall Feedback"
            }}
        """
        
        resp = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        
        text = resp.output[0].content[0].text.strip()
        
        # Parse the JSON output from the model
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse outline JSON: {e}\n\nModel output:\n{text}")
        
        return data
    
    def judge_story(self, story: list, original_prompt: str) -> json:
            
        system_msg = ("""
            You are an expert story editor and quality assurance specialist for a children's book publisher (target audience 5-10 years old). Your task is to evaluate a series of proposed story sections. You must judge the outline on the following criteria:
            *   Age Appropriateness: Suitability of vocabulary, complexity, and emotional content for 5-10 year olds.
            *   Engagement & Pacing: Ability to hold attention, flow, and rhythm.
            *   Clarity & Cohesion: Ease of understanding the narrative and plot.
            *   Prompt Adeherance: How well the output matches the prompt
        """
        
            "You must ONLY output valid JSON — no commentary, explanation, or markdown. "
            "Each section must contain: scores and feedback. "
            "The 'feedback' field should contain general thoughts on the outline "
                
        )
        user_msg = f"""
            Here is the original prompt that generated the story. All sections of the story must align with this prompt:
            ---
            {original_prompt}
            ---

           
            
            Here is the list of story sections:
            ---
            {story}
            ---
            
            Output format (STRICT JSON):
            
            {{
                "scores": {{
                    age_approriatness: (int 0 - 5),
                    engagement: (int 0 - 5),
                    clarity: (int 0 - 5),
                    adherence: (int 0 - 5)     
                }}
                "feedback": "Overall Feedback"
            }}
        """
        
        resp = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        
        text = resp.output[0].content[0].text.strip()
        
        # Parse the JSON output from the model
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse outline JSON: {e}\n\nModel output:\n{text}")
        
        return data
    