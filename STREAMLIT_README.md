# Kids Story Generator - Streamlit App

A beautiful web interface for generating illustrated children's stories with AI.

## Features

- **Interactive Story Generation**: Create custom stories for kids ages 5-10
- **Story Editing**: Edit any section of the story after generation with natural language instructions
- **Image Generation**: Each story section comes with an AI-generated illustration
- **Real-time Preview**: See your story sections and images as they're generated
- **Download**: Save your completed story as a text file

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the App

Launch the Streamlit app with:
```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## How to Use

### Creating a Story

1. **Enter a story prompt** in the sidebar (e.g., "A story about a curious cat who goes to space")
2. **Select the number of sections** you want (2-10 sections)
3. **Click "Generate Story"** and wait for the AI to create your story
4. Each section will be generated with its own illustration

### Editing a Story

After your story is generated:

1. **Click the "✏️ Edit Section" button** under any section you want to modify
2. **Describe your changes** in natural language (e.g., "Make the dragon more friendly" or "Add a rainbow to the scene")
3. **Click "Apply Changes"** to regenerate that section and its image
4. The edited section will maintain continuity with the rest of the story

### Downloading

- Click the **"Download Story as Text"** button at the bottom to save your story
- Images are automatically saved as `0.png`, `1.png`, etc. in the project directory

## Features Explained

### Story Generation Flow

1. **Prompt Validation**: Checks if your input is a valid story request
2. **Outline Creation**: Generates a structured outline with multiple sections
3. **Section Writing**: Creates story text for each section, maintaining continuity
4. **Image Generation**: Creates illustrations based on each section's content

### Editing Function

The `edit_story_section()` function in `model.py` allows you to:
- Modify any section with natural language instructions
- Maintain story context from previous sections
- Automatically regenerate the corresponding illustration
- Keep the story's tone appropriate for children ages 5-10

## Technical Details

- **Frontend**: Streamlit for the web interface
- **AI Model**: OpenAI GPT-3.5-turbo for text generation
- **Image Model**: GPT-image-1 for illustrations
- **State Management**: Streamlit session state for tracking story data
- **Data Persistence**: Stories are saved to `story_context.json`

## Tips for Best Results

- Be specific in your story prompts (include characters, settings, themes)
- Use 3-5 sections for well-paced stories
- When editing, give clear instructions about what you want to change
- The AI maintains continuity between sections automatically

## Troubleshooting

- **Story generation fails**: Check that your OpenAI API key is valid in `.env`
- **Images not displaying**: Ensure you have internet connection and API access
- **"Not a story request" error**: Try rephrasing your prompt to be more story-focused
