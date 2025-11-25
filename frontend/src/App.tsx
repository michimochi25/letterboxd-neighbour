import { useState } from "react";
import "./App.css";
import { Input } from "./components/ui/input";
import { Button } from "./components/ui/button";
import { Spinner } from "./components/ui/spinner";
import { Card } from "./components/Card";
import { StackedBar } from "./components/StackedBar";
import { cn } from "./lib/utils";
import type { Data } from "./types";
import { DisagreeRow } from "./components/DisagreeRow";

function App() {
  const [user1, setUser1] = useState<string>("");
  const [user2, setUser2] = useState<string>("");
  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCompare = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    if (!user1 || !user2) {
      setError("Please enter two usernames.");
      return;
    }

    setError("");
    setData(null);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/compare", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user1: user1,
          user2: user2,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Comparison failed");
      }

      const realData = await response.json();
      console.log(realData);
      setData(realData);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center p-6 gap-10">
      <header className="flex flex-col items-center gap-3">
        <h1 className="font-bold text-6xl text-white text-center">
          Letterboxd Neighbour
        </h1>
        <p className="text-xl text-center text-slate-400">
          Measure film taste between two Letterboxd users.
        </p>
      </header>

      {/* Input section */}
      <section className="mt-6 gap-2 flex flex-col items-center w-full">
        <div className="w-full flex flex-col items-center gap-4 md:flex-row md:gap-8">
          <Input
            placeholder="Username 1"
            className="w-1/2 border-gray-400"
            onChange={(e) => setUser1(e.target.value.trim())}
          />
          <h1>vs.</h1>
          <Input
            placeholder="Username 2"
            className="w-1/2 border-gray-400"
            onChange={(e) => setUser2(e.target.value.trim())}
          />
        </div>
        <Button
          className="mt-5 h-10 w-1/2 bg-gray-700 text-white hover:cursor-pointer hover:bg-gray-700/90"
          onClick={(e) => {
            handleCompare(e);
          }}
        >
          Compare Users
        </Button>
        <p className="text-slate-500">
          *this might take a while if users logged too many movies
        </p>
      </section>

      {/* Result section */}
      <section className="flex flex-col items-center justify-center w-full">
        {error && <p className="text-red-500">{error}</p>}
        {loading && (
          <div className="flex flex-col items-center justify-center">
            <Spinner className="size-8" />
            <p>Fetching results...</p>
          </div>
        )}
        {data && (
          <div className="flex flex-col gap-7 w-full">
            <div className="flex w-full gap-10 flex-col md:flex-row justify-center items-center">
              <div
                className={cn(
                  "p-10 w-fit aspect-square flex flex-col items-center justify-center gap-1 rounded-full place-self-center",
                  // Percentage 0-30 -> orange
                  data.metrics.finalScore <= 30 && "bg-[#ff8000]",
                  // Percentage 31-60 -> green
                  data.metrics.finalScore > 30 &&
                    data.metrics.finalScore <= 60 &&
                    "bg-[#00e054]",
                  // Percentage 61-100 -> blue
                  data.metrics.finalScore > 60 && "bg-[#40bcf4]"
                )}
              >
                <h1 className="font-bold text-xl">Overall Score</h1>
                <h2 className="font-bold text-7xl">
                  {data.metrics.finalScore}%
                </h2>
              </div>
              <div className="grid md:grid-rows-2 flex gap-3">
                <Card
                  className={cn(
                    "w-full flex flex-col items-center gap-1",
                    // Percentage 0-30 -> orange
                    data.metrics.tasteMatch <= 30 && "bg-[#ff8000]",
                    // Percentage 31-60 -> green
                    data.metrics.tasteMatch > 30 &&
                      data.metrics.tasteMatch <= 60 &&
                      "bg-[#00e054]",
                    // Percentage 61-100 -> blue
                    data.metrics.tasteMatch > 60 && "bg-[#40bcf4]"
                  )}
                >
                  <h1 className="font-bold text-xl">Taste Match</h1>
                  <h2 className="font-bold text-7xl text-(--primary)">
                    {data.metrics.tasteMatch}%
                  </h2>
                </Card>
                <Card
                  className={cn(
                    "w-full flex flex-col items-center gap-1",
                    // Percentage 0-30 -> orange
                    data.metrics.libraryOverlap <= 30 && "bg-[#ff8000]",
                    // Percentage 31-60 -> green
                    data.metrics.libraryOverlap > 30 &&
                      data.metrics.libraryOverlap <= 60 &&
                      "bg-[#00e054]",
                    // Percentage 61-100 -> blue
                    data.metrics.libraryOverlap > 60 && "bg-[#40bcf4]"
                  )}
                >
                  <h1 className="font-bold text-xl">Library Overlap</h1>
                  <h2 className="font-bold text-7xl text-(--primary)">
                    {data.metrics.libraryOverlap}%
                  </h2>
                </Card>
              </div>
            </div>

            <div className="w-full flex justify-center flex-col items-center">
              <h1 className="font-bold text-2xl mb-2">Common Movies</h1>
              <StackedBar
                data={[
                  {
                    label: `${data.users[0]}'s only`,
                    value:
                      data.metrics.totalWatched[0] - data.metrics.sharedCount,
                    color: "bg-[#ff8000]",
                  },
                  {
                    label: "Common",
                    value: data.metrics.sharedCount,
                    color: "bg-[#00e054]",
                  },
                  {
                    label: `${data.users[1]}'s only`,
                    value:
                      data.metrics.totalWatched[1] - data.metrics.sharedCount,
                    color: "bg-[#40bcf4]",
                  },
                ]}
              />
            </div>

            {/* Top 3 Disagreement */}
            <div className="w-full max-w-2xl p-4 space-y-4 rounded-lg shadow-sm border border-gray-100">
              <h1 className="font-bold text-2xl mb-4 text-center">
                Top 3 Disagreements
              </h1>
              {data.controversialMovies.length > 0 && (
                <>
                  <div className="w-full grid grid-cols-3 justify-items-center items-center gap-4 p-2 border-b border-gray-200">
                    <span className="font-bold">Movie</span>
                    <a
                      href={`https://letterboxd.com/${data.users[0]}`}
                      target="_blank"
                      className="font-bold"
                    >
                      {data.users[0]}'s Rating
                    </a>
                    <a
                      href={`https://letterboxd.com/${data.users[1]}`}
                      target="_blank"
                      className="font-bold"
                    >
                      {data.users[1]}'s Rating
                    </a>
                  </div>
                  {data.controversialMovies.map((movie, index) => {
                    return (
                      <DisagreeRow
                        key={index}
                        title={movie.title}
                        u1Rating={movie.u1Rating}
                        u2Rating={movie.u2Rating}
                      />
                    );
                  })}
                </>
              )}
              {data.controversialMovies.length === 0 && (
                <p className="text-center">
                  No significant disagreements found! You two seem to have very
                  similar tastes.
                </p>
              )}
            </div>
          </div>
        )}
      </section>
      <footer>
        Made by{" "}
        <a href="https://letterboxd.com/JalanKotak/" target="_blank">
          JalanKotak
        </a>
      </footer>
    </div>
  );
}

export default App;
