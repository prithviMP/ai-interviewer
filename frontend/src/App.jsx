import React, { useState, useEffect, useCallback } from "react";
import {
  Play,
  Send,
  RefreshCw,
  Award,
  AlertCircle,
  ChevronRight,
  BookOpen,
  HelpCircle,
  CheckCircle2,
  Circle,
  TrendingUp,
  FileText,
} from "lucide-react";
import { AuthForm } from "./components/AuthForm";
import { DashboardLayout } from "./components/DashboardLayout";
import { GlowingCard } from "./components/ui/GlowingCard";
import { HoverBorderGradient } from "./components/ui/HoverBorderGradient";
import { MultiStepLoader } from "./components/ui/MultiStepLoader";
import { apiFetch, clearAuth, getUser } from "./lib/auth";

const SUBJECTS_TOPICS = {
  Frontend: ["React Hooks", "JavaScript", "CSS", "TypeScript"],
  Backend: ["Node.js", "Databases", "API Design", "Authentication"],
  DevOps: ["Docker", "CI/CD", "Kubernetes"],
  Data: ["SQL", "Data Modeling", "ETL"],
};

export default function App() {
  const [user, setUser] = useState(getUser);
  const [view, setView] = useState("home");

  const [skillCategory, setSkillCategory] = useState("Frontend");
  const [topic, setTopic] = useState("React Hooks");
  const [difficulty, setDifficulty] = useState("Medium");
  const [experienceLevel, setExperienceLevel] = useState("Mid");
  const [assessmentType, setAssessmentType] = useState("Knowledge Check");
  const [learningObjectives, setLearningObjectives] = useState("");

  const [sessionId, setSessionId] = useState("");
  const [questions, setQuestions] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [results, setResults] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  const [history, setHistory] = useState([]);
  const [reports, setReports] = useState(null);
  const [selectedHistory, setSelectedHistory] = useState(null);

  useEffect(() => {
    const topics = SUBJECTS_TOPICS[skillCategory];
    if (topics && !topics.includes(topic)) setTopic(topics[0]);
  }, [skillCategory]);

  const loadReports = useCallback(async () => {
    try {
      const data = await apiFetch("/reports");
      setReports(data);
    } catch {
      /* ignore */
    }
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const data = await apiFetch("/history");
      setHistory(data);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    if (user && view === "home") loadReports();
    if (user && view === "history") loadHistory();
    if (user && view === "reports") loadReports();
  }, [user, view, loadReports, loadHistory]);

  const buildConfig = () => ({
    skill_category: skillCategory,
    topic,
    difficulty,
    experience_level: experienceLevel,
    assessment_type: assessmentType,
    learning_objectives: learningObjectives,
  });

  const handleStartAssessment = async () => {
    setErrorMsg("");
    setLoading(true);
    try {
      const data = await apiFetch("/assessments/generate", {
        method: "POST",
        body: JSON.stringify(buildConfig()),
      });
      setSessionId(data.session_id);
      setQuestions(data.questions);
      setQuestionIndex(0);
      setSelectedAnswer("");
      setQuestionStartTime(Date.now());
      setView("assessment");
    } catch (err) {
      setErrorMsg(err.message || "Failed to generate assessment.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer.trim()) {
      setErrorMsg("Please select an answer.");
      return;
    }
    setErrorMsg("");
    setLoading(true);
    const timeMs = Date.now() - questionStartTime;
    try {
      const data = await apiFetch(`/assessments/${sessionId}/answer`, {
        method: "POST",
        body: JSON.stringify({ selected_answer: selectedAnswer, time_ms: timeMs }),
      });
      if (data.done) {
        await fetchResults();
      } else {
        setQuestionIndex((i) => i + 1);
        setSelectedAnswer("");
        setQuestionStartTime(Date.now());
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to submit answer.");
    } finally {
      setLoading(false);
    }
  };

  const fetchResults = async () => {
    try {
      const [resultsData, feedbackData] = await Promise.all([
        apiFetch(`/assessments/${sessionId}/results`),
        apiFetch(`/assessments/${sessionId}/feedback`, { method: "POST" }).catch(() => null),
      ]);
      setResults(resultsData);
      setFeedback(feedbackData);
      await apiFetch("/history", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId }),
      }).catch(() => null);
      setView("results");
      loadReports();
    } catch (err) {
      setErrorMsg(err.message || "Failed to load results.");
    }
  };

  const handleNewTest = () => {
    setSessionId("");
    setQuestions([]);
    setQuestionIndex(0);
    setSelectedAnswer("");
    setResults(null);
    setFeedback(null);
    setErrorMsg("");
    setView("new-test");
  };

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    setView("home");
  };

  const openHistoryDetail = async (id) => {
    try {
      const data = await apiFetch(`/history/${id}`);
      setSelectedHistory(data);
      setView("history-detail");
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  if (!user) {
    return <AuthForm onSuccess={setUser} />;
  }

  const currentQuestion = questions[questionIndex];
  const sidebarView = ["assessment", "results", "history-detail"].includes(view) ? "new-test" : view;

  return (
    <>
      <DashboardLayout
        user={user}
        activeView={sidebarView}
        onNavigate={(id) => {
          setErrorMsg("");
          if (id === "new-test") handleNewTest();
          else setView(id);
        }}
        onLogout={handleLogout}
      >
        {errorMsg && <ErrorAlert message={errorMsg} onDismiss={() => setErrorMsg("")} />}

        {view === "home" && (
          <div className="space-y-6 max-w-3xl">
            <GlowingCard>
              <h3 className="text-xl font-bold text-zinc-100 mb-1">Welcome back, {user.name}!</h3>
              <p className="text-sm text-zinc-400">Ready for your next AI-powered assessment?</p>
            </GlowingCard>
            <div className="grid sm:grid-cols-3 gap-4">
              <StatCard label="Total Tests" value={reports?.total_tests ?? 0} />
              <StatCard label="Average Score" value={`${reports?.average_score ?? 0}%`} />
              <StatCard label="Best Score" value={`${reports?.best_score ?? 0}%`} />
            </div>
            <HoverBorderGradient onClick={() => setView("new-test")} containerClassName="w-full sm:w-auto">
              <span className="flex items-center gap-2"><Play className="w-4 h-4 fill-current" /> Start New Test</span>
            </HoverBorderGradient>
          </div>
        )}

        {view === "new-test" && (
          <div className="max-w-xl space-y-6">
            <GlowingCard>
              <div className="space-y-5">
                <SelectField label="Skill Category" icon={<BookOpen className="w-3.5 h-3.5" />} value={skillCategory} onChange={setSkillCategory}>
                  {Object.keys(SUBJECTS_TOPICS).map((s) => <option key={s} value={s}>{s}</option>)}
                </SelectField>
                <SelectField label="Topic" icon={<HelpCircle className="w-3.5 h-3.5" />} value={topic} onChange={setTopic}>
                  {SUBJECTS_TOPICS[skillCategory]?.map((t) => <option key={t} value={t}>{t}</option>)}
                </SelectField>
                <SelectField label="Difficulty" icon={<Award className="w-3.5 h-3.5" />} value={difficulty} onChange={setDifficulty}>
                  {["Easy", "Medium", "Hard"].map((d) => <option key={d} value={d}>{d}</option>)}
                </SelectField>
                <SelectField label="Experience Level" icon={<Award className="w-3.5 h-3.5" />} value={experienceLevel} onChange={setExperienceLevel}>
                  {["Junior", "Mid", "Senior"].map((l) => <option key={l} value={l}>{l}</option>)}
                </SelectField>
                <SelectField label="Assessment Type" icon={<FileText className="w-3.5 h-3.5" />} value={assessmentType} onChange={setAssessmentType}>
                  {["Knowledge Check", "Interview Prep", "Certification"].map((t) => <option key={t} value={t}>{t}</option>)}
                </SelectField>
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono">Learning Objectives (optional)</label>
                  <textarea
                    value={learningObjectives}
                    onChange={(e) => setLearningObjectives(e.target.value)}
                    rows={2}
                    className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none resize-none"
                  />
                </div>
                <HoverBorderGradient onClick={handleStartAssessment} containerClassName="w-full" disabled={loading}>
                  <span className="flex items-center justify-center gap-2"><Play className="w-4 h-4 fill-current" /> Generate & Start</span>
                </HoverBorderGradient>
              </div>
            </GlowingCard>
          </div>
        )}

        {view === "assessment" && currentQuestion && (
          <AssessmentView
            skillCategory={skillCategory}
            topic={topic}
            difficulty={difficulty}
            questionIndex={questionIndex}
            totalQuestions={questions.length}
            currentQuestion={currentQuestion}
            selectedAnswer={selectedAnswer}
            setSelectedAnswer={setSelectedAnswer}
            loading={loading}
            onSubmit={handleSubmitAnswer}
          />
        )}

        {view === "results" && results && (
          <ResultsView results={results} feedback={feedback} onNewTest={handleNewTest} />
        )}

        {view === "history" && (
          <div className="space-y-3 max-w-2xl">
            {history.length === 0 && <p className="text-sm text-zinc-500">No tests yet. Start your first assessment!</p>}
            {history.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => openHistoryDetail(item.id)}
                className="w-full text-left"
              >
                <GlowingCard containerClassName="w-full hover:border-indigo-500/30 transition-colors cursor-pointer">
                  <div className="flex justify-between items-center gap-4">
                    <div>
                      <p className="text-sm font-bold text-zinc-100">{item.topic} · {item.skill_category}</p>
                      <p className="text-xs text-zinc-500">{new Date(item.completed_at).toLocaleString()}</p>
                    </div>
                    <span className="text-lg font-mono font-bold text-indigo-400">{item.accuracy_percent}%</span>
                  </div>
                </GlowingCard>
              </button>
            ))}
          </div>
        )}

        {view === "history-detail" && selectedHistory && (
          <ResultsView
            results={selectedHistory.results}
            feedback={selectedHistory.feedback}
            onNewTest={() => setView("history")}
            backLabel="Back to History"
          />
        )}

        {view === "reports" && (
          <div className="space-y-6 max-w-2xl">
            <div className="grid sm:grid-cols-3 gap-4">
              <StatCard label="Total Tests" value={reports?.total_tests ?? 0} icon={<FileText className="w-4 h-4" />} />
              <StatCard label="Average Score" value={`${reports?.average_score ?? 0}%`} icon={<TrendingUp className="w-4 h-4" />} />
              <StatCard label="Best Score" value={`${reports?.best_score ?? 0}%`} icon={<Award className="w-4 h-4" />} />
            </div>
            <GlowingCard>
              <h3 className="text-sm font-bold text-zinc-300 mb-4 uppercase font-mono">Recent Tests</h3>
              {(reports?.recent_tests ?? []).map((t) => (
                <div key={t.id} className="flex justify-between py-2 border-b border-white/5 last:border-0">
                  <span className="text-sm text-zinc-400">{t.topic} · {t.difficulty}</span>
                  <span className="text-sm font-mono text-indigo-400">{t.accuracy_percent}%</span>
                </div>
              ))}
              {!reports?.recent_tests?.length && <p className="text-xs text-zinc-500">No data yet</p>}
            </GlowingCard>
          </div>
        )}
      </DashboardLayout>

      <MultiStepLoader loading={loading} />
    </>
  );
}

function AssessmentView({ skillCategory, topic, difficulty, questionIndex, totalQuestions, currentQuestion, selectedAnswer, setSelectedAnswer, loading, onSubmit }) {
  return (
    <div className="max-w-2xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4 bg-zinc-900/40 px-5 py-3 rounded-2xl border border-white/5">
        <div className="flex items-center gap-1.5 text-xs text-zinc-400">
          <span>{skillCategory}</span><ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
          <span>{topic}</span><ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
          <span className="text-indigo-400 font-semibold">{difficulty}</span>
        </div>
        <span className="text-xs font-mono font-bold bg-zinc-800 text-zinc-300 px-3 py-1 rounded-full border border-white/5">
          {questionIndex + 1} / {totalQuestions}
        </span>
      </div>
      <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden border border-white/5">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full transition-all duration-500" style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }} />
      </div>
      <GlowingCard>
        <div className="space-y-6">
          <p className="text-lg font-bold text-zinc-100">{currentQuestion.question}</p>
          <div className="space-y-3">
            {currentQuestion.options.map((option, idx) => (
              <button
                key={option}
                type="button"
                onClick={() => setSelectedAnswer(option)}
                disabled={loading}
                className={`w-full flex items-center gap-3 p-4 rounded-xl border text-left transition-colors ${
                  selectedAnswer === option ? "border-indigo-500/60 bg-indigo-500/10" : "border-white/10 bg-zinc-900/50 hover:border-indigo-500/30"
                }`}
              >
                {selectedAnswer === option ? <CheckCircle2 className="w-5 h-5 text-indigo-400 shrink-0" /> : <Circle className="w-5 h-5 text-zinc-500 shrink-0" />}
                <span className="text-xs font-mono font-bold text-zinc-500">{String.fromCharCode(65 + idx)}</span>
                <span className="text-sm text-zinc-100">{option}</span>
              </button>
            ))}
          </div>
          <div className="flex justify-end">
            <HoverBorderGradient onClick={onSubmit} disabled={!selectedAnswer.trim() || loading}>
              <span className="flex items-center gap-2"><Send className="w-4 h-4" /> Submit Answer</span>
            </HoverBorderGradient>
          </div>
        </div>
      </GlowingCard>
    </div>
  );
}

function ResultsView({ results, feedback, onNewTest, backLabel = "Start New Test" }) {
  return (
    <div className="space-y-6 max-w-2xl">
      <GlowingCard containerClassName="w-full">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-zinc-100">Results</h2>
            <p className="text-xs text-zinc-500">{results.correct_count}/{results.total_questions} correct</p>
          </div>
          <span className="text-3xl font-mono font-bold text-indigo-400">{results.accuracy_percent}%</span>
        </div>
      </GlowingCard>
      {feedback && (
        <GlowingCard>
          <h3 className="text-xs font-bold uppercase text-indigo-400 font-mono mb-2">AI Feedback</h3>
          <p className="text-sm text-zinc-300">{feedback.summary}</p>
        </GlowingCard>
      )}
      {results.questions?.map((q, idx) => (
        <GlowingCard key={q.question_id || idx} containerClassName="w-full">
          <div className="space-y-2">
            <div className="flex justify-between gap-2">
              <h4 className="text-sm font-bold text-zinc-100">Q{idx + 1}: {q.question}</h4>
              <span className={`text-xs px-2 py-0.5 rounded ${q.correct ? "text-emerald-400 bg-emerald-500/10" : "text-red-400 bg-red-500/10"}`}>
                {q.correct ? "Correct" : "Wrong"}
              </span>
            </div>
            <p className="text-xs text-zinc-500">{q.explanation}</p>
          </div>
        </GlowingCard>
      ))}
      <HoverBorderGradient onClick={onNewTest}>
        <span className="flex items-center gap-2"><RefreshCw className="w-4 h-4" /> {backLabel}</span>
      </HoverBorderGradient>
    </div>
  );
}

function StatCard({ label, value, icon }) {
  return (
    <GlowingCard>
      <div className="flex items-center gap-3">
        {icon && <span className="text-indigo-400">{icon}</span>}
        <div>
          <p className="text-[10px] uppercase font-mono text-zinc-500">{label}</p>
          <p className="text-2xl font-bold text-zinc-100">{value}</p>
        </div>
      </div>
    </GlowingCard>
  );
}

function ErrorAlert({ message, onDismiss }) {
  return (
    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-red-400">
      <AlertCircle className="w-5 h-5 shrink-0" />
      <p className="text-xs flex-1">{message}</p>
      <button type="button" onClick={onDismiss} className="text-xs opacity-70">Dismiss</button>
    </div>
  );
}

function SelectField({ label, icon, value, onChange, children }) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono flex items-center gap-2">{icon} {label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className="w-full bg-zinc-900 border border-white/10 rounded-xl px-4 py-3 text-zinc-100 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
        {children}
      </select>
    </div>
  );
}
