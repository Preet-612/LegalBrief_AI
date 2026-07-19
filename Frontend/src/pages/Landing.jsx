import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Scale, ShieldCheck, MessageSquareText, FileSearch, ArrowRight, Upload, Sparkles } from "lucide-react";
import Footer from "../components/layout/Footer";
import Button from "../components/common/Button";
import { ROUTES } from "../utils/constants";

const FEATURES = [
  { icon: FileSearch, title: "Instant Summaries", desc: "Get an executive summary of any contract in seconds, no legal degree required." },
  { icon: ShieldCheck, title: "Risk Detection", desc: "Automatically flag risky clauses with severity scoring and plain-English suggestions." },
  { icon: MessageSquareText, title: "Chat With Your Contract", desc: "Ask questions in natural language and get grounded answers from the document." },
];

const STEPS = [
  { step: "01", title: "Upload", desc: "Drop in a PDF or DOCX contract." },
  { step: "02", title: "Analyze", desc: "AI extracts clauses, dates, and risks." },
  { step: "03", title: "Understand", desc: "Chat, review summaries, and negotiate with confidence." },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-primary-600 p-1.5">
            <Scale size={18} className="text-white" />
          </div>
          <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">LegalBrief Agent</span>
        </div>
        <Button variant="primary" size="sm" onClick={() => navigate(ROUTES.DASHBOARD)}>
          Open Dashboard
        </Button>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pb-20 pt-16 text-center sm:pt-24">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary-100 via-white to-white dark:from-primary-500/10 dark:via-gray-950 dark:to-gray-950" />
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto flex max-w-3xl flex-col items-center"
        >
          <span className="mb-5 flex items-center gap-1.5 rounded-full border border-primary-200 bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700 dark:border-primary-500/30 dark:bg-primary-500/10 dark:text-primary-400">
            <Sparkles size={13} /> AI-powered contract intelligence
          </span>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100 sm:text-6xl">
            Understand any contract <span className="bg-gradient-to-r from-primary-600 to-secondary-500 bg-clip-text text-transparent">in minutes</span>
          </h1>
          <p className="mt-5 max-w-xl text-lg text-gray-600 dark:text-gray-400">
            Upload legal documents, get instant summaries, catch risky clauses, and chat with an AI that actually read the fine print — so you don't have to.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" icon={Upload} onClick={() => navigate(ROUTES.UPLOAD)}>
              Upload a Document
            </Button>
            <Button size="lg" variant="outline" icon={ArrowRight} iconPosition="right" onClick={() => navigate(ROUTES.DASHBOARD)}>
              Explore Dashboard
            </Button>
          </div>
        </motion.div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <h2 className="text-center text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
          Everything you need to read contracts with confidence
        </h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.1 }}
              className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="mb-4 w-fit rounded-xl bg-primary-100 p-3 dark:bg-primary-500/10">
                <f.icon size={22} className="text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-gray-50 px-6 py-16 dark:bg-gray-900/40">
        <div className="mx-auto max-w-6xl">
          <h2 className="text-center text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
            How it works
          </h2>
          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.step} className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary-600 text-sm font-bold text-white">
                  {s.step}
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100">{s.title}</h3>
                <p className="mt-1.5 text-sm text-gray-600 dark:text-gray-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20 text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
          Stop signing contracts you don't fully understand
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-gray-600 dark:text-gray-400">
          Get started for free — no legal jargon, no billable hours.
        </p>
        <div className="mt-7">
          <Button size="lg" icon={ArrowRight} iconPosition="right" onClick={() => navigate(ROUTES.UPLOAD)}>
            Get Started
          </Button>
        </div>
      </section>

      <Footer />
    </div>
  );
}
