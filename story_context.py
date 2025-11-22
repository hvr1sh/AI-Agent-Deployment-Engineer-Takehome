import json

class StoryContext():
    def __init__(self):
        self.context = {
            # "title": "",
            # "prompt": "",
            # "num_sections": 0,
            # "sections": [],
            # "images": []
        }
        
    def update_story_context(self, dump=False, path = 'story_context.json', **kwargs):
        for key, value in kwargs.items():
            self.context[key] = value
        
        if dump:
            with open(path, "w") as f:
                json.dump(self.context, f, indent=4)

    def reset_story_context(self):
        self.story_context = {}
