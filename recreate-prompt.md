# Recreate Prompt: AI Interview Taker MVP (Phase 1 Skeleton)

Paste the prompt below into any AI coding assistant to recreate the current state of the project.

---

## PROMPT START

Please create an MVP of an AI Interview Taker app (Phase 1 Skeleton with mock data) using a FastAPI Python backend and a React (Vite) frontend. The frontend uses Tailwind CSS, Framer Motion, and custom-coded Aceternity UI components.

Set up the project structure exactly as outlined below:

### 1. Project Directory Layout

Ensure the workspace has the following folders and files:
```
ai-interviewer/
├── backend/
│   ├── .env.example
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── components/
│       │   └── ui/
│       │       ├── GlowingCard.jsx
│       │       ├── GridBackground.jsx
│       │       ├── HoverBorderGradient.jsx
│       │       └── MultiStepLoader.jsx
│       └── lib/
│           └── utils.js
└── README.md
```

---

### 2. Backend Implementation (FastAPI)

#### File: `backend/requirements.txt`
```text
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.4
anthropic==0.28.1
python-dotenv==1.0.1
```

#### File: `backend/.env.example`
```env
# Anthropic Claude API Key (required for LLM integration)
ANTHROPIC_API_KEY=
```

#### File: `backend/main.py`
```python
import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="AI Interview Taker MVP API")

# Enable CORS for frontend local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions = {}

# Mock questions for different combinations
MOCK_QUESTIONS_POOL = {
    ("Frontend", "React"): [
        "What is the purpose of state in React, and how does it differ from props?",
        "What are React Hooks, and what rules must you follow when using them?",
        "Explain the Virtual DOM and how React reconciles updates to the real DOM.",
        "How does the useEffect hook work, and how do you clean up side effects in it?",
        "What is the difference between controlled and uncontrolled components in React?"
    ],
    ("Frontend", "JavaScript"): [
        "What is the difference between 'let', 'const', and 'var' in JavaScript?",
        "Explain the concept of closures in JavaScript and provide a practical use case.",
        "What is the difference between '==' and '===' operators in JavaScript?",
        "Explain how the JavaScript Event Loop works and how it handles asynchronous operations.",
        "What are Promises, and how do they compare to async/await syntax?"
    ],
    ("Frontend", "CSS"): [
        "What is the difference between Flexbox and CSS Grid layout systems?",
        "Explain the CSS Box Model and how 'box-sizing: border-box' affects it.",
        "What are CSS custom properties (variables) and how do they differ from preprocessor variables?",
        "Explain CSS specificity and how the cascade determines styling application rules.",
        "What is the purpose of media queries and how do you implement mobile-first design?"
    ],
    ("Backend", "Node.js"): [
        "Explain the single-threaded event loop architecture of Node.js.",
        "What is the difference between 'require' (CommonJS) and 'import' (ES Modules) in Node.js?",
        "How does middleware work in Express, and what is its role in request processing?",
        "What is the difference between stream-based and buffer-based file processing in Node.js?",
        "Explain how error handling is typically implemented in asynchronous Node.js operations."
    ],
    ("Backend", "Databases"): [
        "What is the difference between SQL and NoSQL databases, and when would you use each?",
        "Explain the ACID properties of relational database transactions.",
        "What is database indexing, and how does it improve query performance? Are there downsides?",
        "Explain the difference between inner join, left join, and outer join in SQL.",
        "What is database normalization, and why is it important in relational database design?"
    ]
}

DEFAULT_MOCK_QUESTIONS = [
    "What is the primary technical concept behind this topic, and why is it important?",
    "Explain a common problem or challenge associated with this topic and how you would solve it.",
    "Describe the difference between two competing approaches or features in this area.",
    "How do you optimize or write efficient code/systems related to this topic?",
    "Explain how you would debug or troubleshoot an issue related to this topic."
]

# Request/Response Pydantic Models
class StartInterviewRequest(BaseModel):
    subject: str
    topic: str
    difficulty: str

class StartInterviewResponse(BaseModel):
    session_id: str
    question: str
    question_number: int
    total_questions: int

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str

class SubmitAnswerResponse(BaseModel):
    score: int
    feedback: str
    done: bool
    next_question: Optional[str] = None
    question_number: int
    total_questions: int

class QuestionDetail(BaseModel):
    question: str
    answer: str
    score: int
    feedback: str

class ResultsResponse(BaseModel):
    subject: str
    topic: str
    difficulty: str
    overall_score: float
    questions: List[QuestionDetail]


@app.post("/start-interview", response_model=StartInterviewResponse)
def start_interview(payload: StartInterviewRequest):
    session_id = str(uuid.uuid4())
    
    key = (payload.subject, payload.topic)
    questions = MOCK_QUESTIONS_POOL.get(key, DEFAULT_MOCK_QUESTIONS).copy()
    
    difficulty_prefix = f"[{payload.difficulty} level] "
    questions = [difficulty_prefix + q for q in questions]
    
    sessions[session_id] = {
        "subject": payload.subject,
        "topic": payload.topic,
        "difficulty": payload.difficulty,
        "current_index": 0,
        "questions": questions,
        "qa_log": []
    }
    
    return StartInterviewResponse(
        session_id=session_id,
        question=questions[0],
        question_number=1,
        total_questions=5
    )


@app.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest):
    session_id = payload.session_id
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = sessions[session_id]
    current_index = session["current_index"]
    questions = session["questions"]
    
    if current_index >= 5:
        raise HTTPException(status_code=400, detail="Interview is already completed")
        
    current_question = questions[current_index]
    
    answer_len = len(payload.answer.strip())
    if answer_len == 0:
        score = 0
        feedback = "You did not provide an answer. Please attempt the question next time to receive credit."
    elif answer_len < 15:
        score = 4
        feedback = f"Your answer is too short. At the {session['difficulty']} difficulty level, we expect a more detailed explanation of the concepts."
    else:
        score = 6 + (answer_len % 5)
        score = min(score, 10)
        feedback = (
            f"Good effort. Your response correctly identifies some core aspects. "
            f"Under {session['difficulty']} criteria, you could improve by elaborating on edge cases and deep-dive mechanics."
        )
        
    session["qa_log"].append({
        "question": current_question,
        "answer": payload.answer,
        "score": score,
        "feedback": feedback
    })
    
    session["current_index"] += 1
    next_index = session["current_index"]
    done = next_index >= 5
    
    next_question = None
    if not done:
        next_question = questions[next_index]
        
    return SubmitAnswerResponse(
        score=score,
        feedback=feedback,
        done=done,
        next_question=next_question,
        question_number=next_index + 1 if not done else 5,
        total_questions=5
    )


@app.get("/results/{session_id}", response_model=ResultsResponse)
def get_results(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = sessions[session_id]
    qa_log = session["qa_log"]
    
    if len(qa_log) == 0:
        overall_score = 0.0
    else:
        overall_score = round(sum(q["score"] for q in qa_log) / len(qa_log), 1)
        
    return ResultsResponse(
        subject=session["subject"],
        topic=session["topic"],
        difficulty=session["difficulty"],
        overall_score=overall_score,
        questions=[
            QuestionDetail(
                question=q["question"],
                answer=q["answer"],
                score=q["score"],
                feedback=q["feedback"]
            )
            for q in qa_log
        ]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

---

### 3. Frontend Implementation (React Vite + Tailwind + Framer Motion)

Initialize the React application in the `frontend` folder using `vite`. Ensure the following dependencies are installed:
- `tailwindcss@3.4.15`
- `postcss`
- `autoprefixer`
- `framer-motion`
- `lucide-react`
- `tailwind-merge`
- `clsx`

Create the configuration and source files listed below:

#### File: `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "var(--border)",
      },
      animation: {
        "shimmer": "shimmer 2s linear infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "first": "moveVertical 30s ease infinite",
        "second": "moveInCircle 20s ease infinite",
        "third": "moveInCircle 40s ease infinite",
        "fourth": "moveHorizontal 40s ease infinite",
        "fifth": "moveInCircle 20s ease infinite",
      },
      keyframes: {
        shimmer: {
          from: {
            backgroundPosition: "0 0",
          },
          to: {
            backgroundPosition: "-200% 0",
          },
        },
        moveVertical: {
          "0%": {
            transform: "translateY(-50%)",
          },
          "50%": {
            transform: "translateY(50%)",
          },
          "100%": {
            transform: "translateY(-50%)",
          },
        },
        moveInCircle: {
          "0%": {
            transform: "rotate(0deg)",
          },
          "50%": {
            transform: "rotate(180deg)",
          },
          "100%": {
            transform: "rotate(360deg)",
          },
        },
        moveHorizontal: {
          "0%": {
            transform: "translateX(-50%) translateY(-10%)",
          },
          "50%": {
            transform: "translateX(50%) translateY(10%)",
          },
          "100%": {
            transform: "translateX(-50%) translateY(-10%)",
          },
        },
      },
    },
  },
  plugins: [],
}
```

#### File: `frontend/postcss.config.js`
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

#### File: `frontend/src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --background: 240 10% 3.9%;
  --foreground: 0 0% 98%;
  --border: 240 3.7% 15.9%;
}

body {
  background-color: #030303;
  color: #fafafa;
  font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
  margin: 0;
  padding: 0;
  min-height: 100vh;
  overflow-x: hidden;
}

::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #09090b;
}
::-webkit-scrollbar-thumb {
  background: #27272a;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #3f3f46;
}

.glass-panel {
  background: rgba(15, 15, 20, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

#### File: `frontend/src/App.css`
```css
/* App.css reset to prevent style conflicts */
```

#### File: `frontend/src/lib/utils.js`
```javascript
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
```

#### File: `frontend/src/components/ui/GridBackground.jsx`
```jsx
import React from "react";

export function GridBackground({ children }) {
  return (
    <div className="min-h-screen w-full bg-[#030303] relative flex flex-col items-center justify-start antialiased overflow-x-hidden">
      {/* Background Grid Lines */}
      <div 
        className="absolute inset-0 z-0 bg-[linear-gradient(to_right,#16161d_1px,transparent_1px),linear-gradient(to_bottom,#16161d_1px,transparent_1px)] bg-[size:3rem_3rem] [mask-image:radial-gradient(ellipse_60%_60%_at_50%_50%,#000_50%,transparent_100%)] opacity-70"
      />
      
      {/* Radial soft background ambient glow */}
      <div className="absolute top-[-10%] left-[20%] w-[60%] h-[40%] rounded-full bg-gradient-to-r from-indigo-500/10 to-purple-500/10 blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-[-10%] left-[10%] w-[50%] h-[55%] rounded-full bg-blue-500/5 blur-[150px] pointer-events-none z-0" />

      <div className="relative z-10 w-full flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}
```

#### File: `frontend/src/components/ui/HoverBorderGradient.jsx`
```jsx
import React, { useState } from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

export function HoverBorderGradient({
  children,
  containerClassName,
  className,
  as: Component = "button",
  duration = 1.5,
  clockwise = true,
  disabled = false,
  ...props
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <Component
      onMouseEnter={() => !disabled && setHovered(true)}
      onMouseLeave={() => !disabled && setHovered(false)}
      disabled={disabled}
      className={cn(
        "relative flex rounded-xl content-center transition-all duration-300 items-center justify-center p-[1px] overflow-hidden focus:outline-none focus:ring-2 focus:ring-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed",
        disabled ? "bg-zinc-800 border border-zinc-700/50" : "bg-zinc-800/50 border border-white/10 hover:border-transparent",
        containerClassName
      )}
      {...props}
    >
      <div
        className={cn(
          "w-full text-zinc-100 z-10 px-6 py-3 rounded-[11px] font-medium transition-colors duration-300",
          disabled ? "bg-zinc-900/40 text-zinc-500" : "bg-zinc-950/90 group-hover:bg-zinc-950/40",
          className
        )}
      >
        {children}
      </div>
      {!disabled && (
        <motion.div
          className="absolute inset-0 z-0 bg-[conic-gradient(from_0deg,transparent_40%,#6366f1_70%,#a855f7_90%,transparent_100%)]"
          initial={{ rotate: 0 }}
          animate={
            hovered
              ? { rotate: clockwise ? 360 : -360 }
              : { rotate: 0 }
          }
          transition={{
            duration: duration,
            repeat: Infinity,
            ease: "linear",
          }}
          style={{
            width: "300%",
            height: "300%",
            left: "-100%",
            top: "-100%",
          }}
        />
      )}
    </Component>
  );
}
```

#### File: `frontend/src/components/ui/GlowingCard.jsx`
```jsx
import React from "react";
import { cn } from "../../lib/utils";

export function GlowingCard({ children, className, containerClassName }) {
  return (
    <div 
      className={cn(
        "relative group rounded-2xl p-[1px] bg-gradient-to-b from-zinc-800/80 to-zinc-900/80 border border-white/5 transition-all duration-300 hover:border-zinc-700/80",
        containerClassName
      )}
    >
      {/* Background hover glowing gradient */}
      <div 
        className="absolute inset-0 rounded-2xl bg-gradient-to-r from-indigo-500/15 via-purple-500/10 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl pointer-events-none" 
      />
      
      {/* Inner card content wrapper */}
      <div 
        className={cn(
          "relative z-10 glass-panel rounded-2xl p-6 h-full flex flex-col justify-start overflow-hidden",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}
```

#### File: `frontend/src/components/ui/MultiStepLoader.jsx`
```jsx
import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

const DEFAULT_STEPS = [
  { text: "Capturing your submission..." },
  { text: "Analyzing language structure..." },
  { text: "Evaluating grading criteria..." },
  { text: "Calculating final score..." },
  { text: "Generating custom feedback..." }
];

export function MultiStepLoader({ loading, steps = DEFAULT_STEPS }) {
  const [currentState, setCurrentState] = useState(0);

  useEffect(() => {
    if (!loading) {
      setCurrentState(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentState((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 700);

    return () => clearInterval(interval);
  }, [loading, steps.length]);

  return (
    <AnimatePresence mode="wait">
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/85 backdrop-blur-md"
        >
          <div className="w-full max-w-md p-6 flex flex-col items-start justify-center relative">
            <h3 className="text-zinc-400 text-xs tracking-wider uppercase mb-6 font-mono font-semibold">
              Evaluation In Progress
            </h3>

            <div className="space-y-6">
              {steps.map((step, index) => {
                const isCompleted = index < currentState;
                const isLoading = index === currentState;
                const isPending = index > currentState;

                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 text-left"
                  >
                    <div className="w-6 h-6 flex items-center justify-center shrink-0">
                      {isCompleted && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="bg-emerald-500 rounded-full p-1"
                        >
                          <Check className="w-3.5 h-3.5 text-black stroke-[3px]" />
                        </motion.div>
                      )}
                      {isLoading && (
                        <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
                      )}
                      {isPending && (
                        <div className="w-2.5 h-2.5 bg-zinc-700 rounded-full" />
                      )}
                    </div>
                    
                    <span
                      className={cn(
                        "text-sm font-medium transition-colors duration-300",
                        isCompleted && "text-zinc-400 line-through decoration-zinc-700/50",
                        isLoading && "text-zinc-100 font-semibold",
                        isPending && "text-zinc-600"
                      )}
                    >
                      {step.text}
                    </span>
                  </motion.div>
                );
              })}
            </div>
            
            {/* Visual Progress Line */}
            <div className="w-full bg-zinc-800 h-[2px] mt-10 rounded-full overflow-hidden">
              <motion.div 
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full"
                animate={{ width: `${((currentState + 1) / steps.length) * 100}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

#### File: `frontend/src/App.jsx`
```jsx
import React, { useState, useEffect } from "react";
import { 
  Brain, 
  Play, 
  Send, 
  RefreshCw, 
  Award, 
  AlertCircle, 
  ChevronRight,
  BookOpen,
  HelpCircle,
  MessageSquare
} from "lucide-react";
import { GridBackground } from "./components/ui/GridBackground";
import { HoverBorderGradient } from "./components/ui/HoverBorderGradient";
import { GlowingCard } from "./components/ui/GlowingCard";
import { MultiStepLoader } from "./components/ui/MultiStepLoader";

const API_BASE = "http://127.0.0.1:8000";

const SUBJECTS_TOPICS = {
  Frontend: ["React", "JavaScript", "CSS"],
  Backend: ["Node.js", "Databases"]
};

export default function App() {
  const [screen, setScreen] = useState("setup");
  
  const [subject, setSubject] = useState("Frontend");
  const [topic, setTopic] = useState("React");
  const [difficulty, setDifficulty] = useState("Medium");
  
  const [sessionId, setSessionId] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [answerText, setAnswerText] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  
  const [results, setResults] = useState(null);

  useEffect(() => {
    const topics = SUBJECTS_TOPICS[subject];
    if (topics && !topics.includes(topic)) {
      setTopic(topics[0]);
    }
  }, [subject]);

  const handleStartInterview = async () => {
    setErrorMsg("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/start-interview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, topic, difficulty })
      });
      
      if (!response.ok) {
        throw new Error("Failed to start session. Make sure the backend server is running.");
      }
      
      const data = await response.json();
      setSessionId(data.session_id);
      setCurrentQuestion(data.question);
      setQuestionNumber(data.question_number);
      setTotalQuestions(data.total_questions);
      setAnswerText("");
      setScreen("interview");
    } catch (err) {
      setErrorMsg(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answerText.trim()) {
      setErrorMsg("Answer cannot be empty.");
      return;
    }
    
    setErrorMsg("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/submit-answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, answer: answerText })
      });
      
      if (!response.ok) {
        throw new Error("Failed to submit answer. Please try again.");
      }
      
      const data = await response.json();
      
      if (data.done) {
        await fetchResults();
      } else {
        setCurrentQuestion(data.next_question);
        setQuestionNumber(data.question_number);
        setTotalQuestions(data.total_questions);
        setAnswerText("");
      }
    } catch (err) {
      setErrorMsg(err.message || "An error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/results/${sessionId}`);
      if (!response.ok) {
        throw new Error("Failed to retrieve interview results.");
      }
      const data = await response.json();
      setResults(data);
      setScreen("results");
    } catch (err) {
      setErrorMsg(err.message || "An error occurred fetching results.");
    }
  };

  const handleRestart = () => {
    setScreen("setup");
    setSessionId("");
    setCurrentQuestion("");
    setQuestionNumber(1);
    setAnswerText("");
    setResults(null);
    setErrorMsg("");
  };

  return (
    <GridBackground>
      <header className="w-full max-w-6xl mx-auto px-6 py-6 flex items-center justify-between border-b border-white/5 relative z-10">
        <div className="flex items-center gap-2.5 cursor-pointer" onClick={handleRestart}>
          <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <Brain className="w-6 h-6 animate-pulse-slow" />
          </div>
          <div>
            <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
              InterviewerAI
            </h1>
            <p className="text-[10px] text-zinc-500 font-mono tracking-wider uppercase font-semibold">
              MVP Phase 1
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span className="text-xs font-mono text-zinc-400">System Ready</span>
        </div>
      </header>

      <main className="w-full max-w-4xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center relative z-10">
        {errorMsg && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-red-400 animate-in fade-in slide-in-from-top-2">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">Action Failed</h4>
              <p className="text-xs opacity-90 mt-0.5">{errorMsg}</p>
            </div>
          </div>
        )}

        {screen === "setup" && (
          <div className="max-w-xl mx-auto w-full space-y-8 animate-in fade-in duration-500">
            <div className="text-center space-y-3">
              <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-b from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
                Configure Your Session
              </h2>
              <p className="text-zinc-400 text-sm max-w-sm mx-auto">
                Set your path, test your skills, and receive instant generative grading and feedback.
              </p>
            </div>

            <GlowingCard>
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
                    <BookOpen className="w-3.5 h-3.5" /> Subject
                  </label>
                  <select
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                  >
                    {Object.keys(SUBJECTS_TOPICS).map((sub) => (
                      <option key={sub} value={sub}>{sub}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
                    <HelpCircle className="w-3.5 h-3.5" /> Topic
                  </label>
                  <select
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                  >
                    {SUBJECTS_TOPICS[subject]?.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">
                    <Award className="w-3.5 h-3.5" /> Difficulty
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition"
                  >
                    <option value="Easy">Easy (Lenient Grading)</option>
                    <option value="Medium">Medium (Balanced Grading)</option>
                    <option value="Hard">Hard (Strict Grading)</option>
                  </select>
                </div>

                <div className="pt-2">
                  <HoverBorderGradient 
                    onClick={handleStartInterview} 
                    containerClassName="w-full"
                    disabled={loading}
                  >
                    <span className="flex items-center justify-center gap-2">
                      <Play className="w-4 h-4 fill-current" /> Start Interview Session
                    </span>
                  </HoverBorderGradient>
                </div>
              </div>
            </GlowingCard>
          </div>
        )}

        {screen === "interview" && (
          <div className="max-w-2xl mx-auto w-full space-y-6 animate-in fade-in duration-300">
            <div className="flex flex-wrap items-center justify-between gap-4 bg-zinc-900/40 px-5 py-3 rounded-2xl border border-white/5">
              <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-medium">
                <span>{subject}</span>
                <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                <span>{topic}</span>
                <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                <span className="text-indigo-400 font-semibold">{difficulty}</span>
              </div>
              <span className="text-xs font-mono font-bold bg-zinc-800 text-zinc-300 px-3 py-1 rounded-full border border-white/5">
                Question {questionNumber} of {totalQuestions}
              </span>
            </div>

            <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden border border-white/5">
              <div 
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-500" 
                style={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
              />
            </div>

            <GlowingCard>
              <div className="space-y-6">
                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-500 font-mono">
                    Question Prompt
                  </h3>
                  <p className="text-lg font-bold text-zinc-100 leading-relaxed">
                    {currentQuestion}
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-zinc-500 font-mono flex items-center gap-1.5">
                    <MessageSquare className="w-3.5 h-3.5" /> Your Answer
                  </label>
                  <textarea
                    rows={6}
                    value={answerText}
                    onChange={(e) => setAnswerText(e.target.value)}
                    placeholder="Type your comprehensive explanation here..."
                    className="w-full bg-zinc-900/80 border border-white/10 rounded-xl p-4 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition placeholder-zinc-600 leading-relaxed resize-none"
                  />
                </div>

                <div className="flex justify-end pt-2">
                  <HoverBorderGradient 
                    onClick={handleSubmitAnswer}
                    disabled={!answerText.trim() || loading}
                    containerClassName="w-full sm:w-auto"
                  >
                    <span className="flex items-center justify-center gap-2">
                      <Send className="w-4 h-4" /> Submit Answer
                    </span>
                  </HoverBorderGradient>
                </div>
              </div>
            </GlowingCard>
            
            <MultiStepLoader loading={loading} />
          </div>
        )}

        {screen === "results" && results && (
          <div className="w-full space-y-8 animate-in fade-in duration-500">
            <GlowingCard containerClassName="w-full">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-1.5 text-xs text-zinc-400 font-medium">
                    <span>{results.subject}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                    <span>{results.topic}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                    <span className="text-indigo-400 font-semibold">{results.difficulty}</span>
                  </div>
                  <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-b from-zinc-100 to-zinc-400 bg-clip-text text-transparent">
                    Interview Evaluation Report
                  </h2>
                  <p className="text-xs text-zinc-500">
                    Calculated using generative strictness models matching {results.difficulty} difficulty.
                  </p>
                </div>

                <div className="flex items-center gap-4 bg-zinc-900/60 p-4 rounded-2xl border border-white/5 shrink-0">
                  <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400">
                    <Award className="w-8 h-8" />
                  </div>
                  <div>
                    <p className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-wider">
                      Overall Score
                    </p>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-3xl font-extrabold font-mono ${results.overall_score >= 7.0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                        {results.overall_score.toFixed(1)}
                      </span>
                      <span className="text-zinc-600 text-sm font-semibold">/ 10.0</span>
                    </div>
                  </div>
                </div>
              </div>
            </GlowingCard>

            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-500 font-mono pl-1">
                Question Breakdown
              </h3>
              
              {results.questions.map((q, idx) => {
                const isPassed = q.score >= 7;
                return (
                  <GlowingCard key={idx} containerClassName="w-full">
                    <div className="space-y-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-mono font-bold uppercase">
                            Question {idx + 1}
                          </p>
                          <h4 className="text-sm font-bold text-zinc-100 leading-snug">
                            {q.question}
                          </h4>
                        </div>
                        <div className={`shrink-0 px-3 py-1.5 rounded-xl border text-xs font-bold font-mono ${
                          isPassed 
                            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
                            : "bg-amber-500/10 border-amber-500/20 text-amber-400"
                        }`}>
                          Score: {q.score}/10
                        </div>
                      </div>

                      <div className="p-3.5 bg-zinc-900/50 rounded-xl border border-white/5 space-y-1.5">
                        <h5 className="text-[10px] text-zinc-500 font-mono font-bold uppercase tracking-wider">
                          Your Answer
                        </h5>
                        <p className="text-xs text-zinc-300 leading-relaxed font-mono whitespace-pre-wrap">
                          {q.answer || "(No response provided)"}
                        </p>
                      </div>

                      <div className="p-3.5 bg-zinc-900/30 rounded-xl border border-dashed border-white/5 space-y-1.5">
                        <h5 className="text-[10px] text-zinc-400 font-mono font-bold uppercase tracking-wider">
                          AI Evaluator Feedback
                        </h5>
                        <p className="text-xs text-zinc-400 leading-relaxed">
                          {q.feedback}
                        </p>
                      </div>
                    </div>
                  </GlowingCard>
                );
              })}
            </div>

            <div className="flex justify-center pt-4">
              <HoverBorderGradient onClick={handleRestart} containerClassName="w-full sm:w-auto">
                <span className="flex items-center justify-center gap-2">
                  <RefreshCw className="w-4 h-4" /> Start New Interview Session
                </span>
              </HoverBorderGradient>
            </div>
          </div>
        )}
      </main>
      
      <footer className="w-full max-w-6xl mx-auto px-6 py-6 text-center border-t border-white/5 mt-auto relative z-10">
        <p className="text-[11px] text-zinc-600 font-mono tracking-wider uppercase">
          Build for Scaler AI module • Powered by Anthropic Claude API
        </p>
      </footer>
    </GridBackground>
  );
}
```

#### File: `frontend/src/main.jsx`
```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

### 4. Running the Project

1. **Start the backend server:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 -m uvicorn main:app --reload --port 8000
   ```

2. **Start the frontend dev server:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Verify that the mock interview flows successfully from config setup through to the results panel.

## PROMPT END
