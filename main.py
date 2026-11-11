import os
import time
from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM
from dotenv import load_dotenv

# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES & KEY ROTATION
# ==========================================
load_dotenv()

# Multi-key fallback and rotation strategy
API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY"),
]
# Filter out empty or None values
API_KEYS = [key for key in API_KEYS if key]

if not API_KEYS:
    raise ValueError(
        "Please add at least GOOGLE_API_KEY or GOOGLE_API_KEY_1 to your .env file."
    )

# Initialize primary active key
active_api_key = API_KEYS[0]
os.environ["GOOGLE_API_KEY"] = active_api_key


# ==========================================
# 2. INITIALIZE LLM (Gemini via CrewAI)
# ==========================================
gemini_llm = LLM(
    model="gemini/gemini-3.6-flash",  # Active stable model identifier
    temperature=0.2,  # Low temperature for precise financial logic
    timeout=120,
    max_retries=3,
)


# ==========================================
# 3. DEFINE FINANCE-FOCUSED AGENTS (The FinTech Dev Team)
# ==========================================

planner_agent = Agent(
    role="FinTech Financial Systems Architect",
    goal="Analyze financial calculation requirements and create a concise technical blueprint for financial metrics.",
    backstory=(
        "You are an expert financial system architect holding an MBA and M.Phil in Finance, "
        "specializing in automated corporate finance workflows, liquidity ratios, and credit risk models."
    ),
    verbose=True,
    llm=gemini_llm,
)

developer_agent = Agent(
    role="Quantitative Python Developer",
    goal="Write clean, modular, and accurate Python code implementing financial formulas (ratios, cash flows, and risk scoring).",
    backstory=(
        "You are a master Python developer experienced in building financial calculation modules "
        "adhering strictly to PEP 8 standards and financial accounting principles."
    ),
    verbose=True,
    llm=gemini_llm,
)

tester_agent = Agent(
    role="Financial QA Test Engineer",
    goal="Create concise unit tests to verify financial calculations, boundary cases, and division-by-zero handling.",
    backstory=(
        "You are a meticulous QA engineer who ensures financial software absolute accuracy "
        "by writing thorough unit tests using Python's unittest framework for monetary computations."
    ),
    verbose=True,
    llm=gemini_llm,
)

reviewer_agent = Agent(
    role="Senior Financial Code Reviewer & Risk Auditor",
    goal="Review financial code and test cases for accounting logic errors, rounding discrepancies, or security flaws.",
    backstory=(
        "You are a strict code reviewer with a deep background in financial auditing, risk management, "
        "and numerical stability in software."
    ),
    verbose=True,
    llm=gemini_llm,
)

reporter_agent = Agent(
    role="Lead Financial Technologist & Technical Writer",
    goal="Compile the final verified financial Python code and a professional executive risk assessment report.",
    backstory=(
        "You are a technical lead bridging finance and software engineering, responsible for producing "
        "polished executive deliverables and deployment manuals."
    ),
    verbose=True,
    llm=gemini_llm,
)


# ==========================================
# 4. DEFINE TASKS (With Token Efficiency & Disk Outputs)
# ==========================================

planning_task = Task(
    description=(
        "Analyze the following FinTech software requirement: '{requirement}'. "
        "Produce a concise technical implementation plan outlining modules for financial statement parsing, "
        "ratio computation (Current Ratio, Debt-to-Equity, ROE), and credit scoring. Keep sections brief."
    ),
    expected_output="A structured markdown document containing the financial software architecture and implementation plan.",
    agent=planner_agent,
    output_file="1_finance_implementation_plan.md",
)

coding_task = Task(
    description=(
        "Using the financial implementation plan provided, write the complete, functional Python module "
        "that computes financial ratios and credit risk scores cleanly and accurately."
    ),
    expected_output="Production-ready Python code blocks with proper financial formulas, comments, and docstrings.",
    agent=developer_agent,
    output_file="2_financial_code.py",
)

testing_task = Task(
    description=(
        "Review the generated financial Python code and write robust unit tests covering standard financial datasets, "
        "edge cases (e.g., zero equity, negative cash flows), and invalid inputs using unittest."
    ),
    expected_output="A clean set of unit test cases using Python's unittest framework.",
    agent=tester_agent,
    output_file="3_financial_test_cases.py",
)

review_task = Task(
    description=(
        "Evaluate the generated financial code and test cases for accounting accuracy, numerical edge cases, "
        "and code hygiene. Provide concrete recommendations."
    ),
    expected_output="A concise code review report listing financial logic checks and optimization suggestions.",
    agent=reviewer_agent,
    output_file="4_financial_code_review.md",
)

reporting_task = Task(
    description=(
        "Synthesize all previous outputs into a final executive FinTech development report summarizing the financial calculation tool."
    ),
    expected_output="A final comprehensive executive report containing deployment instructions, formula summaries, and test results.",
    agent=reporter_agent,
    output_file="5_final_fintech_development_report.md",
)


# ==========================================
# 5. ASSEMBLE THE CREW
# ==========================================

fintech_crew = Crew(
    agents=[
        planner_agent,
        developer_agent,
        tester_agent,
        reviewer_agent,
        reporter_agent,
    ],
    tasks=[
        planning_task,
        coding_task,
        testing_task,
        review_task,
        reporting_task,
    ],
    process=Process.sequential,
    verbose=True,
)


# ==========================================
# 6. RESILIENT EXECUTION WITH KEY ROTATION & BACKOFF
# ==========================================
if __name__ == "__main__":
    user_requirement = (
        "Build a Python command-line utility and module for corporate finance analysis that: "
        "1) Computes key liquidity ratios (Current Ratio, Quick Ratio) and solvency ratios (Debt-to-Equity). "
        "2) Calculates Return on Equity (ROE) using DuPont analysis components. "
        "3) Computes an automated Credit Risk Score based on threshold criteria. "
        "4) Handles missing data and division-by-zero gracefully with custom exceptions."
    )

    max_attempts = len(API_KEYS)
    success = False

    print(
        "### Starting FinTech Multi-Agent Software Development Workflow ###"
    )

    for attempt in range(max_attempts):
        try:
            # Rotate key if multiple attempts occur
            current_key = API_KEYS[attempt % len(API_KEYS)]
            os.environ["GOOGLE_API_KEY"] = current_key
            print(
                f"\n[Attempt {attempt + 1}/{max_attempts}] Executing FinTech crew workflow with active API key..."
            )

            result = fintech_crew.kickoff(inputs={"requirement": user_requirement})

            success = True
            print("\n\n########################################")
            print("## FINTECH WORKFLOW COMPLETED SUCCESSFULLY! ##")
            print(
                "## Artifacts saved directly to disk: 1_finance_implementation_plan.md, 2_financial_code.py, etc. ##"
            )
            print("########################################\n")
            break

        except Exception as e:
            print(f"\n[Warning] Execution failed on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                backoff_delay = (attempt + 1) * 5  # Incremental backoff delay
                print(
                    f"Retrying with rotated API key after {backoff_delay} seconds backoff..."
                )
                time.sleep(backoff_delay)
            else:
                print(
                    "\n[Error] All API keys and retry attempts exhausted. Please check rate limits or network connection."
                )
                raise e