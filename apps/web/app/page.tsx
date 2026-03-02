import { ContentRow } from '@/components/ContentRow';
import { Hero } from '@/components/Hero';

const rows = ['Trending Now', 'Team Picks', 'New Releases'];

export default function HomePage(): JSX.Element {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-10 px-6 py-10">
      <Hero />
      {rows.map((title) => (
        <ContentRow key={title} title={title} />
      ))}
    </main>
  );
}
