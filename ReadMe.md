# FinTech Multi-Agent Software Development System

An automated multi-agent AI system built using **CrewAI** and **Google Gemini** that simulates a specialized FinTech software development team. It takes corporate finance requirements and autonomously plans, develops, tests, audits, and documents a robust financial analysis module.

---

## 👥 The Multi-Agent Team Architecture

1. **FinTech Financial Systems Architect:** Analyzes financial calculation requirements and creates technical blueprints for metrics (Liquidity, Solvency, DuPont ROE, and Credit Risk).
2. **Quantitative Python Developer:** Writes clean, modular, and accurate Python code implementing corporate finance formulas adhering to PEP 8 standards.
3. **Financial QA Test Engineer:** Creates rigorous unit tests verifying financial computations, edge cases, and division-by-zero handling using Python's `unittest`.
4. **Senior Financial Code Reviewer & Risk Auditor:** Evaluates code and test cases for accounting logic errors, numerical stability, and code hygiene.
5. **Lead Financial Technologist & Technical Writer:** Compiles final verified code and produces the executive financial software report.

---

## 🚀 Key Features & Output Artifacts

The system executes sequentially and automatically generates clean artifacts directly to disk:
* `1_finance_implementation_plan.md`: System architecture and technical blueprint.
* `2_financial_code.py`: Production-ready Python module for financial calculations.
* `3_financial_test_cases.py`: Comprehensive test suite using `unittest`.
* `4_financial_code_review.md`: Code audit report and recommendations.
* `5_final_fintech_development_report.md`: Executive summary and operational deployment manual.

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fintech-multi-agent-system.git
   cd fintech-multi-agent-system
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install crewai "crewai[google-genai]" python-dotenv
   ```

4. **Configure your environment variables:**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_google_ai_studio_api_key_here
   ```

---

## ▶️ Usage

Run the multi-agent orchestrator script:
```bash
python main.py
```

---

## 🛠️ Tech Stack
* **Python 3.11+**
* **CrewAI Framework**
* **Google Gemini (gemini-3.6-flash)**
* **LiteLLM**