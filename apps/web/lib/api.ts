import { EventCreate, HomeResponse, ItemResponse } from '@/lib/types';

function baseUrl(): string {
  if (typeof window === 'undefined') {
    return process.env.INTERNAL_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl()}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {})
    },
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function getHome(userId: string): Promise<HomeResponse> {
  const params = new URLSearchParams({ user_id: userId });
  return requestJson<HomeResponse>(`/api/v1/home?${params.toString()}`);
}

export async function getItem(itemId: string): Promise<ItemResponse> {
  return requestJson<ItemResponse>(`/api/v1/item/${itemId}`);
}

export async function postEvent(payload: EventCreate): Promise<void> {
  await requestJson<{ status: string }>('/api/v1/events', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}
