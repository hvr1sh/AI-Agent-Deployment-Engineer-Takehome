## Running the App
- pip install -r requirments.txt
- create .env file with OPENAI_API_KEY
   ```
   OPENAI_API_KEY= "your api_key"
   ```
- **streamlit run main.py**
The app will open in your default web browser at `http://localhost:8501`

## Component Descriptions

### Frontend: Streamlit (main.py)
- **Session State Management**: Stores story data, sections, images, edit state
- **User Interface**: Sidebar for input, main area for story display
- **Real-time Updates**: Progress bars and spinners during generation
- **Edit Interface**: Forms for editing individual sections

### Model Layer: Model class (model.py)

The Model class handles all generative functions involving OpenAI. This includes and generative tasks.

- **generate_story_outline()**: Creates structured outline with N sections
- **generate_story_section()**: Writes individual section text with context
- **generate_image_from_text()**: Creates illustration from section text
- **edit_story_section()**: Modifies section based on user instructions

### Judge Layer: Judge class (judge.py)

The Judge class handles all judging taks

- **is_story_prompt()**: Validates if input is a story request
- **judge_story_outline()**: Judges a story outline
- **judge_story_section()**: Judges full story

### Context Manager: StoryContext (story_context.py)

Context manager was only used for testing, it is not used in main.py. Helped me track metadata and also dump it to JSON. Having a JSON was helpful as I was able to track model outputs at different parts of the project. In final version (main.py) I used streamlit.session_state() to manage this metadata instead.

- **update_story_context()**: Updates internal context dictionary
- **reset_story_context()**: Clears all metadata

### Data Storage
- **story_context.json**: Persistent storage of story data
- **{N}.png files**: Generated images saved to disk
- **Session State**: In-memory storage during Streamlit session

## API Calls Summary

| Operation | Model | Purpose | Output |
|-----------|-------|---------|--------|
| Validate Prompt | gpt-3.5-turbo | Check if valid story request | "0" or "1" |
| Generate Outline | gpt-3.5-turbo | Create story outline | JSON array |
| Generate Section | gpt-3.5-turbo | Write story text | Text string |
| Edit Section | gpt-3.5-turbo | Modify story text | Text string |
| Generate Image | dalle-2 or dalle-3 (User Defined) | Create illustration | Base64 image |

## Performance Considerations

### Validate Prompt
Optimized prompt to take as little tokens as I could. The output of this step is only 1 charecter, 0 or 1 as well which should help use less tokens

### Image Generation:

- I don't think 5 year old me would have been thrilled to read a book with no pictures so I decided to 
- Image generation takes the most time

- **Model Selection:**
   - Initially was using gpt-image-1 model
      - Slow
      - Expensive
   - Learned the dalle-2 and dalle-3 were much faster
      - dalle-2 was cheaper but the quality was siginificantly worse than dalle-3
      - dalle-3 was more expensive and there was no point using it, espcially for testing
      - Decided to allow user to select between the 2 models

- **Parallel Image Generation:**
   - Since generating an image invloved an asynchronis API call (I/O bound task) the python gil was not relavent, allowing for multitheading
      - NOTE: Not truley running in parrallel. Python is actually context switching between threads to check if the response from API has been recieved. Once recieved, python handles the response before switching to next thread. However since API requests are not handled localy, this will still boost performance significanly as the requests themselves will not be handled sequentially.
   - Decided to include option to turn parallel generation on and off to compare performance in the UI.
   - The main drawback is that you cannot pass previouse images in as context

- **Parallel Text Generation:**
   - Text is not generated in parallel like the images it is sequential.
      - Text is generated much faster than an image
      - Since all the text requires context about what comes before it, previouse sections are passed in as context for the next setion


## AI Usage
**Tools Used**:
   - ChatGPT - Debugging and some Code Generation
   - Calude Code - Documentation
- **Documentation**
   - The biggest use of AI was for documentaion. I used it to build the block Diagram and this file
   - That being said I also went through and made significant edits manually
- **Code Generation**
   - The vast majority of functions in model.py were written by me, occasionally using ChatGPT to debug
   - ChatGPT also helped alot more for the UI components and streamlit. Usage of ChatGPT improved UI quality alot
   - ChatGPT inspired the switch from using story_context.py to streamlit.session_context()


