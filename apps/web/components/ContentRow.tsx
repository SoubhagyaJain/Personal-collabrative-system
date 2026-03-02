interface ContentRowProps {
  title: string;
}

export function ContentRow({ title }: ContentRowProps): JSX.Element {
  return (
    <section className="space-y-3">
      <h2 className="text-xl font-semibold">{title}</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <article
            key={`${title}-${index}`}
            className="aspect-[2/3] rounded-lg border border-zinc-800 bg-zinc-900/80 transition hover:scale-[1.02] hover:border-brand-500"
          />
        ))}
      </div>
    </section>
  );
}
