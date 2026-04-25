import { useState, useEffect, useRef } from "react";
import { sendQuery } from "./api";

function App() {
  const [messages, setMessages] = useState(() => {
    // Load chat history from localStorage on initial render
    const saved = localStorage.getItem("chat_history_dates");
    return saved ? JSON.parse(saved) : [];
  });
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  // States for date filtering modal and active filter
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [activeFilter, setActiveFilter] = useState(null);

  // Auto-save history onto localStorage whenever messages change
  useEffect(() => {
    localStorage.setItem("chat_history_dates", JSON.stringify(messages));
  }, [messages]);

  // Scroll to bottom when new messages arrive (only if we're not filtering)
  useEffect(() => {
    if (!activeFilter) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, activeFilter]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setError("");
    // Give user message a timestamp for future history-filtering
    const userMsg = {
      role: "user",
      text: trimmed,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    setIsSending(true);
    try {
      const response = await sendQuery(trimmed);
      // Give bot message a timestamp too
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: response, timestamp: new Date().toISOString() },
      ]);
      setInput("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send message.");
    } finally {
      setIsSending(false);
    }
  };

  // Clear out the whole session history
  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem("chat_history_dates");
    setActiveFilter(null);
  };

  // Action to apply the filter when both dates are provided
  const applyFilter = () => {
    if (startDate && endDate) {
      setActiveFilter({ start: startDate, end: endDate });
    }
    setIsModalOpen(false);
  };

  // Return to the latest active session
  const clearFilter = () => {
    setActiveFilter(null);
    setStartDate("");
    setEndDate("");
  };

  // Filter messages dynamically when activeFilter is set
  const displayedMessages = activeFilter
    ? messages.filter((msg) => {
        if (!msg.timestamp) return false; // Exclude messages with no timestamp
        const msgDate = new Date(msg.timestamp).getTime();
        const start = new Date(`${activeFilter.start}T00:00:00`).getTime();
        const end = new Date(`${activeFilter.end}T23:59:59`).getTime();
        return msgDate >= start && msgDate <= end;
      })
    : messages;

  return (
    <div className="min-h-screen px-4 py-10 relative">
      {/* Date Filter Modal Overlay */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-semibold text-upou-ink">
              Filter Chat History
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-black/70 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full rounded-xl border border-black/10 px-3 py-2 text-sm outline-none focus:border-upou-gold focus:ring-2 focus:ring-upou-gold/20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-black/70 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full rounded-xl border border-black/10 px-3 py-2 text-sm outline-none focus:border-upou-gold focus:ring-2 focus:ring-upou-gold/20"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-xl px-4 py-2 text-sm font-medium text-black/60 hover:bg-black/5"
              >
                Cancel
              </button>
              <button
                onClick={applyFilter}
                disabled={!startDate || !endDate}
                className="rounded-xl bg-upou-maroon px-4 py-2 text-sm font-medium text-white hover:brightness-110 disabled:opacity-50 transition"
              >
                Apply Filter
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="mx-auto max-w-4xl">
        <div className="rounded-3xl border border-black/10 bg-white/70 shadow-[0_20px_60px_-25px_rgba(11,18,32,0.35)] backdrop-blur">
          <header className="flex flex-col gap-3 border-b border-black/5 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex items-center gap-3">
                <img
                  src="/assets/up-seal.png"
                  alt="University of the Philippines seal"
                  className="h-11 w-11 rounded-full border border-black/10 bg-white object-cover shadow-sm"
                />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-upou-ink sm:text-xl">
                  UPOU Admissions Helpdesk
                </h1>
                <p className="text-sm text-black/60">
                  Ask about requirements, procedures, deadlines, and forms.
                </p>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => setIsModalOpen(true)}
                className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-black/70 hover:bg-gray-50 transition"
                title="Filter chat history by dates"
              >
                📅 History
              </button>
              {messages.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-red-600 hover:bg-red-50 transition"
                  title="Clear all chat history"
                >
                  Clear Chat
                </button>
              )}
              <span className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-black/70">
                Official KB only (RAG)
              </span>
            </div>
          </header>

          <main className="px-6 py-6">
            {/* Banner when user is viewing filtered history */}
            {activeFilter && (
              <div className="mb-4 flex items-center justify-between rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-800 shadow-sm border border-blue-100">
                <span>
                  Viewing history from{" "}
                  <span className="font-semibold">{activeFilter.start}</span> to{" "}
                  <span className="font-semibold">{activeFilter.end}</span>
                </span>
                <button
                  onClick={clearFilter}
                  className="font-semibold hover:underline bg-white/50 px-3 py-1 rounded-md text-xs border border-blue-200"
                >
                  Return to latest topic
                </button>
              </div>
            )}
            <div className="h-[55vh] min-h-[360px] overflow-y-auto pr-2">
              {displayedMessages.length === 0 ? (
                <div className="mx-auto mt-12 max-w-lg text-center">
                  <p className="text-sm font-medium text-black/80">
                    {activeFilter
                      ? "No history found for those dates"
                      : "Start a conversation"}
                  </p>
                  <p className="mt-2 text-sm text-black/60">
                    {activeFilter
                      ? "Try picking a different start and end date from the calendar."
                      : "Try: “What are the admission requirements for the BAMS program?” or “When is the application deadline?”"}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {displayedMessages?.map((msg, i) => {
                    const isUser = msg.role === "user";
                    return (
                      <div
                        key={i}
                        className={[
                          "flex",
                          isUser ? "justify-end" : "justify-start",
                        ].join(" ")}
                      >
                        <div
                          className={[
                            "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
                            isUser
                              ? "bg-upou-maroon text-white"
                              : "border border-black/10 bg-white text-upou-ink",
                          ].join(" ")}
                        >
                          <div className="mb-1 text-[11px] uppercase tracking-wide opacity-80">
                            {isUser ? "You" : "Helpdesk"}
                          </div>
                          <div className="whitespace-pre-wrap">{msg.text}</div>
                        </div>
                      </div>
                    );
                  })}

                  {isSending ? (
                    <div className="flex justify-start">
                      <div className="max-w-[85%] rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-black/60 shadow-sm">
                        <div className="mb-1 text-[11px] uppercase tracking-wide opacity-80">
                          Helpdesk
                        </div>
                        Thinking…
                      </div>
                    </div>
                  ) : null}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {error ? (
              <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                {error}
              </div>
            ) : null}
          </main>

          <footer className="border-t border-black/5 px-6 py-5">
            <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:gap-4">
              <label className="block text-xs font-medium text-black/70 sm:col-span-2">
                Your question
              </label>

              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={!!activeFilter}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    if (!activeFilter) void handleSend();
                  }
                }}
                placeholder={
                  activeFilter
                    ? "Sending is disabled while viewing history..."
                    : "Type your question… (Ctrl/⌘ + Enter to send)"
                }
                className="h-24 w-full resize-none rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-upou-ink shadow-sm outline-none transition focus:border-upou-gold focus:ring-4 focus:ring-upou-gold/20 disabled:opacity-60 disabled:cursor-not-allowed"
              />

              <div className="flex flex-col gap-2 sm:w-36 sm:self-center">
                <button
                  type="button"
                  disabled={isSending || !!activeFilter}
                  onClick={() => void handleSend()}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-upou-maroon px-6 py-3 text-[13px] font-semibold text-white shadow-[0_12px_26px_-16px_rgba(123,17,19,0.65)] ring-1 ring-black/5 transition hover:shadow-[0_16px_34px_-18px_rgba(123,17,19,0.8)] hover:brightness-110 focus:outline-none focus:ring-4 focus:ring-upou-gold/25 active:brightness-100 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <span>{isSending ? "Sending…" : "Send"}</span>
                  <svg
                    aria-hidden="true"
                    viewBox="0 0 24 24"
                    className="h-4 w-4 opacity-90"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M5 12h12" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </button>
                <p className="text-xs text-black/50 sm:text-center">
                  Uses official KB context.
                </p>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
