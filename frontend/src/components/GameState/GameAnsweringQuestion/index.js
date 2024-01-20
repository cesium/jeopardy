import { useState, useEffect } from "react";

function CountdownTimer({ initialSeconds, refreshRate }) {
  const [seconds, setSeconds] = useState(initialSeconds);

  useEffect(() => {
    if (seconds <= 0) {
      return;
    }

    // Set up the timer
    const timer = setInterval(() => {
      setSeconds((prevSeconds) => prevSeconds - 1 / refreshRate);
    }, 1000.0 / refreshRate);

    // Clean up the timer
    return () => clearInterval(timer);
  }, [seconds, refreshRate]);

  const percentage = (seconds / initialSeconds) * 100;

  return (
    <div
      className={`fixed top-0 h-12 transition-colors ${percentage >= 50 ? "bg-green-700" : percentage >= 20 ? "bg-amber-300" : "bg-red-700"}`}
      style={{ width: percentage + "vw" }}
    ></div>
  );
}

export default function GameAnsweringQuestion({ state }) {
  return (
    <div className="flex flex-col items-center justify-center w-screen h-screen">
      {state.state == 3 && (
        <CountdownTimer initialSeconds={30} refreshRate={60} />
      )}
      <div className="my-24 text-center">
        <p className="font-extrabold text-3xl">
          {state.questions[state.currentQuestion].category}
        </p>
        <p className="font-bold text-2xl mt-2 text-accent">
          {state.questions[state.currentQuestion].value}
        </p>
      </div>
      <div className="uppercase grow items-center flex font-extrabold text-5xl w-3/4 text-center">
        {state.questions[state.currentQuestion].statement}
      </div>
      <div className="flex items-center justify-center my-24 text-center">
        {state.players.map((p, idx) => (
          <div key={`player-${idx}`} className="mx-12">
            <p className="font-extrabold text-3xl">{p.name}</p>
            <p className="font-bold text-2xl mt-2">{p.balance}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
