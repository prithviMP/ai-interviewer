import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

const DEFAULT_STEPS = [
  { text: "Analyzing skill requirements..." },
  { text: "Generating questions with Gemini..." },
  { text: "Crafting personalized MCQs..." },
  { text: "Validating question quality..." },
  { text: "Finalizing assessment..." },
];

export function MultiStepLoader({ loading, steps = DEFAULT_STEPS }) {
  const [currentState, setCurrentState] = useState(0);

  useEffect(() => {
    if (!loading) {
      setCurrentState(0);
      return;
    }
    const interval = setInterval(() => {
      setCurrentState((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
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
              Gemini AI Generation
            </h3>
            <div className="space-y-6">
              {steps.map((step, index) => {
                const isCompleted = index < currentState;
                const isLoading = index === currentState;
                const isPending = index > currentState;
                return (
                  <div key={index} className="flex items-center gap-4 text-left">
                    <div className="w-6 h-6 flex items-center justify-center shrink-0">
                      {isCompleted && (
                        <div className="bg-emerald-500 rounded-full p-1">
                          <Check className="w-3.5 h-3.5 text-black stroke-[3px]" />
                        </div>
                      )}
                      {isLoading && <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />}
                      {isPending && <div className="w-2.5 h-2.5 bg-zinc-700 rounded-full" />}
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
                  </div>
                );
              })}
            </div>
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
