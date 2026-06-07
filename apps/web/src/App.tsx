import { FormEvent, useMemo, useState } from "react";

type TranscriptionStatus =
  | "queued"
  | "extracting_audio"
  | "converting_audio"
  | "transcribing_midi"
  | "generating_score"
  | "exporting_pdf"
  | "completed"
  | "failed";

type CreateTranscriptionResponse = {
  id: string;
  status: TranscriptionStatus;
};

type TranscriptionStatusResponse = {
  id: string;
  youtube_url: string;
  status: TranscriptionStatus;
  created_at: string;
  updated_at: string;
  has_midi: boolean;
  has_pdf: boolean;
  error: string | null;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const statusLabels: Record<TranscriptionStatus, string> = {
  queued: "Queued",
  extracting_audio: "Extracting audio",
  converting_audio: "Converting audio",
  transcribing_midi: "Transcribing MIDI",
  generating_score: "Generating score",
  exporting_pdf: "Exporting PDF",
  completed: "Completed",
  failed: "Failed",
};

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [job, setJob] = useState<TranscriptionStatusResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const downloadLinks = useMemo(() => {
    if (!job) {
      return null;
    }
    return {
      midi: `${API_BASE_URL}/transcriptions/${job.id}/download-midi`,
      pdf: `${API_BASE_URL}/transcriptions/${job.id}/download-pdf`,
    };
  }, [job]);

  async function fetchStatus(id: string) {
    const response = await fetch(`${API_BASE_URL}/transcriptions/${id}/status`);
    if (!response.ok) {
      throw new Error("Could not load transcription status.");
    }
    const data = (await response.json()) as TranscriptionStatusResponse;
    setJob(data);
    return data;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setJob(null);
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/transcriptions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ youtube_url: youtubeUrl }),
      });

      if (!response.ok) {
        throw new Error("Could not create a transcription job.");
      }

      const data = (await response.json()) as CreateTranscriptionResponse;
      const latest = await fetchStatus(data.id);
      pollUntilFinished(latest.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function pollUntilFinished(id: string) {
    setIsPolling(true);
    let attempts = 0;

    const poll = async () => {
      attempts += 1;
      try {
        const latest = await fetchStatus(id);
        if (latest.status === "completed" || latest.status === "failed" || attempts >= 40) {
          setIsPolling(false);
          return;
        }
        window.setTimeout(poll, 1000);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not refresh status.");
        setIsPolling(false);
      }
    };

    window.setTimeout(poll, 1000);
  }

  return (
    <main className="min-h-screen">
      <section className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-12">
        <header className="max-w-3xl">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-accent">
            ScoreAI
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
            Turn a YouTube piano performance into sheet music.
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Paste a YouTube link to start a mocked transcription job. The backend is structured
            for yt-dlp, ffmpeg, Basic Pitch, music21, and MuseScore once the real pipeline is
            ready.
          </p>
        </header>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:flex-row"
        >
          <label className="sr-only" htmlFor="youtube-url">
            YouTube URL
          </label>
          <input
            id="youtube-url"
            type="url"
            value={youtubeUrl}
            onChange={(event) => setYoutubeUrl(event.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            required
            className="min-h-12 flex-1 rounded-md border border-slate-300 px-4 outline-none transition focus:border-accent focus:ring-2 focus:ring-blue-100"
          />
          <button
            type="submit"
            disabled={isSubmitting}
            className="min-h-12 rounded-md bg-accent px-6 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {isSubmitting ? "Starting..." : "Create Sheet Music"}
          </button>
        </form>

        {error ? (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        ) : null}

        {job ? (
          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold text-ink">Transcription status</h2>
                <p className="break-all text-sm text-slate-500">Job ID: {job.id}</p>
              </div>
              <span className="w-fit rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-accent">
                {statusLabels[job.status]}
                {isPolling ? "..." : ""}
              </span>
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <div className="rounded-md bg-staff p-4">
                <p className="text-sm font-semibold text-slate-500">Source</p>
                <p className="mt-1 break-all text-sm text-ink">{job.youtube_url}</p>
              </div>
              <div className="rounded-md bg-staff p-4">
                <p className="text-sm font-semibold text-slate-500">Updated</p>
                <p className="mt-1 text-sm text-ink">
                  {new Date(job.updated_at).toLocaleString()}
                </p>
              </div>
            </div>

            {job.error ? <p className="mt-4 text-sm text-red-600">{job.error}</p> : null}

            <div className="mt-6 flex flex-wrap gap-3">
              <a
                href={downloadLinks?.midi}
                className={`rounded-md px-4 py-2 text-sm font-semibold ${
                  job.has_midi
                    ? "bg-ink text-white"
                    : "pointer-events-none bg-slate-200 text-slate-500"
                }`}
              >
                Download MIDI
              </a>
              <a
                href={downloadLinks?.pdf}
                className={`rounded-md px-4 py-2 text-sm font-semibold ${
                  job.has_pdf
                    ? "bg-ink text-white"
                    : "pointer-events-none bg-slate-200 text-slate-500"
                }`}
              >
                Download PDF
              </a>
            </div>
          </section>
        ) : null}
      </section>
    </main>
  );
}

export default App;
