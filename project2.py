import streamlit as st
from pypdf import PdfReader
import ollama
import json
from datetime import date

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EduGen AI",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "quiz_data": None,
    "user_answers": {},
    "test_submitted": False,
    "pdf_text": "",
    "weak_topics": [],
    "strong_topics": [],
    "score": 0,
    "total": 0,
    "percentage": 0.0,
    "study_plan": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# HEADER
# =========================================================

st.title("🎓 EduGen AI")

st.subheader(
    "🤖 AI-Powered Exam Preparation & Personalized Learning Platform"
)

st.write(
    "Upload your study material, generate questions, "
    "take mock tests, analyze your performance and "
    "create a personalized study plan."
)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Study Settings")

    exam_date = st.date_input(
        "📅 Exam Date",
        min_value=date.today()
    )

    study_hours = st.slider(
        "⏰ Study Hours Per Day",
        min_value=1,
        max_value=12,
        value=2
    )

    st.divider()

    st.info(
        "Your exam date and available study time "
        "are used to create your personalized study plan."
    )

# =========================================================
# DASHBOARD
# =========================================================

if st.session_state.test_submitted:

    st.divider()

    st.header("📊 Student Performance Dashboard")

    days_remaining = (
        exam_date - date.today()
    ).days

    if days_remaining < 0:
        days_remaining = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🏆 Score",
            f"{st.session_state.score}/{st.session_state.total}"
        )

    with col2:
        st.metric(
            "📊 Accuracy",
            f"{st.session_state.percentage:.1f}%"
        )

    with col3:
        st.metric(
            "📅 Days Until Exam",
            days_remaining
        )

    with col4:
        st.metric(
            "⏰ Study Hours/Day",
            study_hours
        )

    percentage = st.session_state.percentage

    if percentage >= 80:

        st.success(
            "🔥 Excellent Performance! You are performing very well."
        )

    elif percentage >= 60:

        st.info(
            "👍 Good Performance! A little more practice can improve your score."
        )

    else:

        st.warning(
            "⚠️ More Practice Needed. Focus on your weak topics."
        )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🟢 Strong Topics")

        if st.session_state.strong_topics:

            for topic in st.session_state.strong_topics:
                st.success(f"✓ {topic}")

        else:

            st.write("No strong topics identified yet.")

    with col2:

        st.subheader("🔴 Weak Topics")

        if st.session_state.weak_topics:

            for topic in st.session_state.weak_topics:
                st.error(f"⚠ {topic}")

        else:

            st.success("No major weak topics!")

# =========================================================
# PDF UPLOAD
# =========================================================

st.divider()

st.header("📄 Study Material")

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)

# =========================================================
# QUESTION SETTINGS
# =========================================================

number_of_questions = st.number_input(
    "🔢 Number of Questions",
    min_value=1,
    max_value=20,
    value=5
)

difficulty = st.selectbox(
    "🎯 Select Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)

question_type = st.selectbox(
    "📝 Select Question Type",
    [
        "Multiple Choice",
        "True/False",
        "Short Answer",
        "Long Answer"
    ]
)

mock_test = st.checkbox(
    "📝 Enable Mock Test Mode"
)

# =========================================================
# GENERATE QUESTIONS
# =========================================================

if st.button("✨ Generate Questions"):

    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload a PDF first."
        )

    else:

        with st.spinner(
            "📖 Reading your study material..."
        ):

            try:

                reader = PdfReader(uploaded_file)

                text = ""

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text

            except Exception as e:

                st.error(
                    "❌ Could not read the PDF."
                )

                st.code(str(e))

                text = ""

        if not text.strip():

            st.error(
                "❌ No readable text was found in the PDF."
            )

        else:

            st.session_state.pdf_text = text

            st.success(
                "✅ PDF read successfully!"
            )

            with st.expander(
                "📖 View Extracted Text"
            ):

                st.write(
                    text[:3000]
                )

            # =================================================
            # MOCK TEST PROMPT
            # =================================================

            if mock_test:

                prompt = f"""
You are an expert college examination question generator.

Use ONLY the information provided in the study material.

Generate exactly {number_of_questions} multiple-choice questions.

Difficulty level: {difficulty}

IMPORTANT:
Return ONLY a JSON OBJECT.
Do not use markdown.
Do not use ```json.
Do not write any explanation outside the JSON.

Use exactly this format:

{{
  "questions": [
    {{
      "question": "Question text",
      "topic": "Topic name",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A",
      "explanation": "Short explanation"
    }}
  ]
}}

IMPORTANT RULES:

1. Create exactly {number_of_questions} questions.
2. Every question must have exactly 4 options.
3. The answer must exactly match one of the four options.
4. Every question must have a topic.
5. Topics must come from the study material.
6. Questions must be suitable for a college examination.
7. Use ONLY information from the study material.

STUDY MATERIAL:

{text}
"""

            else:

                prompt = f"""
You are an expert college examination question generator.

Use ONLY the information provided in the study material.

Generate {number_of_questions} questions.

Question Type:
{question_type}

Difficulty Level:
{difficulty}

Make the questions clear and suitable for a college examination.

Do not use information outside the study material.

STUDY MATERIAL:

{text}
"""

            # =================================================
            # ASK OLLAMA
            # =================================================

            with st.spinner(
                "🤖 AI is generating your questions..."
            ):

                try:

                    if mock_test:

                        response = ollama.chat(
                            model="llama3.2",
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            format="json",
                            options={
                                "temperature": 0
                            }
                        )

                    else:

                        response = ollama.chat(
                            model="llama3.2",
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )

                    questions = response.message.content

                except Exception as e:

                    st.error(
                        "❌ Could not connect to Ollama."
                    )

                    st.code(str(e))

                    questions = None

            # =================================================
            # PROCESS AI RESPONSE
            # =================================================

            if questions:

                if mock_test:

                    try:

                        # -----------------------------------------
                        # CLEAN AI RESPONSE
                        # -----------------------------------------

                        cleaned_questions = questions.strip()

                        # Remove markdown if AI adds it
                        if "```json" in cleaned_questions:

                            cleaned_questions = (
                                cleaned_questions
                                .replace("```json", "")
                                .replace("```", "")
                                .strip()
                            )

                        elif "```" in cleaned_questions:

                            cleaned_questions = (
                                cleaned_questions
                                .replace("```", "")
                                .strip()
                            )

                        # -----------------------------------------
                        # FIND JSON OBJECT
                        # -----------------------------------------

                        start = cleaned_questions.find("{")
                        end = cleaned_questions.rfind("}")

                        if start == -1 or end == -1:

                            raise ValueError(
                                "No valid JSON object was found."
                            )

                        cleaned_questions = (
                            cleaned_questions[
                                start:end + 1
                            ]
                        )

                        # -----------------------------------------
                        # CONVERT JSON TO PYTHON
                        # -----------------------------------------

                        parsed_data = json.loads(
                            cleaned_questions
                        )

                        # -----------------------------------------
                        # HANDLE DIFFERENT AI FORMATS
                        # -----------------------------------------

                        if isinstance(
                            parsed_data,
                            dict
                        ):

                            quiz_data = parsed_data.get(
                                "questions",
                                []
                            )

                        elif isinstance(
                            parsed_data,
                            list
                        ):

                            quiz_data = parsed_data

                        else:

                            quiz_data = []

                        # -----------------------------------------
                        # CHECK QUESTIONS
                        # -----------------------------------------

                        if not quiz_data:

                            raise ValueError(
                                "No questions were found in AI response."
                            )

                        # -----------------------------------------
                        # VALIDATE QUESTIONS
                        # -----------------------------------------

                        valid_questions = []

                        for question in quiz_data:

                            if not isinstance(
                                question,
                                dict
                            ):
                                continue

                            if (
                                "question" not in question
                                or "options" not in question
                                or "answer" not in question
                            ):
                                continue

                            if len(
                                question["options"]
                            ) != 4:

                                continue

                            if question["answer"] not in question["options"]:

                                continue

                            if "topic" not in question:

                                question["topic"] = "General"

                            if "explanation" not in question:

                                question["explanation"] = (
                                    "Review the study material for this concept."
                                )

                            valid_questions.append(
                                question
                            )

                        if not valid_questions:

                            raise ValueError(
                                "AI questions were not in the expected format."
                            )

                        # -----------------------------------------
                        # SAVE QUIZ
                        # -----------------------------------------

                        st.session_state.quiz_data = (
                            valid_questions
                        )

                        st.session_state.user_answers = {}

                        st.session_state.test_submitted = False

                        st.session_state.weak_topics = []

                        st.session_state.strong_topics = []

                        st.session_state.score = 0

                        st.session_state.total = 0

                        st.session_state.percentage = 0.0

                        st.session_state.study_plan = None

                        st.success(
                            "🎉 Mock test generated successfully!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ AI generated questions, but they could not be processed."
                        )

                        st.write(
                            "The AI response was:"
                        )

                        st.code(
                            questions
                        )

                        st.write(
                            "Technical error:"
                        )

                        st.code(
                            str(e)
                        )

                else:

                    st.divider()

                    st.subheader(
                        "🎓 Generated Questions"
                    )

                    st.write(
                        questions
                    )

# =========================================================
# MOCK TEST
# =========================================================

if st.session_state.quiz_data is not None:

    st.divider()

    st.header(
        "📝 AI Mock Test"
    )

    st.info(
        "Select your answers. You can change your answers before submitting."
    )

    quiz_data = (
        st.session_state.quiz_data
    )

    # -----------------------------------------------------
    # QUESTIONS
    # -----------------------------------------------------

    for i, question in enumerate(
        quiz_data
    ):

        st.markdown(
            f"### Question {i + 1}"
        )

        st.write(
            question["question"]
        )

        previous_answer = (
            st.session_state.user_answers.get(
                i,
                None
            )
        )

        if previous_answer in question["options"]:

            selected_index = (
                question["options"].index(
                    previous_answer
                )
            )

        else:

            selected_index = None

        selected_answer = st.radio(
            "Choose your answer:",
            question["options"],
            index=selected_index,
            key=f"answer_{i}"
        )

        st.session_state.user_answers[i] = (
            selected_answer
        )

        st.divider()

    # -----------------------------------------------------
    # SUBMIT TEST
    # -----------------------------------------------------

    if st.button(
        "🚀 Submit Test"
    ):

        unanswered = []

        for i in range(
            len(quiz_data)
        ):

            if (
                st.session_state.user_answers.get(
                    i
                ) is None
            ):

                unanswered.append(
                    i + 1
                )

        if unanswered:

            st.warning(
                "⚠️ Please answer question(s): "
                + ", ".join(
                    map(
                        str,
                        unanswered
                    )
                )
            )

        else:

            score = 0

            for i, question in enumerate(
                quiz_data
            ):

                if (
                    st.session_state.user_answers[i]
                    == question["answer"]
                ):

                    score += 1

            total = len(
                quiz_data
            )

            percentage = (
                score / total
            ) * 100

            st.session_state.score = score

            st.session_state.total = total

            st.session_state.percentage = percentage

            st.session_state.test_submitted = True

            # =================================================
            # TOPIC ANALYSIS
            # =================================================

            topic_stats = {}

            for i, question in enumerate(
                quiz_data
            ):

                topic = question.get(
                    "topic",
                    "General"
                )

                if topic not in topic_stats:

                    topic_stats[topic] = {
                        "correct": 0,
                        "total": 0
                    }

                topic_stats[topic]["total"] += 1

                if (
                    st.session_state.user_answers[i]
                    == question["answer"]
                ):

                    topic_stats[topic]["correct"] += 1

            weak_topics = []

            strong_topics = []

            for topic, stats in topic_stats.items():

                topic_percentage = (
                    stats["correct"]
                    / stats["total"]
                ) * 100

                if topic_percentage >= 80:

                    strong_topics.append(
                        topic
                    )

                elif topic_percentage < 60:

                    weak_topics.append(
                        topic
                    )

            st.session_state.weak_topics = (
                weak_topics
            )

            st.session_state.strong_topics = (
                strong_topics
            )

            st.balloons()

            st.rerun()

# =========================================================
# RESULTS
# =========================================================

if (
    st.session_state.quiz_data is not None
    and st.session_state.test_submitted
):

    quiz_data = (
        st.session_state.quiz_data
    )

    score = st.session_state.score

    total = st.session_state.total

    percentage = st.session_state.percentage

    st.divider()

    st.header(
        "🏆 Test Results"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🏆 Score",
            f"{score}/{total}"
        )

    with col2:

        st.metric(
            "📊 Accuracy",
            f"{percentage:.1f}%"
        )

    with col3:

        if percentage >= 80:

            performance = "Excellent 🔥"

        elif percentage >= 60:

            performance = "Good 👍"

        else:

            performance = "Needs Practice ⚠️"

        st.metric(
            "📈 Performance",
            performance
        )

    # =====================================================
    # TOPIC ANALYSIS
    # =====================================================

    st.divider()

    st.header(
        "🧠 AI Topic Performance Analysis"
    )

    topic_stats = {}

    for i, question in enumerate(
        quiz_data
    ):

        topic = question.get(
            "topic",
            "General"
        )

        if topic not in topic_stats:

            topic_stats[topic] = {
                "correct": 0,
                "total": 0
            }

        topic_stats[topic]["total"] += 1

        if (
            st.session_state.user_answers[i]
            == question["answer"]
        ):

            topic_stats[topic]["correct"] += 1

    for topic, stats in topic_stats.items():

        topic_percentage = (
            stats["correct"]
            / stats["total"]
        ) * 100

        if topic_percentage >= 80:

            st.success(
                f"🟢 {topic}: "
                f"{stats['correct']}/{stats['total']} "
                f"({topic_percentage:.0f}%)"
            )

        elif topic_percentage >= 60:

            st.info(
                f"🟡 {topic}: "
                f"{stats['correct']}/{stats['total']} "
                f"({topic_percentage:.0f}%)"
            )

        else:

            st.error(
                f"🔴 {topic}: "
                f"{stats['correct']}/{stats['total']} "
                f"({topic_percentage:.0f}%)"
            )

    # =====================================================
    # WEAK TOPICS
    # =====================================================

    st.divider()

    st.subheader(
        "⚠️ Weak Topics"
    )

    if st.session_state.weak_topics:

        for topic in st.session_state.weak_topics:

            st.warning(
                f"📚 Revise: {topic}"
            )

    else:

        st.success(
            "🎉 No major weak topics detected!"
        )

    # =====================================================
    # AI RECOMMENDATION
    # =====================================================

    st.divider()

    st.subheader(
        "🤖 AI Study Recommendation"
    )

    if st.session_state.weak_topics:

        weak_topic_text = ", ".join(
            st.session_state.weak_topics
        )

        recommendation_prompt = f"""
You are an AI academic tutor.

A student completed a mock test.

Score:
{score}/{total}

Accuracy:
{percentage:.1f}%

Weak topics:
{weak_topic_text}

Give a short practical study recommendation.

Explain:

1. What to revise.
2. What to practice.
3. How to improve the score.

Keep it easy to understand.
"""

        try:

            with st.spinner(
                "🤖 AI is analyzing performance..."
            ):

                recommendation_response = (
                    ollama.chat(
                        model="llama3.2",
                        messages=[
                            {
                                "role": "user",
                                "content":
                                recommendation_prompt
                            }
                        ]
                    )
                )

            recommendation = (
                recommendation_response
                .message
                .content
            )

            st.write(
                recommendation
            )

        except Exception:

            st.info(
                "Revise your weak topics and practice more."
            )

    else:

        st.success(
            "🔥 Excellent! Keep practicing!"
        )

    # =====================================================
    # PERSONALIZED STUDY PLAN
    # =====================================================

    st.divider()

    st.header(
        "📅 AI Personalized Study Plan"
    )

    days_remaining = (
        exam_date - date.today()
    ).days

    if days_remaining < 1:

        st.warning(
            "⚠️ Please select a future exam date."
        )

    else:

        st.write(
            f"📅 Days remaining: **{days_remaining}**"
        )

        st.write(
            f"⏰ Study time: **{study_hours} hours/day**"
        )

        if st.button(
            "🚀 Generate My Personalized Study Plan"
        ):

            weak_topic_text = (
                ", ".join(
                    st.session_state.weak_topics
                )
                if st.session_state.weak_topics
                else "No major weak topics"
            )

            strong_topic_text = (
                ", ".join(
                    st.session_state.strong_topics
                )
                if st.session_state.strong_topics
                else "None"
            )

            study_plan_prompt = f"""
You are an expert AI academic planner.

Create a personalized study plan.

Exam date:
{exam_date}

Days remaining:
{days_remaining}

Available study time:
{study_hours} hours per day.

Score:
{score}/{total}

Accuracy:
{percentage:.1f}%

Weak topics:
{weak_topic_text}

Strong topics:
{strong_topic_text}

Create a realistic day-by-day study plan.

Prioritize weak topics.

Include:

- Revision
- Practice questions
- Mock tests
- Final revision

For every day include:

Day number
Topic
Study tasks
Practice
Recommended hours

Keep it practical and easy to follow.
"""

            try:

                with st.spinner(
                    "🤖 Creating your personalized study plan..."
                ):

                    plan_response = (
                        ollama.chat(
                            model="llama3.2",
                            messages=[
                                {
                                    "role": "user",
                                    "content":
                                    study_plan_prompt
                                }
                            ]
                        )
                    )

                st.session_state.study_plan = (
                    plan_response
                    .message
                    .content
                )

                st.success(
                    "🎉 Personalized study plan generated!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "❌ Could not generate study plan."
                )

                st.code(
                    str(e)
                )

        if st.session_state.study_plan:

            st.markdown(
                st.session_state.study_plan
            )

    # =====================================================
    # QUESTION REVIEW
    # =====================================================

    st.divider()

    st.subheader(
        "📖 Question Review"
    )

    for i, question in enumerate(
        quiz_data
    ):

        user_answer = (
            st.session_state.user_answers[i]
        )

        correct_answer = (
            question["answer"]
        )

        if user_answer == correct_answer:

            st.success(
                f"Question {i + 1}: ✅ Correct"
            )

        else:

            st.error(
                f"Question {i + 1}: ❌ Incorrect"
            )

            st.write(
                f"Your Answer: {user_answer}"
            )

            st.write(
                f"Correct Answer: {correct_answer}"
            )

            st.write(
                "Explanation:",
                question.get(
                    "explanation",
                    "No explanation available."
                )
            )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🎓 EduGen AI | Python | Streamlit | "
    "Ollama | Llama 3.2 | PyPDF | NLP | LLM"
)