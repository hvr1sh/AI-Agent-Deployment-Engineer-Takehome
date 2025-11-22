```
┌─────────────────────────────────────────────────────────────────┐
│                        STORY GENERATION                          │
└─────────────────────────────────────────────────────────────────┘

User Input
   ↓
┌──────────────────────┐
│ Streamlit Frontend   │
│ - story_prompt: str  │
│ - num_sections: int  │
└──────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: Validate Prompt                                          │
│ Model.is_story_prompt(prompt)                                    │
│   → OpenAI API Call (GPT-3.5-turbo)                              │
│   → Returns: "1" (valid) or "0" (invalid)                        │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: Generate Outline                                         │
│ Model.generate_story_outline(prompt, num_sections)               │
│   → OpenAI API Call (GPT-3.5-turbo)                              │
│   → Returns: JSON array of section objects                       │
│     [{                                                           │
│       "section_id": 1,                                           │
│       "title": "...",                                            │
│       "summary": "...",                                          │
│       "prompt": "..."                                            │
│     }, ...]                                                      │
└──────────────────────────────────────────────────────────────────┘
   ↓                                                            ↑
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: Judge Outline (Loop)                                     │
│ For all section_promts from Model.generate_story_outline():      │
│  Model.generate_story_section(section_prompts, origininal_prompt)│
│     → OpenAI API Call (GPT-3.5-turbo)                            │
│     → Returns: Feedback (Json)                                   │
│     → If score < 17 or less than 3 itterations loop back         │
└──────────────────────────────────────────────────────────────────┘
  ↓ 
┌──────────────────────────────────────────────────────────────────┐
│ Step 4: Generate Each Section (Loop)                             │
│ For each section_prompt in outline:                              │
│   Model.generate_story_section(section_prompt, previous_texts)   │
│     → OpenAI API Call (GPT-3.5-turbo)                            │
│     → Returns: Story text (2-5 sentences)                        │
│     → Appends to sections array                                  │
└──────────────────────────────────────────────────────────────────┘
   ↓                                                            ↑
┌──────────────────────────────────────────────────────────────────┐
│ Step 5: Judge Story (Loop)                                       │
│ For all sections from Model.generate_story_section():            │
│  Model.generate_story_section(section_prompts, origininal_prompt)│
│     → OpenAI API Call (GPT-3.5-turbo)                            │
│     → Returns: Feedback (Json)                                   │
│     → If score < 17 or less than 3 itterations loop back         │
└──────────────────────────────────────────────────────────────────┘
   ↓ 
┌──────────────────────────────────────────────────────────────────┐
│ Step 6: Generate Images (Loop)                                   │
│ For each section_text in sections:                               │
│   Model.generate_image_from_text(section_text)                   │
│     → OpenAI API Call (gpt-image-1)                              │
│     → Returns: Base64 encoded image                              │
│     → Saves as {index}.png                                       │
│     → Appends to images array                                    │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 7: Save Context                                             │
│ StoryContext.update_story_context(                               │
│   prompt=...,                                                    │
│   num_sections=...,                                              │
│   section_prompts=...,                                           │ 
│   sections=...,                                                  │
│   dump=True                                                      │
│ )                                                                │
│   → Saves to story_context.json                                  │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────┐
│ Display in UI        │
│ - Sections + Images  │
│ - Edit buttons       │
│ - Download button    │
└──────────────────────┘
```

### 2. Story Editing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        STORY EDITING                             │
└─────────────────────────────────────────────────────────────────┘

User Action: Click "Edit Section N"
   ↓
┌──────────────────────┐
│ Streamlit UI         │
│ - Show edit form     │
│ - User enters:       │
│   edit_instruction   │
└──────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 1: Edit Section Text                                       │
│ Model.edit_story_section(                                       │
│   original_section=sections[N],                                 │
│   edit_instruction="...",                                       │
│   previous_sections=sections[0:N]                               │
│ )                                                               │
│   → OpenAI API Call (GPT-3.5-turbo)                            │
│   → Returns: Edited section text                               │
│   → Updates session_state.sections[N]                          │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 2: Regenerate Image                                        │
│ Model.generate_image_from_text(edited_section)                  │
│   → OpenAI API Call (gpt-image-1)                               │
│   → Returns: New base64 image                                   │
│   → Updates session_state.images[N]                             │
│   → Saves as {N}.png (overwrites)                               │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────────────────────────────────────────────────┐
│ Step 3: Update Context                                          │
│ StoryContext.update_story_context(sections=..., dump=True)      │
│   → Updates story_context.json                                  │
└──────────────────────────────────────────────────────────────────┘
   ↓
┌──────────────────────┐
│ Refresh UI           │
│ - Show edited text   │
│ - Show new image     │
└──────────────────────┘
```