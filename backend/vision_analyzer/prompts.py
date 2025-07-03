# vision_analyzer/prompts.py

def create_vision_prompt(contextual_text: str, analysis_type: str = "technical") -> str:
    """
    Generates a specialized prompt for analyzing a video frame.

    Args:
        contextual_text: The text from subtitles occurring around the time of the frame.
        analysis_type: The type of content expected (e.g., 'technical', 'general').

    Returns:
        A string containing the formatted prompt for the vision model.
    """
    base_prompt = (
        "You are an expert technical analyst. Your task is to analyze the provided video frame "
        "and describe it with precision, focusing on its relevance to the provided context."
    )

    if analysis_type == "technical":
        instructions = (
            "1. **Classify the Screen Type**: Determine if the frame shows a 'code_editor', 'terminal', 'diagram', 'webpage', 'presentation', or 'other'.\n"
            "2. **Describe the Content**: Provide a detailed summary of what is visible. If it's code, identify the language and explain the code's purpose. If it's a terminal, describe the commands and their output. If it's a diagram, explain what it represents.\n"
            "3. **Correlate with Context**: Explain how the visual information relates to the following text spoken at the same time. Is the screen demonstrating what is being said?\n"
        )
    else: # General purpose prompt
        instructions = (
            "1. **Describe the Scene**: Provide a general description of the image.\n"
            "2. **Identify Key Objects**: List the most important objects or elements in the scene.\n"
            "3. **Connect to Context**: Explain how the scene relates to the provided spoken text.\n"
        )
    
    context_section = f"\n**Spoken Context:**\n---\n{contextual_text}\n---\n"

    return f"{base_prompt}\n\n{instructions}\n{context_section}\nAnalyze the provided image now."

