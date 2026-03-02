'use client';

import { useEffect, useState } from 'react';

import { ContentRow } from '@/components/ContentRow';
import { Hero } from '@/components/Hero';
import { getHome, postEvent } from '@/lib/api';
import { EventCreate, HomeResponse, ItemCard } from '@/lib/types';

const USER_ID_KEY = 'recsysflix_user_id';
const SESSION_ID_KEY = 'recsysflix_session_id';
const IMPRESSION_KEYS = 'recsysflix_impressions';

function getOrCreateUserId(): string {
  const existing = localStorage.getItem(USER_ID_KEY);
  if (existing) return existing;
  const next = crypto.randomUUID();
  localStorage.setItem(USER_ID_KEY, next);
  return next;
}

function getOrCreateSessionId(): string {
  const existing = sessionStorage.getItem(SESSION_ID_KEY);
  if (existing) return existing;
  const next = crypto.randomUUID();
  sessionStorage.setItem(SESSION_ID_KEY, next);
  return next;
}

export function HomeClient(): JSX.Element {
  const [home, setHome] = useState<HomeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const [identity, setIdentity] = useState<{ userId: string; sessionId: string } | null>(null);
  const [impressionSet, setImpressionSet] = useState<Set<string>>(new Set());

  useEffect(() => {
    const userId = getOrCreateUserId();
    const sessionId = getOrCreateSessionId();
    setIdentity({ userId, sessionId });

    const existing = sessionStorage.getItem(IMPRESSION_KEYS);
    if (existing) {
      setImpressionSet(new Set(JSON.parse(existing) as string[]));
    }
  }, []);

  useEffect(() => {
    if (!identity) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    getHome(identity.userId)
      .then((response) => {
        if (!cancelled) setHome(response);
      })
      .catch(() => {
        if (!cancelled) setError('Unable to load recommendations right now.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [identity, reloadToken]);

  useEffect(() => {
    if (!home || !identity) return;

    const nextSet = new Set(impressionSet);
    const payloads: EventCreate[] = [];

    home.rows.forEach((row) => {
      row.items.slice(0, 12).forEach((item, index) => {
        const dedupeKey = `${identity.sessionId}:${row.id}:${item.id}`;
        if (nextSet.has(dedupeKey)) return;
        nextSet.add(dedupeKey);
        payloads.push({
          user_id: identity.userId,
          item_id: item.id,
          event_type: 'impression',
          row_id: row.id,
          rank_position: index + 1,
          session_id: identity.sessionId
        });
      });
    });

    if (payloads.length === 0) return;

    setImpressionSet(nextSet);
    sessionStorage.setItem(IMPRESSION_KEYS, JSON.stringify([...nextSet]));
    payloads.forEach((payload) => void postEvent(payload));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [home, identity]);

  const onCardClick = (item: ItemCard, rankPosition: number, rowId: string): void => {
    if (!identity) return;
    void postEvent({
      user_id: identity.userId,
      item_id: item.id,
      event_type: 'click',
      row_id: rowId,
      rank_position: rankPosition,
      session_id: identity.sessionId
    });
  };

  const onPlayClick = (item: ItemCard, rankPosition: number, rowId: string): void => {
    if (!identity) return;
    void postEvent({
      user_id: identity.userId,
      item_id: item.id,
      event_type: 'play',
      row_id: rowId,
      rank_position: rankPosition,
      session_id: identity.sessionId
    });
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-10 px-6 py-10">
      <Hero />

      {loading ? (
        <div className="space-y-8">
          {Array.from({ length: 3 }).map((_, idx) => (
            <section key={idx} className="space-y-3">
              <div className="h-6 w-48 animate-pulse rounded bg-zinc-800" />
              <div className="flex gap-4 overflow-hidden">
                {Array.from({ length: 6 }).map((__, cardIdx) => (
                  <div key={cardIdx} className="h-64 w-44 animate-pulse rounded-lg bg-zinc-800" />
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : null}

      {!loading && error ? (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 text-center">
          <p className="mb-4 text-zinc-300">{error}</p>
          <button
            type="button"
            className="rounded bg-brand-500 px-4 py-2 font-semibold hover:bg-brand-500/90"
            onClick={() => setReloadToken((v) => v + 1)}
          >
            Retry
          </button>
        </div>
      ) : null}

      {!loading && !error && home
        ? home.rows.map((row) => (
            <ContentRow
              key={row.id}
              rowId={row.id}
              title={row.title}
              items={row.items}
              onCardClick={onCardClick}
              onPlayClick={onPlayClick}
            />
          ))
        : null}
    </main>
  );
}
