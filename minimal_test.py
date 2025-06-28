"""
Minimal Gradio test to check if the basic interface works
"""

import gradio as gr

def simple_function(text):
    return f"You typed: {text}"

# Create the simplest possible interface
demo = gr.Interface(
    fn=simple_function,
    inputs="text",
    outputs="text",
    title="🧪 Minimal Gradio Test"
)

if __name__ == "__main__":
    print("🧪 Testing minimal Gradio interface...")
    try:
        demo.launch(server_name="127.0.0.1", server_port=7860)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Pydantic compatibility issue - need to fix versions")