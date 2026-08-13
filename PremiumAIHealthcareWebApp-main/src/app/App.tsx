import { useState, useEffect, useRef } from "react";
import {
  Plus,
  Search,
  Settings,
  Send,
  Brain,
  Activity,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Menu,
  X,
  Pill,
  Shield,
  ChevronRight,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { clsx } from "clsx";

// ─── Types ────────────────────────────────────────────────────────────────────

type Role = "ai" | "user";

interface Message {
  id: string;
  role: Role;
  content: string;
  isResult?: boolean;
  timestamp: Date;
}

interface RecentItem {
  id: string;
  title: string;
  date: string;
  diagnosis: string;
}

type DemoStep = { role: Role; content: string; isLoading?: boolean };

// ─── Static data ──────────────────────────────────────────────────────────────

const RECENT: RecentItem[] = [
  { id: "r1", title: "Respiratory symptoms", date: "Today", diagnosis: "Influenza" },
  { id: "r2", title: "Skin rash evaluation", date: "Yesterday", diagnosis: "Dermatitis" },
  { id: "r3", title: "Digestive discomfort", date: "Aug 10", diagnosis: "Gastritis" },
  { id: "r4", title: "Persistent fatigue", date: "Aug 7", diagnosis: "Anemia screen" },
  { id: "r5", title: "Joint pain & stiffness", date: "Aug 2", diagnosis: "Arthritis eval" },
];

const DEMO: DemoStep[] = [
  {
    role: "ai",
    content:
      "Hi! I'm MedAI, your AI health assistant. I'll ask you a few focused questions about your symptoms to generate a preliminary assessment.\n\nWhat are you experiencing today?",
  },
  { role: "user", content: "I have fever and a pretty bad headache." },
  {
    role: "ai",
    content:
      "Got it — fever and headache. How long have you had the fever, and do you know roughly what temperature it has been?",
  },
  { role: "user", content: "About 3 days. Temperature around 38.5°C." },
  {
    role: "ai",
    content:
      "Three days at 38.5°C. Are you experiencing any body aches or muscle pain alongside those symptoms?",
  },
  { role: "user", content: "Yes, quite a bit actually — especially in my legs." },
  {
    role: "ai",
    content: "Understood. One more: any chills, fatigue, or loss of appetite?",
  },
  { role: "user", content: "Yes to all three. I'm really tired." },
  {
    role: "ai",
    content:
      "Thank you — I have enough to run the assessment. Analyzing your symptom profile now...",
    isLoading: true,
  },
];

const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

// ─── ScoreBar ─────────────────────────────────────────────────────────────────

function ScoreBar({ score, color }: { score: number; color: string }) {
  return (
    <div className="h-1.5 w-full rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
      <motion.div
        className={clsx("h-full rounded-full", color)}
        initial={{ width: 0 }}
        animate={{ width: `${score}%` }}
        transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
      />
    </div>
  );
}

// ─── AssessmentResult ─────────────────────────────────────────────────────────

function AssessmentResult() {
  const diagnoses = [
    { name: "Influenza (Flu)", score: 72, color: "bg-teal-400" },
    { name: "Viral Infection", score: 18, color: "bg-cyan-400" },
    { name: "Common Cold", score: 10, color: "bg-sky-400" },
  ];

  const symptoms = [
    "Fever 38.5°C",
    "Headache",
    "Body Aches",
    "Leg Pain",
    "Chills",
    "Fatigue",
    "Loss of Appetite",
    "3-Day Duration",
  ];

  const cards = [
    {
      Icon: Clock,
      title: "Recovery Timeline",
      body: "Influenza typically resolves in 7–10 days. Symptoms peak around day 3–5.",
    },
    {
      Icon: Pill,
      title: "Common Treatments",
      body: "Rest, hydration, and antipyretics. Antivirals may shorten duration if started early.",
    },
    {
      Icon: Shield,
      title: "When to Seek Care",
      body: "See a doctor if fever exceeds 39.5°C, breathing is difficult, or symptoms worsen after day 5.",
    },
    {
      Icon: Activity,
      title: "Contagion Period",
      body: "Contagious from 1 day before symptoms appear through 5–7 days after onset.",
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="w-full rounded-2xl border overflow-hidden"
      style={{ borderColor: "rgba(255,255,255,0.08)", background: "#0d1524" }}
    >
      {/* Card header */}
      <div
        className="flex items-center gap-3 px-5 py-4 border-b"
        style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.015)" }}
      >
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center"
          style={{ background: "rgba(45,212,191,0.12)", border: "1px solid rgba(45,212,191,0.22)" }}
        >
          <CheckCircle2 size={15} className="text-teal-400" />
        </div>
        <div>
          <div className="text-sm font-semibold" style={{ color: "rgba(228,232,242,0.9)" }}>
            Assessment Complete
          </div>
          <div className="text-[11px] mt-0.5 font-mono tracking-wide" style={{ color: "rgba(228,232,242,0.35)" }}>
            8 symptoms analyzed · 3 candidates scored
          </div>
        </div>
        <div className="ml-auto flex flex-col items-end gap-0.5">
          <div className="text-[10px] font-mono" style={{ color: "rgba(228,232,242,0.2)" }}>
            MedAI-2.4
          </div>
          <div className="text-[10px] font-mono text-teal-400/50">HIGH CONFIDENCE</div>
        </div>
      </div>

      <div className="p-5 space-y-6">
        {/* Primary diagnosis */}
        <div>
          <div
            className="text-[10px] uppercase tracking-[0.14em] font-mono mb-3"
            style={{ color: "rgba(228,232,242,0.3)" }}
          >
            Primary Assessment
          </div>
          <div
            className="rounded-xl p-4"
            style={{
              background: "rgba(45,212,191,0.06)",
              border: "1px solid rgba(45,212,191,0.16)",
            }}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="font-bold text-lg leading-none" style={{ color: "rgba(228,232,242,0.92)" }}>
                  {diagnoses[0].name}
                </div>
                <div className="text-[11px] font-mono mt-1" style={{ color: "rgba(228,232,242,0.35)" }}>
                  Top model prediction
                </div>
              </div>
              <div className="text-3xl font-bold font-mono text-teal-400 leading-none">
                {diagnoses[0].score}%
              </div>
            </div>
            <ScoreBar score={diagnoses[0].score} color={diagnoses[0].color} />
          </div>
        </div>

        {/* Other candidates */}
        <div>
          <div
            className="text-[10px] uppercase tracking-[0.14em] font-mono mb-3"
            style={{ color: "rgba(228,232,242,0.3)" }}
          >
            Other Considerations
          </div>
          <div className="space-y-3.5">
            {diagnoses.slice(1).map((d) => (
              <div key={d.name}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm" style={{ color: "rgba(228,232,242,0.65)" }}>
                    {d.name}
                  </span>
                  <span className="text-sm font-mono" style={{ color: "rgba(228,232,242,0.4)" }}>
                    {d.score}%
                  </span>
                </div>
                <ScoreBar score={d.score} color={d.color} />
              </div>
            ))}
          </div>
        </div>

        {/* Why this result */}
        <div>
          <div
            className="text-[10px] uppercase tracking-[0.14em] font-mono mb-3"
            style={{ color: "rgba(228,232,242,0.3)" }}
          >
            Why this result?
          </div>
          <div className="flex flex-wrap gap-2">
            {symptoms.map((s) => (
              <span
                key={s}
                className="text-[11px] px-2.5 py-1 rounded-full font-mono"
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.10)",
                  color: "rgba(228,232,242,0.55)",
                }}
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        {/* Medical info cards */}
        <div>
          <div
            className="text-[10px] uppercase tracking-[0.14em] font-mono mb-3"
            style={{ color: "rgba(228,232,242,0.3)" }}
          >
            Medical Information
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {cards.map(({ Icon, title, body }) => (
              <div
                key={title}
                className="rounded-xl p-3.5 transition-colors cursor-default"
                style={{
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLDivElement).style.background = "rgba(255,255,255,0.05)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLDivElement).style.background = "rgba(255,255,255,0.03)";
                }}
              >
                <Icon size={13} className="text-cyan-400 mb-2.5" />
                <div
                  className="text-xs font-semibold mb-1.5 leading-snug"
                  style={{ color: "rgba(228,232,242,0.75)" }}
                >
                  {title}
                </div>
                <div className="text-[11px] leading-relaxed" style={{ color: "rgba(228,232,242,0.4)" }}>
                  {body}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Disclaimer */}
        <div
          className="rounded-xl p-4 flex gap-3"
          style={{
            background: "rgba(251,191,36,0.05)",
            border: "1px solid rgba(251,191,36,0.15)",
          }}
        >
          <AlertTriangle size={13} className="text-amber-400 mt-0.5 shrink-0" />
          <p className="text-[11px] leading-relaxed" style={{ color: "rgba(253,230,138,0.55)" }}>
            <span className="font-semibold" style={{ color: "rgba(253,230,138,0.72)" }}>
              Educational use only.
            </span>{" "}
            This is an ML-based assessment and does not constitute a medical diagnosis. Results are
            probabilistic estimates and must not replace evaluation by a licensed healthcare professional.
            Always consult a qualified doctor for medical advice.
          </p>
        </div>
      </div>
    </motion.div>
  );
}

// ─── TypingIndicator ──────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 4 }}
      transition={{ duration: 0.2 }}
      className="flex items-end gap-3"
    >
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
        style={{ background: "rgba(6,182,212,0.12)", border: "1px solid rgba(6,182,212,0.22)" }}
      >
        <Brain size={13} className="text-cyan-400" />
      </div>
      <div
        className="rounded-2xl rounded-bl-sm px-4 py-3.5"
        style={{ background: "#0d1524", border: "1px solid rgba(255,255,255,0.07)" }}
      >
        <div className="flex gap-1.5 items-center">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-1.5 h-1.5 rounded-full"
              style={{ background: "rgba(255,255,255,0.3)" }}
              animate={{ opacity: [0.25, 0.9, 0.25], y: [0, -2.5, 0] }}
              transition={{ duration: 1.3, repeat: Infinity, delay: i * 0.18, ease: "easeInOut" }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}

// ─── MessageBubble ────────────────────────────────────────────────────────────

function MessageBubble({ message }: { message: Message }) {
  const isAI = message.role === "ai";

  if (message.isResult) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-start gap-3"
      >
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-1"
          style={{ background: "rgba(45,212,191,0.12)", border: "1px solid rgba(45,212,191,0.22)" }}
        >
          <Brain size={13} className="text-teal-400" />
        </div>
        <div className="flex-1 min-w-0">
          <AssessmentResult />
        </div>
      </motion.div>
    );
  }

  const lines = message.content.split("\n");

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={clsx("flex items-end gap-3", !isAI && "flex-row-reverse")}
    >
      {isAI ? (
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
          style={{ background: "rgba(6,182,212,0.12)", border: "1px solid rgba(6,182,212,0.22)" }}
        >
          <Brain size={13} className="text-cyan-400" />
        </div>
      ) : (
        <div
          className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[11px] font-bold"
          style={{
            background: "rgba(255,255,255,0.07)",
            border: "1px solid rgba(255,255,255,0.12)",
            color: "rgba(228,232,242,0.5)",
          }}
        >
          Y
        </div>
      )}
      <div
        className="max-w-[76%] text-sm leading-relaxed px-4 py-3"
        style={
          isAI
            ? {
                borderRadius: "1rem 1rem 1rem 0.25rem",
                background: "#0d1524",
                border: "1px solid rgba(255,255,255,0.07)",
                color: "rgba(228,232,242,0.78)",
              }
            : {
                borderRadius: "1rem 1rem 0.25rem 1rem",
                background: "rgba(6,182,212,0.10)",
                border: "1px solid rgba(6,182,212,0.18)",
                color: "rgba(228,232,242,0.88)",
              }
        }
      >
        {lines.map((line, i) => (
          <span key={i}>
            {line}
            {i < lines.length - 1 && <br />}
          </span>
        ))}
        <div className="text-[10px] font-mono mt-1.5" style={{ color: "rgba(255,255,255,0.2)" }}>
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </motion.div>
  );
}

// ─── EmptyState ───────────────────────────────────────────────────────────────

function EmptyState({ onDemo }: { onDemo: () => void }) {
  const suggestions = [
    "Fever & headache",
    "Skin irritation",
    "Chest tightness",
    "Digestive pain",
    "Joint stiffness",
    "Persistent fatigue",
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full gap-7 px-6 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="space-y-1"
      >
        <div
          className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5"
          style={{
            background: "rgba(6,182,212,0.09)",
            border: "1px solid rgba(6,182,212,0.18)",
            boxShadow: "0 0 32px rgba(6,182,212,0.08)",
          }}
        >
          <Brain size={26} className="text-cyan-400" />
        </div>
        <h2
          className="font-semibold text-xl"
          style={{ color: "rgba(228,232,242,0.88)" }}
        >
          How can I help you today?
        </h2>
        <p
          className="text-sm leading-relaxed max-w-xs mx-auto"
          style={{ color: "rgba(228,232,242,0.36)" }}
        >
          Describe your symptoms and I'll run a machine learning assessment to suggest possible
          conditions.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.15 }}
        className="flex flex-wrap gap-2 justify-center max-w-md"
      >
        {suggestions.map((s, i) => (
          <motion.button
            key={s}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 + i * 0.06 }}
            onClick={onDemo}
            className="text-xs px-3.5 py-2 rounded-full transition-all"
            style={{
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.08)",
              color: "rgba(228,232,242,0.45)",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget;
              el.style.background = "rgba(255,255,255,0.08)";
              el.style.borderColor = "rgba(255,255,255,0.15)";
              el.style.color = "rgba(228,232,242,0.78)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget;
              el.style.background = "rgba(255,255,255,0.04)";
              el.style.borderColor = "rgba(255,255,255,0.08)";
              el.style.color = "rgba(228,232,242,0.45)";
            }}
          >
            {s}
          </motion.button>
        ))}
      </motion.div>

      <p className="text-[10px] font-mono" style={{ color: "rgba(255,255,255,0.18)" }}>
        Click a suggestion to see a full demo assessment · Or type below
      </p>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────

function Sidebar({
  isOpen,
  onClose,
  onNewChat,
  activeId,
}: {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  activeId: string | null;
}) {
  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-20 md:hidden"
            style={{ background: "rgba(0,0,0,0.65)" }}
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      <div
        className={clsx(
          "fixed md:static inset-y-0 left-0 z-30 md:z-auto",
          "w-[260px] h-full flex flex-col shrink-0",
          "transition-transform duration-300 ease-in-out",
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
        style={{ background: "#060a11", borderRight: "1px solid rgba(255,255,255,0.05)" }}
      >
        {/* Logo */}
        <div
          className="flex items-center gap-2.5 px-4 h-14 shrink-0"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}
        >
          <div
            className="w-7 h-7 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #22d3ee, #00c89a)",
              boxShadow: "0 0 14px rgba(6,182,212,0.28)",
            }}
          >
            <Brain size={14} className="text-white" />
          </div>
          <span className="font-bold tracking-tight text-[15px]" style={{ color: "rgba(228,232,242,0.92)" }}>
            MedAI
          </span>
          <span
            className="text-[10px] font-mono px-1.5 py-0.5 rounded ml-0.5"
            style={{
              background: "rgba(6,182,212,0.10)",
              color: "rgba(6,182,212,0.6)",
              border: "1px solid rgba(6,182,212,0.15)",
            }}
          >
            Beta
          </span>
          <button
            onClick={onClose}
            className="md:hidden ml-auto p-1 rounded-lg transition-colors"
            style={{ color: "rgba(228,232,242,0.28)" }}
            onMouseEnter={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "rgba(228,232,242,0.65)")}
            onMouseLeave={(e) => ((e.currentTarget as HTMLButtonElement).style.color = "rgba(228,232,242,0.28)")}
          >
            <X size={15} />
          </button>
        </div>

        {/* New Assessment */}
        <div className="px-3 pt-4 pb-2 shrink-0">
          <button
            onClick={onNewChat}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all"
            style={{
              background: "rgba(6,182,212,0.09)",
              border: "1px solid rgba(6,182,212,0.20)",
              color: "#22d3ee",
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget;
              el.style.background = "rgba(6,182,212,0.14)";
              el.style.borderColor = "rgba(6,182,212,0.28)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget;
              el.style.background = "rgba(6,182,212,0.09)";
              el.style.borderColor = "rgba(6,182,212,0.20)";
            }}
          >
            <Plus size={15} />
            New Assessment
          </button>
        </div>

        {/* Search */}
        <div className="px-3 pb-3 shrink-0">
          <div
            className="flex items-center gap-2 px-3 py-2.5 rounded-xl"
            style={{
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            <Search size={13} className="shrink-0" style={{ color: "rgba(255,255,255,0.22)" }} />
            <input
              type="text"
              placeholder="Search assessments..."
              className="flex-1 bg-transparent text-[13px] outline-none"
              style={{ color: "rgba(228,232,242,0.65)" }}
            />
          </div>
        </div>

        {/* Recent list */}
        <div className="flex-1 overflow-y-auto px-3 min-h-0">
          <div
            className="text-[10px] uppercase tracking-[0.1em] font-mono px-2 mb-2"
            style={{ color: "rgba(255,255,255,0.22)" }}
          >
            Recent
          </div>
          <div className="space-y-0.5">
            {RECENT.map((item) => (
              <button
                key={item.id}
                className="w-full text-left px-3 py-2.5 rounded-xl transition-all group"
                style={{
                  background: activeId === item.id ? "rgba(255,255,255,0.07)" : "transparent",
                  border: activeId === item.id ? "1px solid rgba(255,255,255,0.08)" : "1px solid transparent",
                }}
                onMouseEnter={(e) => {
                  if (activeId !== item.id) {
                    (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.04)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeId !== item.id) {
                    (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                  }
                }}
              >
                <div className="text-[13px] truncate" style={{ color: "rgba(228,232,242,0.65)" }}>
                  {item.title}
                </div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-[10px] font-mono" style={{ color: "rgba(255,255,255,0.22)" }}>
                    {item.date}
                  </span>
                  <span style={{ color: "rgba(255,255,255,0.15)" }}>·</span>
                  <span className="text-[10px] font-mono text-cyan-400/45">{item.diagnosis}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className="p-3 shrink-0" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
          <button
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[13px] transition-all"
            style={{ color: "rgba(228,232,242,0.35)" }}
            onMouseEnter={(e) => {
              const el = e.currentTarget;
              el.style.color = "rgba(228,232,242,0.65)";
              el.style.background = "rgba(255,255,255,0.04)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget;
              el.style.color = "rgba(228,232,242,0.35)";
              el.style.background = "transparent";
            }}
          >
            <Settings size={14} />
            Settings
          </button>
        </div>
      </div>
    </>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [demoRunning, setDemoRunning] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const addMessage = (role: Role, content: string, isResult?: boolean) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        role,
        content,
        isResult,
        timestamp: new Date(),
      },
    ]);
  };

  const runDemo = async () => {
    if (demoRunning) return;
    setDemoRunning(true);
    setHasStarted(true);
    setMessages([]);
    setIsTyping(false);

    for (const step of DEMO) {
      if (step.role === "ai") {
        setIsTyping(true);
        await sleep(900 + Math.min(step.content.length * 9, 2200));
        setIsTyping(false);
        addMessage("ai", step.content);

        if (step.isLoading) {
          await sleep(700);
          setIsTyping(true);
          await sleep(2900);
          setIsTyping(false);
          addMessage("ai", "", true);
        }
      } else {
        await sleep(650);
        addMessage("user", step.content);
      }
      await sleep(180);
    }

    setDemoRunning(false);
  };

  const handleSend = () => {
    const text = input.trim();
    if (!text || demoRunning) return;

    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    if (!hasStarted) {
      setHasStarted(true);
      addMessage("user", text);
      setIsTyping(true);
      setTimeout(() => {
        setIsTyping(false);
        addMessage(
          "ai",
          "Hi! I'm MedAI. I'll ask a few questions about your symptoms.\n\nHow long have you been experiencing this, and has anything changed recently?"
        );
      }, 1300);
      return;
    }

    addMessage("user", text);
    setIsTyping(true);
    setTimeout(() => {
      setIsTyping(false);
      addMessage(
        "ai",
        "Thank you for that detail. Are you also experiencing any other symptoms — such as fever, fatigue, or pain in a specific area?"
      );
    }, 1600);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 128) + "px";
  };

  const handleNewChat = () => {
    setMessages([]);
    setHasStarted(false);
    setIsTyping(false);
    setDemoRunning(false);
    setSidebarOpen(false);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  return (
    <div
      className="h-screen w-screen flex overflow-hidden"
      style={{ background: "#080c14", color: "#e4e8f2", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
        activeId={null}
      />

      {/* Main panel */}
      <div className="flex flex-col flex-1 min-w-0 h-full">
        {/* Top bar */}
        <div
          className="flex items-center gap-3 px-5 h-14 shrink-0"
          style={{
            borderBottom: "1px solid rgba(255,255,255,0.05)",
            background: "rgba(8,12,20,0.92)",
            backdropFilter: "blur(12px)",
          }}
        >
          <button
            onClick={() => setSidebarOpen(true)}
            className="md:hidden p-1.5 rounded-lg transition-all"
            style={{ color: "rgba(255,255,255,0.3)" }}
            onMouseEnter={(e) => {
              const el = e.currentTarget;
              el.style.color = "rgba(255,255,255,0.6)";
              el.style.background = "rgba(255,255,255,0.05)";
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget;
              el.style.color = "rgba(255,255,255,0.3)";
              el.style.background = "transparent";
            }}
          >
            <Menu size={17} />
          </button>

          <div className="flex items-center gap-2.5">
            <motion.div
              className="w-2 h-2 rounded-full bg-teal-400"
              animate={{ opacity: [1, 0.45, 1] }}
              transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
            />
            <span className="text-[14px] font-semibold" style={{ color: "rgba(228,232,242,0.82)" }}>
              MedAI
            </span>
            <span style={{ color: "rgba(255,255,255,0.18)" }}>·</span>
            <span className="text-[13px]" style={{ color: "rgba(228,232,242,0.38)" }}>
              AI Health Assistant
            </span>
          </div>

          <div className="ml-auto flex items-center gap-3">
            {!hasStarted && (
              <motion.button
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                onClick={runDemo}
                disabled={demoRunning}
                className="text-[12px] px-3.5 py-1.5 rounded-lg font-mono flex items-center gap-1.5 transition-all"
                style={{
                  background: "rgba(6,182,212,0.09)",
                  border: "1px solid rgba(6,182,212,0.20)",
                  color: "#22d3ee",
                  opacity: demoRunning ? 0.5 : 1,
                }}
                onMouseEnter={(e) => {
                  if (!demoRunning) {
                    (e.currentTarget as HTMLButtonElement).style.background = "rgba(6,182,212,0.14)";
                  }
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = "rgba(6,182,212,0.09)";
                }}
              >
                Demo Assessment
                <ChevronRight size={12} />
              </motion.button>
            )}
            <div className="text-[11px] font-mono hidden sm:block" style={{ color: "rgba(255,255,255,0.18)" }}>
              MedAI-2.4
            </div>
          </div>
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-y-auto min-h-0">
          <style>{`
            .chat-scroll::-webkit-scrollbar { width: 0; }
            .chat-scroll { scrollbar-width: none; }
          `}</style>
          <div className="chat-scroll h-full overflow-y-auto">
            {!hasStarted ? (
              <EmptyState onDemo={runDemo} />
            ) : (
              <div className="max-w-[680px] mx-auto px-4 sm:px-6 py-6 space-y-5">
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                <AnimatePresence>{isTyping && <TypingIndicator />}</AnimatePresence>
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Composer */}
        <div
          className="shrink-0 px-4 sm:px-6 py-4"
          style={{
            borderTop: "1px solid rgba(255,255,255,0.05)",
            background: "rgba(8,12,20,0.92)",
            backdropFilter: "blur(12px)",
          }}
        >
          <div className="max-w-[680px] mx-auto">
            <div
              className="flex items-end gap-3 rounded-2xl px-4 py-3 transition-colors"
              style={{ background: "#0d1524", border: "1px solid rgba(255,255,255,0.08)" }}
              onFocus={() => {}}
            >
              <textarea
                ref={textareaRef}
                value={input}
                onChange={handleTextareaChange}
                onKeyDown={handleKeyDown}
                placeholder="Tell me what you're experiencing..."
                rows={1}
                disabled={demoRunning}
                className="flex-1 bg-transparent text-[14px] outline-none resize-none leading-relaxed"
                style={{
                  color: "rgba(228,232,242,0.8)",
                  minHeight: "22px",
                  maxHeight: "128px",
                  overflowY: "auto",
                }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || demoRunning}
                className="w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-200 shrink-0"
                style={
                  input.trim() && !demoRunning
                    ? {
                        background: "#00c89a",
                        color: "#080c14",
                        boxShadow: "0 0 18px rgba(0,200,154,0.22)",
                      }
                    : {
                        background: "rgba(255,255,255,0.05)",
                        color: "rgba(255,255,255,0.2)",
                        cursor: "not-allowed",
                      }
                }
                onMouseEnter={(e) => {
                  if (input.trim() && !demoRunning) {
                    (e.currentTarget as HTMLButtonElement).style.background = "#00e0ac";
                  }
                }}
                onMouseLeave={(e) => {
                  if (input.trim() && !demoRunning) {
                    (e.currentTarget as HTMLButtonElement).style.background = "#00c89a";
                  }
                }}
              >
                <Send size={13} />
              </button>
            </div>
            <p
              className="text-[10px] text-center mt-2 font-mono"
              style={{ color: "rgba(255,255,255,0.18)" }}
            >
              For educational purposes only — not a substitute for professional medical advice
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
