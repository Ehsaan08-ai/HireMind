# 🧠 HireMind: AI-Powered Resume Scanner & ATS Compatibility Analyzer

HireMind is a state-of-the-art Application Tracking System (ATS) optimization tool that leverages Natural Language Processing (NLP), Deep Learning, and Large Language Models (LLMs) to bridge the gap between job descriptions and resumes. 

Designed to empower both job seekers and recruiters, HireMind extracts critical skills, evaluates semantic relevance, validates resume formatting compatibility, and generates publication-grade PDF analysis reports to optimize resumes for modern automated hiring algorithms.

---

## 🔗 Live Application & Landing Page

* **Live Application (Frontend)**: [https://hiremind-ats-scorer.streamlit.app/](https://hiremind-ats-scorer.streamlit.app/)
* **Project Landing Page**: *Not Created Yet!*

---

## 🚀 The Architecture Journey: Why I Migrated from Render to AWS

Initially, the project was planned for deployment on Render's standard server tier. However, modern AI-driven architectures carry substantial memory footprints. During deployment, the application consistently crashed due to Out-Of-Memory (OOM) errors.

### The Memory Bottleneck of Free Hosting
Your HireMind backend relies on highly advanced, specialized machine learning libraries:
1. **PyTorch & Hugging Face Transformers** (`sentence-transformers` utilizing the `all-MiniLM-L6-v2` model) for calculating deep semantic similarity scores (~500MB RAM overhead).
2. **spaCy NLP Models** (`en_core_web_md`) for Named Entity Recognition (NER) and high-accuracy grammatical part-of-speech parsing (~200MB RAM overhead).
3. **Layout Rendering Runtimes** (`WeasyPrint` dependencies) for PDF report compiling.

Altogether, the active runtime requires **800MB – 1.2GB of RAM** to parse, load, and execute. Because traditional platforms like Render limit free tiers to **512MB RAM**, hosting there was technically impossible.

### The Scalable Solution: AWS EC2 + Native Systemd / Docker
To provide a production-ready environment on a budget, I transitioned the deployment architecture to **AWS EC2** using a `t3.micro` instance (eligible for the **AWS Free Tier**). 

By implementing **Virtual SSD Swap Space (2GB)**, I successfully gave my server a massive memory overhead buffer. This allows the lightweight, high-performance host to handle heavy ML weight loading and heavy parsing operations flawlessly—combining enterprise reliability with $0 deployment costs.

---

## 🛠️ Key Technical Features

* **Semantic Similarity Scorer**: Employs deep transformer embeddings to match the semantic meaning of resume experience against job specifications, bypassing generic keyword-stuffing hacks.
* **Granular Score Breakdown**: Generates comprehensive scores spanning Content, Formatting, Keywords, Skill Validation, and overall ATS Compatibility.
* **Intelligent PDF/DOCX Parsing**: Parses raw document assets with structured, error-resistant layout extractors.
* **Document Generation System**: Dynamically compiles structured, styled PDF analytical feedback summaries via WeasyPrint.
* **Auto-Scaling Backend**: Built using FastAPI with async lifecycle management, auto-documentation (`/docs`), and full CORS authorization.

---

## 💻 Local Development Setup

To run both the frontend and backend applications on your local workstation:

### Prerequisites
* Python 3.10 or 3.11 installed
* Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ehsaan08-ai/HireMind.git
cd HireMind
```

### Step 2: Setup the Backend
1. Open a new terminal in the `HireMind` root folder.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. Install dependencies and download spaCy NLP libraries:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_md
   python -m spacy download en_core_web_sm
   ```
4. Create a `.env` file in the root folder and add your API credentials:
   ```ini
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   GROQ_API_KEY=your_groq_api_key
   ```
5. Start the backend server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
The backend API documentation will now be interactive at `http://localhost:8000/docs`.

### Step 3: Setup the Frontend
1. Open a second terminal window and activate the virtual environment:
   ```bash
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
2. Launch the Streamlit application:
   ```bash
   streamlit run frontend/streamlit_app.py
   ```
The frontend will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Production Deployment on AWS EC2

The project comes with a completely automated native host-installer script (**[deploy.sh](deploy.sh)**) that configures the application to run continuously as a background system daemon on an Ubuntu EC2 instance.

### Step 1: Launch an Ubuntu EC2 Instance
1. Launch a **t3.micro** or **t3.small** instance running **Ubuntu 24.04 LTS**.
2. Under **Security Groups**, configure inbound rules to allow:
   * Port `22` (SSH)
   * Port `80` (HTTP)
   * Port `443` (HTTPS)
   * Port `8000` (FastAPI Custom TCP)

### Step 2: Configure Virtual RAM (Swap Space) on the Instance
Connect to your EC2 instance via SSH and allocate swap space (to prevent PyTorch/spaCy loading from crashing the low-RAM server):
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Step 3: Run the Automated Deployer
1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com/Ehsaan08-ai/HireMind.git
   cd HireMind
   ```
2. Create your `.env` file containing your Supabase and Groq keys:
   ```bash
   nano .env
   # Paste your environment variables and save (Ctrl+O -> Enter -> Ctrl+X)
   ```
3. Make the automated script executable and run it:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Managing the Running Service
The deployer configures a standard Linux `systemd` background daemon to keep your app alive 24/7. Use these commands to manage it:

* **View live server logs**: `sudo journalctl -u hiremind -f`
* **Restart the backend service**: `sudo systemctl restart hiremind`
* **Stop the backend service**: `sudo systemctl stop hiremind`
