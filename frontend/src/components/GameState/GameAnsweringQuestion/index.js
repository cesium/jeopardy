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
    <div>
      {state.state == 3 && (
        <CountdownTimer initialSeconds={30} refreshRate={60} />
      )}
      Answering Question
    </div>
  );
}
