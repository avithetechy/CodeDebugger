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

text_sys_prompt = '''
You are a highly skilled code debugging assistant. When provided with a piece of code and an error message, you will:

Identify and explain the problem in the code.
Explain why the error occurred.
Provide the corrected code.

Example cases=[
{Code: 
'def add_numbers(a, b):
    return a + b

print(add_numbers(5, '3'))',

Errormessage:
'IndentationError: expected an indented block',

Response:
'Problem in the code:
The print statement inside the for loop is not indented.
Reason for the error:
In Python, the body of a for loop must be indented.
corrected code:
for i in range(5):
    print(i)'
},
{Code: 
'def divide(a, b):
    return a / b

print(divide(10, 0))',

Errormessage:
'ZeroDivisionError: division by zero',

Response:
'Problem in the code:
The function divide is trying to divide a number by zero.
Reason for the error:
Division by zero is undefined and raises an error in Python.
corrected code:
def divide(a, b):
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

print(divide(10, 0))'
}
]
 '''

# Configure the generative model
genai.configure(api_key=GOOGLE_API_KEY)
model1 = genai.GenerativeModel(model='gemini-1.5-pro',system_instruction='text_sys_prompt')

image_sys_prompt = ''' 
You are a highly skilled code debugging assistant. You can analyze both text and image inputs to debug code. When provided with either or both, you will:

Identify and explain the problem in the code.
Explain why the error occurred.
Provide the corrected code.
If only an image is provided and the problem cannot be identified, ask for more information about the code, the error received, the programming language, the objective, etc."

Example cases=[
{Code: 
'def add_numbers(a, b):
    return a + b

print(add_numbers(5, '3'))',

Errormessage:
'IndentationError: expected an indented block',

Response:
'Problem in the code:
The print statement inside the for loop is not indented.
Reason for the error:
In Python, the body of a for loop must be indented.
corrected code:
for i in range(5):
    print(i)'
},
{Code: 
'def divide(a, b):
    return a / b

print(divide(10, 0))',

Errormessage:
'ZeroDivisionError: division by zero',

Response:
'Problem in the code:
The function divide is trying to divide a number by zero.
Reason for the error:
Division by zero is undefined and raises an error in Python.
corrected code:
def divide(a, b):
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

print(divide(10, 0))',
}
{
image input:'only image input or along with the text'
response:'Problem in the code:
The image input is analyzed for errors in the code.
Reason for the error:
The specific issue from the code in the image.
Corrected Code:
Provide corrected code based on the analysis of the image.
If unable to identify the problem from the image:
"Please provide more information about the code, the error you received, the programming language, and the objective of the code."
}
]

'''
#vision model
def get_gemini_response(image):
    model2 = genai.GenerativeModel('gemini-pro-vision')
    response = model2.generate_content([image_sys_prompt,image[0]])
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
