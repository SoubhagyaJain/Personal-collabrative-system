export type EventType = 'impression' | 'click' | 'play' | 'like' | 'add_to_list' | 'finish';

export interface ItemCard {
  id: string;
  title: string;
  poster_url: string | null;
  genres: string[];
}

export interface HomeRow {
  id: string;
  title: string;
  items: ItemCard[];
}

export interface HomeResponse {
  user_id: string;
  rows: HomeRow[];
}

export interface ItemDetail extends ItemCard {
  metadata_json: Record<string, unknown> | null;
}

export interface ItemResponse {
  item: ItemDetail;
  more_like_this: ItemCard[];
}

export interface EventCreate {
  user_id: string;
  item_id: string;
  event_type: EventType;
  row_id?: string;
  rank_position?: number;
  session_id?: string;
  variant_id?: string;
  watch_time_sec?: number;
  ts?: string;
}
