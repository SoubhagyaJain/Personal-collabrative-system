export function Hero(): JSX.Element {
  return (
    <section className="relative overflow-hidden rounded-2xl border border-zinc-800 bg-gradient-to-r from-zinc-900 to-zinc-950 p-8 shadow-2xl">
      <p className="mb-4 inline-block rounded-full bg-brand-500/20 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-500">
        Featured
      </p>
      <h1 className="mb-2 text-4xl font-bold">Personal Collaborative System</h1>
      <p className="max-w-2xl text-zinc-300">
        Streamline teamwork with shared tasks, intelligent recommendations, and machine-learning
        enhanced workflows.
      </p>
      <button className="mt-6 rounded-md bg-brand-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-brand-500/90">
        Continue Building
      </button>
    </section>
  );
}
