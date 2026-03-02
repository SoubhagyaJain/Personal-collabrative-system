'use client';

import Link from 'next/link';
import { useRef } from 'react';

import { ItemCard } from '@/lib/types';

interface ContentRowProps {
  rowId: string;
  title: string;
  items: ItemCard[];
  onCardClick: (item: ItemCard, rankPosition: number, rowId: string) => void;
  onPlayClick: (item: ItemCard, rankPosition: number, rowId: string) => void;
}

export function ContentRow({ rowId, title, items, onCardClick, onPlayClick }: ContentRowProps): JSX.Element {
  const scrollerRef = useRef<HTMLDivElement>(null);

  const scrollByAmount = (direction: -1 | 1): void => {
    if (!scrollerRef.current) {
      return;
    }
    scrollerRef.current.scrollBy({ left: direction * 720, behavior: 'smooth' });
  };

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">{title}</h2>
        <div className="flex gap-2">
          <button
            type="button"
            aria-label={`Scroll ${title} left`}
            className="rounded-md border border-zinc-700 px-3 py-1 text-sm hover:bg-zinc-800"
            onClick={() => scrollByAmount(-1)}
          >
            ←
          </button>
          <button
            type="button"
            aria-label={`Scroll ${title} right`}
            className="rounded-md border border-zinc-700 px-3 py-1 text-sm hover:bg-zinc-800"
            onClick={() => scrollByAmount(1)}
          >
            →
          </button>
        </div>
      </div>

      <div
        ref={scrollerRef}
        className="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-3 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
      >
        {items.map((item, index) => (
          <article key={item.id} className="group w-44 flex-none snap-start space-y-2">
            <Link
              href={`/title/${item.id}`}
              onClick={() => onCardClick(item, index + 1, rowId)}
              className="block overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900/80 transition-transform duration-300 group-hover:scale-[1.04] group-hover:border-brand-500"
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
            <p className="truncate text-sm font-medium">{item.title}</p>
            <button
              type="button"
              className="w-full rounded bg-brand-500 px-2 py-1 text-xs font-semibold hover:bg-brand-500/90"
              onClick={() => onPlayClick(item, index + 1, rowId)}
            >
              Play
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
