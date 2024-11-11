# 🚀Super AI Assistant App

An interactive AI-powered assistant built with Streamlit! Chat with advanced models, get voice responses, and upload all kinds of media to unlock the potential of AI in real time. Super AI Assistant brings Google Gemini and Groq models directly to you with a range of features and an easy-to-use interface.

---

## Features

- **Model Selection:** Pick between Google Gemini or Groq's open-source models. The app's sidebar adapts dynamically based on your choice.

- **Multi-Modality:** Enter text or upload images, audio, video, PDFs, Docx files, and even record voice input, all in one place. Snap a picture with your camera, and the app will process it as input!

- **Voice Response:** Get voice responses with multiple voice options to personalize your experience.

- **Chat History:** Keep track of your conversation history. The app remembers your messages, allowing you to continue from where you left off—or reset anytime for a fresh start.

- **Agent-Based Tasks:** Select tools for specific agent tasks to retrieve real-time information on your chosen topics.

- **Summarization:** Effortlessly summarize webpages and YouTube videos.
Just input a URL, and the app will provide a markdown summary!

---

## 📚 Libraries Used

- **Streamlit:** Main framework for creating the app interface.
- **Edge TTS:** For generating voice responses.
- **Google Generative AI:** For advanced Google Gemini functionalities.
- **Langchain:** For Agent-based tasks, chatbot, and summarization.
- **Langchain Groq:** For Groq's lightning-fast LLMs.

---
## Getting Started
### Prerequisites
- Python 3.11 or higher
- Google Gemini and Groq API keys
 
### 🛠️ Installation & Setup

**Step 1: Clone the Repository:**
```bash
git clone https://github.com/aasherkamal216/Super-AI-Assistant-App.git
cd Super-AI-Assistant-App
```

**Step 2: Set Up a Virtual Environment:**
Create a virtual environment to keep dependencies organized.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

**Step 3: Install Dependencies:**
Install all required packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

**Step 4: Create Your API Keys:**
Create your API keys for Google Gemini and Groq and save them somewhere secure. You'll need to put them in the app's sidebar.

**Step 5: Run the App:**

```bash
streamlit run app.py
```

Your app should now be running at `http://localhost:8501`!

---

##  How to Use
1. **Enter API Keys**: Go to the sidebar and enter your API keys for Google Gemini and Groq.
2. **Choose a Model**: Select between Google Gemini or Groq in the sidebar.
3. **Choose Media Type**: For Google Gemini, options include text, images, audio, video, PDFs and Docx files. Upload any of these media files and ask questions.
4. **Agent Mode**: Select any LLM other than Gemini, you'll see a radio button to select Agent. Once selected, choose tools for the Agent.
5. **Summarization**: If the selected LLM is from Groq, you can choose Summarization. Enter a URL and get a markdown summary.
---

Get ready to experience a powerful, multi-modal AI assistant with features that adapt to all your needs! 🚀

---
