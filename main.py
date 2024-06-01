from dotenv import load_dotenv
import os
import streamlit as st
import textwrap
from PIL import Image
import google.generativeai as genai

load_dotenv()  # take environment variables from .env

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# Get API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the generative model
genai.configure(api_key=GOOGLE_API_KEY)
model1 = genai.GenerativeModel('gemini-1.5-pro')

#vision model
def get_gemini_response(image):
    model2 = genai.GenerativeModel('gemini-pro-vision')
    response = model2.generate_content([image[0]])
    return response.text

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit UI
st.title("Code Debugger Chatbot")

st.write("Enter your code:")
code_input = st.text_area("Code:")

st.write("Enter the error you got:")
error_input = st.text_area("Error:")

st.write("You can even provide an image of the code or error")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
image=""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True) 



if st.button("Submit"):
    if code_input or error_input or uploaded_file:

        code_response = model1.generate_content("code: " + code_input + " error: " + error_input)
        st.markdown(to_markdown(code_response.text))

        if uploaded_file:
            image_data = input_image_setup(uploaded_file)
            response=get_gemini_response(image_data)
            st.write(response)
    else:
        st.warning("Please fill in all the fields.")
