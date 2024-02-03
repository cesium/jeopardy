import { useState, useEffect } from "react";

import useSound from "use-sound";

import { State } from "../../../types";

import * as api from "../../../lib/api";

interface GameAnsweringQuestionProps {
  state: State;
  role: string;
}

function CountdownTimer({ initialSeconds, refreshRate, endSound }) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [playEndSound] = useSound("/sounds/end.mp3", { interrupt: true });

  useEffect(() => {
    if (seconds <= 0) {
      if (endSound) playEndSound();
      return;
    }

    // Set up the timer
    const timer = setInterval(() => {
      setSeconds((prevSeconds) => Math.max(0, prevSeconds - 1 / refreshRate));
    }, 1000.0 / refreshRate);

    // Clean up the timer
    return () => clearInterval(timer);
  }, [seconds, refreshRate, endSound, playEndSound]); //TODO: Test dependencies

  const percentage = (seconds / initialSeconds) * 100;

  return (
    <div
      className={`fixed top-0 h-12 transition-colors ${percentage >= 50 ? "bg-green-700" : percentage >= 20 ? "bg-amber-300" : "bg-red-700"}`}
      style={{ width: percentage + "vw" }}
    ></div>
  );
}

export default function GameAnsweringQuestion({
  state,
  role,
}: GameAnsweringQuestionProps) {
  const [playTimerSound, { stop }] = useSound("/sounds/timer.mp3", {
    interrupt: true,
  });
  const [playBuzzSound] = useSound("/sounds/buzz.mp3", { interrupt: true });
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (state.state == 4) {
      playBuzzSound();
      setTimeout(() => playTimerSound(), 500);
      setTimeout(() => stop(), 15500);
    } else stop();
  }, [state]);

  const startQuestion = () => {
    api.startQuestion().then((_) => setStarted(true));
  };

  const skipQuestion = () => {
    api.skipQuestion();
  };

  const submit = (res) => {
    api.answer(res);
  };

  return (
    <div className="flex flex-col items-center justify-center w-screen h-screen">
      {(state.state == 3 || state.state == 4) && (
        <CountdownTimer
          initialSeconds={state.state == 4 ? 7 : 10}
          refreshRate={60}
          endSound={role == "viewer"}
        />
      )}
      <div className="my-24 text-center">
        <p className="font-extrabold text-3xl uppercase">
          {state.currentQuestion.category}
        </p>
        <p className="font-bold text-3xl mt-2 text-accent">
          {state.currentQuestion.value}
        </p>
      </div>
      <div className="uppercase grow items-center flex font-extrabold text-6xl w-3/4 text-center">
        {state.currentQuestion.statement}
      </div>
      {role != "viewer" && (
        <div className="uppercase grow items-center flex font-extrabold text-2xl text-accent w-3/4 text-center">
          {state.currentQuestion.answer}
        </div>
      )}
      {role == "staff" && started && (
        <>
          <div className="w-3/4 grid grid-cols-2 gap-4 mt-12">
            <button
              className="w-full bg-red-700 py-2 text-4xl"
              onClick={(_) => submit(false)}
            >
              Errado
            </button>
            <button
              className="w-full bg-green-700 py-2 text-4xl"
              onClick={(_) => submit(true)}
            >
              Certo
            </button>
          </div>
          <button
            className="w-3/4 bg-amber-700 py-2 text-4xl mt-8"
            onClick={(_) => skipQuestion()}
          >
            Skip
          </button>
        </>
      )}
      {role == "staff" && !started && (
        <div className="w-full flex content-center">
          <button
            className="w-1/2 m-auto mt-12 bg-yellow-700 py-2 text-4xl"
            onClick={(_) => startQuestion()}
          >
            Aceitar Buzz
          </button>
        </div>
      )}
      <div className="flex items-center justify-center my-24 text-center">
        {state.players.map((p, idx) => (
          <div
            key={`player-${idx}`}
            className={`mx-12 ${state.state == 4 && state.currentPlayer.name == p.name ? "text-accent" : ""}`}
          >
            <p className="font-extrabold text-4xl">{p.name}</p>
            <p className="font-bold text-3xl mt-2">{p.balance}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
