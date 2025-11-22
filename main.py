import streamlit as st
import os
from dotenv import load_dotenv
from model import Model
import base64
from io import BytesIO
from PIL import Image
import concurrent.futures
import time
from utils import *
from judge import *


# """ 
# TO RUN THIS FILE:
# -----------------

# pip install -r requirments.txt  # Install Requirments 

# streamlit run main.py   # NOTE: python main.py won't work

# """

# """
# Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

# I think a major priority would be to make it easier to edit the story. 
# Right now you can edit specific sections, but any changes that are made are not currently being applied to other sections.
# For example, if I were to change the name of a charecter in a given prompt, this would not be carried to other sections.

# I also want to add somemore error handeling. 
# Although rare, the API calls sometimes return the wrong format and this is not handles well
# Also sometimes the API call will throw an error. 
# For example if I ask it for a story about Lebron James it will say it can't generate images of that type of content.
# I think this is because the model is prevented from generating pictures of real people.

# I also would try to tune the image generation process more. I think I would add an "Image Planner" step that would plan the images better.
# Right now there isn't continuity between the pictures and I think this would help with that. 

# I think text prompts are ok but could also be improved.

# """



load_dotenv()

st.set_page_config(
    page_title="Kids Story Generator",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'story_generated' not in st.session_state:
        st.session_state.story_generated = False
    if 'sections' not in st.session_state:
        st.session_state.sections = []
    if 'images' not in st.session_state:
        st.session_state.images = []
    if 'section_prompts' not in st.session_state:
        st.session_state.section_prompts = []
    if 'editing_section' not in st.session_state:
        st.session_state.editing_section = None
    if 'model' not in st.session_state:
        st.session_state.model = None
    if 'img_model' not in st.session_state:
        st.session_state.img_model = "dall-e-3"
    if 'img_size' not in st.session_state:
        st.session_state.img_size = "512x512"
    if 'parallel_images' not in st.session_state:
        st.session_state.parallel_images = True
    if 'judge' not in st.session_state:
        st.session_state.judge = None
    if "outline_feedback" not in st.session_state:
        st.session_state.outline_feedback = None
    if "original_prompt" not in st.session_state:
        st.session_state.original_prompt = None
    

def generate_story(prompt, num_sections, parallel_images=True):
    """Generate a new story"""
    model = st.session_state.model
    judge = st.session_state.judge

    st.session_state.original_prompt = prompt
    with st.spinner("Checking if your prompt is a story request..."):
        if not judge.is_story_prompt(prompt):
            st.error("This doesn't look like a story request. Please try again with a story prompt!")
            return False

    checks = 0
    score = 0
    
    age_appropriateness = 0
    engagement = 0
    clarity = 0
    education = 0
    while checks < 3 and score < 17:
        with st.spinner(f"Creating story outline...\n"
                        f"\nItterations: {checks}\n"
                        f"\nScore: {score}\n"
                        f"\nage_approriatness: {age_appropriateness}\n"
                        f"\nengagement: {engagement}\n"
                        f"\nclarity: {clarity}\n"
                        f"\neducation: {education}\n"):
            section_prompts = model.generate_story_outline(prompt, num_sections, st.session_state.outline_feedback, st.session_state.section_prompts)
            st.session_state.section_prompts = section_prompts
            
            feedback = judge.judge_outline(section_prompts, prompt)
            print(feedback['scores'].keys())
            st.session_state.outline_feedback = feedback
            
            # score = sum(feedback['scores'].values())
            checks += 1
            age_appropriateness = feedback['scores']['age_appropriateness']
            engagement = feedback['scores']['engagement']
            clarity = feedback['scores']['clarity']
            education = feedback['scores']['education']
            
            score = age_appropriateness + engagement + clarity + education

    sections = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    score = 0
    checks = 0
    
    age_appropriateness = 0
    engagement = 0
    clarity = 0
    adherence = 0
    
    while score < 17 and checks < 3:
        with st.spinner(f"Creating story...\n"
                        f"\nItterations: {checks}\n"
                        f"\nScore: {score}\n"
                        f"\nage_approriatness: {age_appropriateness}\n"
                        f"\nengagement: {engagement}\n"
                        f"\nclarity: {clarity}\n"
                        f"\nadherance: {adherence}\n"):
            for i, section_prompt in enumerate(section_prompts):
                status_text.text(f"Writing section {i+1}/{num_sections}...")
                section = model.generate_story_section(section_prompt['prompt'], sections[:i])
                sections.append(section)
                progress_bar.progress((i + 1) / num_sections)

            st.session_state.sections = sections
            feedback = judge.judge_story(sections, st.session_state.original_prompt)
            
            score = sum(feedback['scores'].values())
            checks += 1
            
            
            age_appropriateness = feedback['scores']['age_appropriateness']
            engagement = feedback['scores']['engagement']
            clarity = feedback['scores']['clarity']
            adherence = feedback['scores']['adherence']

    status_text.text("Generating images...")
    start_time = time.time()
    images = [None] * num_sections
    img_size = st.session_state.img_size

    if parallel_images and num_sections > 1:
        # Generate images in parallel for efficency
        status_text.text(f"Creating all {num_sections} images in parallel (faster)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(num_sections, 5)) as executor:
            futures = [
                executor.submit(generate_single_image, (section, i, model, img_size))
                for i, section in enumerate(sections)
            ]

            for future in concurrent.futures.as_completed(futures):
                index, img_b64 = future.result()
                images[index] = img_b64
                completed = sum(1 for img in images if img is not None)
                status_text.text(f"Images complete: {completed}/{num_sections}")
    else:
        # Generate images sequentially
        for i, section in enumerate(sections):
            status_text.text(f"Creating image {i+1}/{num_sections}...")
            img_b64 = model.generate_image_from_text(section, size=img_size)
            images[i] = img_b64
            save_base64_image(img_b64, f"{i}.png")

    elapsed_time = time.time() - start_time
    st.session_state.images = images
    st.session_state.story_generated = True


    status_text.text(f"Story complete! (Images generated in {elapsed_time:.1f}s)")
    progress_bar.empty()
    time.sleep(1)
    status_text.empty()

    return True

def edit_section(section_idx, edit_instruction):
    """Edit a specific section of the story"""
    model = st.session_state.model
    original_section = st.session_state.sections[section_idx]
    previous_sections = st.session_state.sections[:section_idx] if section_idx > 0 else None

    with st.spinner("Editing section..."):
        edited_section = model.edit_story_section(
            original_section,
            edit_instruction,
            previous_sections
        )
        st.session_state.sections[section_idx] = edited_section

    # Regenerate image for edited section
    with st.spinner("Regenerating image..."):
        img_size = st.session_state.img_size
        img_b64 = model.generate_image_from_text(edited_section, size=img_size)
        st.session_state.images[section_idx] = img_b64
        save_base64_image(img_b64, f"{section_idx}.png")

        # Update context
        
    st.success("Section updated!")
    st.session_state.editing_section = None

def main():
    initialize_session_state()

    st.title("Kids Story Generator")
    st.markdown("### Create magical stories with pictures for kids ages 5-10!")

    # Sidebar for story generation
    with st.sidebar:
        st.header("Create a New Story")

        story_prompt = st.text_area(
            "What kind of story do you want?",
            placeholder="A story about a brave knight and a friendly dragon...",
            height=100
        )

        num_sections = st.slider(
            "How many sections?",
            min_value=2,
            max_value=10,
            value=3
        )

        with st.expander("Image Settings"):
            img_model = st.selectbox(
                "Image Model",
                options=["dall-e-2", "dall-e-3"],
                index=1,
                help="DALL-E 2 is faster and cheaper, DALL-E 3 is higher quality but slower"
            )
            st.session_state.img_model = img_model

            if img_model == "dall-e-2":
                img_size = st.selectbox(
                    "Image Size",
                    options=["256x256", "512x512", "1024x1024"],
                    index=1,
                    help="Smaller = faster generation"
                )
            else:
                img_size = st.selectbox(
                    "Image Size",
                    options=["1024x1024", "1024x1792", "1792x1024"],
                    index=0
                )
            st.session_state.img_size = img_size

            parallel = st.checkbox(
                "Parallel image generation",
                value=True,
                help="Generate all images at once (much faster!)"
            )
            st.session_state.parallel_images = parallel


        # Initialize model with selected settings
        if st.session_state.model is None or st.session_state.model.img_model != img_model:
            st.session_state.model = Model(img_model=img_model)
        if st.session_state.judge is None:
            st.session_state.judge = Judge()

        if st.button("Generate Story", type="primary", use_container_width=True):
            if story_prompt:
                st.session_state.story_generated = False
                st.session_state.sections = []
                st.session_state.images = []

                generate_story(story_prompt, num_sections, st.session_state.parallel_images)
            else:
                st.warning("Please enter a story prompt!")

        st.divider()

        if st.session_state.story_generated:
            st.markdown("**Story generated!**")
            st.markdown(f"Sections: {len(st.session_state.sections)}")

            if st.button("Start Over", use_container_width=True):
                st.session_state.story_generated = False
                st.session_state.sections = []
                st.session_state.images = []
                st.session_state.section_prompts = []
                st.rerun()

    # Main content area
    if st.session_state.story_generated:
        st.success("Your story is ready!")

        # Display each section with its image
        for i, (section, image_b64) in enumerate(zip(st.session_state.sections, st.session_state.images)):
            with st.container():
                col1, col2 = st.columns([3, 2])

                with col1:
                    
                    if st.session_state.section_prompts:
                        st.markdown(f"### {st.session_state.section_prompts[i]['title']}")
                    st.markdown(f"Section {i+1}")
                    st.markdown(section)

                    # Edit button
                    if st.button(f"Edit Section {i+1}", key=f"edit_btn_{i}"):
                        st.session_state.editing_section = i

                    # Edit interface
                    if st.session_state.editing_section == i:
                        with st.form(key=f"edit_form_{i}"):
                            edit_instruction = st.text_area(
                                "What would you like to change?",
                                placeholder="Make it more exciting, add a specific character, change the ending...",
                                key=f"edit_input_{i}"
                            )

                            col_submit, col_cancel = st.columns(2)
                            with col_submit:
                                submit = st.form_submit_button("Apply Changes", type="primary")
                            with col_cancel:
                                cancel = st.form_submit_button("Cancel")

                            if submit and edit_instruction:
                                edit_section(i, edit_instruction)
                                st.rerun()
                            elif cancel:
                                st.session_state.editing_section = None
                                st.rerun()

                with col2:
                    try:
                        img = base64_to_image(image_b64)
                        st.image(img, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying image: {e}")

                st.divider()

        # Download section
        st.markdown("### Download Your Story")

        full_story = "\n\n".join([
            f"Section {i+1}**\n{section}"
            for i, section in enumerate(st.session_state.sections)
        ])

        st.download_button(
            label="Download Story as Text",
            data=full_story,
            file_name="kids_story.txt",
            mime="text/plain"
        )

    else:
        st.info("👈 Use the sidebar to create your first story!")

        st.markdown("""
        ### How it works:

        1. **Describe your story** in the sidebar (e.g., "A story about a curious cat who goes to space")
        2. **Choose how many sections** you want (2-10 sections)
        3. **Click Generate Story** and watch the magic happen!
        4. **Edit any section** after the story is generated
        5. **Download** your completed story

        Each section comes with a beautiful picture to bring your story to life!
        """)

if __name__ == "__main__":
    main()
