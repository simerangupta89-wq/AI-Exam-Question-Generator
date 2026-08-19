import streamlit as st
from pypdf import PdfReader
import ollama

# -------------------------------
# PAGE TITLE
# -------------------------------

st.title("🎓 AI Exam Question Generator")

st.write("Upload your study material and generate exam questions using AI!")

# -------------------------------
# PDF UPLOAD
# -------------------------------

uploaded_file = st.file_uploader(
    "📄 Upload your PDF",
    type=["pdf"]
)

# -------------------------------
# NUMBER OF QUESTIONS
# -------------------------------

number_of_questions = st.number_input(
    "🔢 Number of Questions",
    min_value=1,
    max_value=20,
    value=5
)

# -------------------------------
# DIFFICULTY
# -------------------------------

difficulty = st.selectbox(
    "🎯 Select Difficulty",
    ["Easy", "Medium", "Hard"]
)

# -------------------------------
# GENERATE BUTTON
# -------------------------------

if st.button("✨ Generate Questions"):

    if uploaded_file is None:

        st.warning("⚠️ Please upload a PDF first.")

    else:

        # Read PDF
        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

        st.success("✅ PDF read successfully!")

        # Show small part of extracted text
        with st.expander("📖 View Extracted Text"):
            st.write(text[:3000])

        # -------------------------------
        # AI PROMPT
        # -------------------------------

        prompt = f"""
You are an expert exam question generator.

Use ONLY the information given in the study material.

Generate {number_of_questions} multiple-choice questions.

Difficulty level: {difficulty}

For every question provide:

Question:
A.
B.
C.
D.

Correct Answer:
Explanation:

Make the questions clear and suitable for a college exam.

Study Material:

{text}
"""

        # -------------------------------
        # ASK OLLAMA
        # -------------------------------

        with st.spinner("🤖 AI is generating your questions..."):

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

        # -------------------------------
        # DISPLAY QUESTIONS
        # -------------------------------

        questions = response.message.content

        st.subheader("🎓 Generated Questions")

        st.write(questions)