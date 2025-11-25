import type { MovieDiff } from "@/types";

const DisagreeRow = ({
  movieDiff,
  user1,
  user2,
}: {
  movieDiff: MovieDiff;
  user1: string;
  user2: string;
}) => {
  const { title, slug, poster, u1Rating, u2Rating } = movieDiff;
  const filmUrl = `https://letterboxd.com/film/${slug}`;
  return (
    <div className="w-full grid grid-cols-3 justify-items-center items-center gap-4 p-2 border-b border-gray-200 last:border-0">
      <a href={filmUrl} target="_blank">
        <div className="space-y-3 flex flex-col items-center">
          <span className="font-bold text-center">{title}</span>
          <img
            src={poster}
            alt={`${title} movie poster`}
            className="w-20"
          ></img>
        </div>
      </a>
      <div className="text-xl">
        {/* User 1's review and rating */}
        <a
          href={`https://letterboxd.com/${user1}/film/${slug}/reviews/`}
          target="_blank"
        >
          {"★".repeat(Math.floor(u1Rating))}{" "}
          <span>{u1Rating % 1 != 0 ? "½" : ""}</span>{" "}
        </a>
      </div>
      <div className="text-xl">
        {/* User 2's review and rating */}
        <a
          href={`https://letterboxd.com/${user2}/film/${slug}/reviews/`}
          target="_blank"
        >
          {"★".repeat(Math.floor(u2Rating))}{" "}
          <span>{u2Rating % 1 != 0 ? "½" : ""}</span>{" "}
        </a>
      </div>
    </div>
  );
};

export { DisagreeRow };
