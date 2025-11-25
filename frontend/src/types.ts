interface Metrics {
  finalScore: number;
  tasteMatch: number;
  libraryOverlap: number;
  sharedCount: number;
  totalWatched: number[];
}

export interface MovieDiff {
  title: string;
  slug: string;
  poster: string;
  u1Rating: number;
  u2Rating: number;
}

export interface Data {
  users: string[];
  metrics: Metrics;
  controversialMovies: MovieDiff[];
  // agreeableMovies: MovieDiff[];
}
