const DisagreeRow = ({
  title,
  u1Rating,
  u2Rating,
}: {
  title: string;
  u1Rating: number;
  u2Rating: number;
}) => {
  return (
    <div className="w-full grid grid-cols-3 justify-items-center items-center gap-4 p-2 border-b border-gray-200 last:border-0">
      <div className="space-y-3">
        <span className="font-bold">{title}</span>
        <img alt={`${title} movie poster`}></img>
      </div>
      <div>
        {/* User 1's review and rating */}
        <p>
          {"★".repeat(Math.floor(u1Rating))}{" "}
          <span>{u1Rating % 1 != 0 ? "½" : ""}</span>{" "}
        </p>
      </div>
      <div>
        {/* User 2's review and rating */}
        <p>
          {"★".repeat(Math.floor(u2Rating))}{" "}
          <span>{u2Rating % 1 != 0 ? "½" : ""}</span>{" "}
        </p>
      </div>
    </div>
  );
};

export { DisagreeRow };
