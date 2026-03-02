import Link from 'next/link';

import { getItem } from '@/lib/api';

interface TitlePageProps {
  params: {
    id: string;
  };
}

export default async function TitlePage({ params }: TitlePageProps): Promise<JSX.Element> {
  const data = await getItem(params.id);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-10 px-6 py-10">
      <Link href="/" className="text-sm text-zinc-300 hover:text-white">
        ← Back to home
      </Link>

      <section className="grid gap-6 md:grid-cols-[240px_1fr]">
        <div className="aspect-[2/3] overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
          {data.item.poster_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={data.item.poster_url} alt={data.item.title} className="h-full w-full object-cover" />
          ) : (
            <div className="flex h-full items-end p-4 text-zinc-300">{data.item.title}</div>
          )}
        </div>

        <div className="space-y-4">
          <h1 className="text-4xl font-bold">{data.item.title}</h1>
          <p className="text-sm text-zinc-300">Genres: {data.item.genres.join(', ') || 'Unknown'}</p>
          {data.item.metadata_json ? (
            <pre className="overflow-auto rounded-lg border border-zinc-800 bg-zinc-900/70 p-4 text-xs text-zinc-300">
              {JSON.stringify(data.item.metadata_json, null, 2)}
            </pre>
          ) : null}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-2xl font-semibold">More Like This</h2>
        <div className="flex gap-4 overflow-x-auto pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          {data.more_like_this.map((item) => (
            <Link
              key={item.id}
              href={`/title/${item.id}`}
              className="w-44 flex-none overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900 transition hover:scale-[1.03] hover:border-brand-500"
            >
              <div className="aspect-[2/3] bg-gradient-to-b from-zinc-800 to-zinc-950">
                {item.poster_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={item.poster_url} alt={item.title} className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full items-end p-3 text-xs text-zinc-300">{item.title}</div>
                )}
              </div>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
