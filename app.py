import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px

# =========================
# 🔑 Setup Gemini API
# =========================
genai.configure(api_key="AIzaSyBEmU1wvMtXzuBvFBJOnrj00fbDEwhX2z0")  

# Gemini helper function
def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

# 🔧 Cleanup function for Gemini code
def clean_code(code: str):
    code = code.strip()
    # Remove markdown fences
    if "```" in code:
        parts = code.split("```")
        code = parts[1] if len(parts) > 1 else code
    code = code.replace("python", "")
    # Remove fig.show()
    code = code.replace("fig.show()", "")
    return code.strip()

# =========================
# 🚀 Streamlit App UI
# =========================
st.set_page_config(
    page_title="Viscelora",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Viscelora")
st.markdown(
    """
    Welcome to the **AI-powered Data Visualization Tool** 🎨  
    Upload your dataset and let **Viscelora** create insightful visualizations for you.  
    """
)

# Sidebar for navigation
st.sidebar.header("⚙️ Menu")

# 1️⃣ Upload Excel
uploaded_file = st.sidebar.file_uploader("Upload your Excel/CSV file", type=["xlsx", "csv"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Show dataset preview in tabs
    tab1, tab2 = st.tabs(["📋 Data Preview", "📌 Column Info"])

    with tab1:
        st.subheader("Dataset Preview")
        st.dataframe(df.head(), use_container_width=True)

    with tab2:
        st.subheader("📌 Available Columns")
        st.write(list(df.columns))

    st.markdown("---")

    # 2️⃣ Get Visualization Suggestions
    if st.sidebar.button("💡 Get Visualization Suggestions"):
        prompt = f"These are the dataset columns: {list(df.columns)}. Suggest 3 meaningful visualizations with short explanation."
        suggestions = ask_gemini(prompt)
        
        st.subheader("💡 Suggested Visualizations")
        st.info(suggestions)

    # 3️⃣ User Selection or Custom Input
    choice = st.sidebar.radio("Choose Option:", ["Suggested Plot", "Custom Plot"])

    if choice == "Suggested Plot":
        user_choice = st.text_input("✏️ Enter your chosen suggestion (e.g., Sales over Time)")
    else:
        user_choice = st.text_area("🖌️ Describe your custom plot", placeholder="e.g., Scatter plot of Sales vs Profit")

    # 4️⃣ Generate and Show Plot
    if st.button("🚀 Generate Plot"):
        if not user_choice:
            st.warning("⚠️ Please enter your choice or custom plot description.")
        else:
            with st.spinner("🔮 Viscelora is generating your plot..."):
                # Ask Gemini for plotting code
                code_prompt = f"""
                Write Python code using plotly.express to create a visualization for: 
                '{user_choice}'.
                The dataset is a pandas dataframe named df with columns {list(df.columns)}.
                Only return the code and fig.show().
                """
                plot_code = ask_gemini(code_prompt)

            st.subheader("🔧 Generated Code")
            st.code(plot_code, language="python")

            # Clean Gemini code
            cleaned_code = clean_code(plot_code)

            try:
                # Execute safely
                local_env = {"df": df, "px": px}
                exec(cleaned_code, local_env)
                fig = local_env.get("fig", None)

                if fig:
                    st.subheader("📊 Visualization Output")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No figure generated. Check the Gemini code.")
            except Exception as e:
                st.error(f"❌ Error executing plot code: {e}")

            # 5️⃣ Ask Gemini for plot description
            desc_prompt = f"Explain in 2-3 lines what the plot '{user_choice}' shows."
            desc = ask_gemini(desc_prompt)

            st.subheader("📝 Plot Description")
            st.success(desc)

else:
    st.info("⬅️ Upload an Excel/CSV file from the sidebar to get started!")
