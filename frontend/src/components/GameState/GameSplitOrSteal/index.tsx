import { State } from "../../../types";
import * as api from "../../../lib/api";
import { useEffect, useState } from "react";
import useSound from "use-sound";

export default function GameSplitOrSteal({
  state,
  role,
  inView,
}: {
  state: State;
  role: "viewer" | "staff" | "host";
  inView: boolean;
}) {
  const [started, setStarted] = useState<boolean>(false);
  const [showSOSResults, setShowSOSResults] = useState<boolean>(false);
  const [fadeOut, setFadeOut] = useState<boolean>(false);
  const [fadeIn, setFadeIn] = useState<boolean>(false);
  const [countDown, setCountDown] = useState<number>(5);
  const [fadeReveal, setFadeReveal] = useState<boolean>(false);

  const [playBuzzSound] = useSound("/sounds/buzz.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playStart] = useSound("/sounds/start.mp3", {
    interrupt: true,
    volume: 2,
  });

  const fight = () => {
    api.startQuestion().then(() => setStarted(true));
  };

  const results = () => {
    api.showSOSResults().then(() => setShowSOSResults(true));
  };

  const endGame = () => {
    api.endGame();
  };

  function winningTeam() {
    const maxPoints = Math.max(...state.teams.map((t) => t.balance));
    return state.teams.find((t) => t.balance === maxPoints);
  }

  useEffect(() => {
    if (role === "viewer") {
      if (state.actions.playBuzzerSound) {
        playBuzzSound();
      }
      if (state.actions.playStartAccepting) {
        playStart();
      }
    }
  }, [playBuzzSound, playStart, role, state.actions]);

  useEffect(() => {
    let active = true;

    if (state.actions.playStartAccepting) setStarted(true);
    if (state.actions.showSOS) {
      setFadeOut(true);
      setTimeout(() => {
        setFadeIn(true);
      }, 500);
      setTimeout(() => {
        setShowSOSResults(true);
        if (active) {
          setInterval(() => {
            if (countDown < 0) return;
            setCountDown((prev) => prev - 1);
          }, 950);
        }
      }, 1000);
      setTimeout(() => {
        setFadeReveal(true);
      }, 7000);
    }

    return () => {
      active = false;
    };
  }, [state.actions, countDown]);

  return (
    <div
      className={`flex flex-col items-center justify-center h-screen gap-10 transition-all duration-500 ${inView ? "opacity-100" : "opacity-0"}`}
    >
      {(role === "staff" || !showSOSResults) && (
        <span
          className={`flex items-center gap-8 pl-10 drop-shadow-lg ${started ? "text-9xl" : "text-[16rem]"}`}
        >
          <h1>SPLIT</h1>{" "}
          <h2 className={`${started ? "text-6xl" : "text-9xl"}`}>OR</h2>{" "}
          <h1>STEAL</h1>
        </span>
      )}
      {role === "staff" ? (
        <>
          {started && !showSOSResults && (
            <div className="grid grid-cols-2 p-10 gap-10 w-1/2 h-64">
              {winningTeam().names.map((name, idx) => (
                <div
                  key={idx}
                  className={`bg-gradient-to-br ${state.SOSAnswers[idx] !== null ? "from-accent/90 to-accent/40" : "from-accent/10 to-accent/5 ring-2 ring-accent/20"} backdrop-blur-md rounded-2xl flex justify-center items-center text-6xl flex-col gap-4`}
                >
                  <p>{name}</p>
                  {state.SOSAnswers[idx] !== null && (
                    <b className="underline">
                      {state.SOSAnswers[idx] ? "STEAL" : "SPLIT"}
                    </b>
                  )}
                </div>
              ))}
            </div>
          )}
          {!started ? (
            <button
              onClick={fight}
              className="uppercase p-2 w-96 bg-accent text-3xl font-bold rounded-sm"
            >
              Aceitar Buzzer
            </button>
          ) : !showSOSResults ? (
            <button
              onClick={results}
              className="uppercase p-2 w-96 bg-accent text-3xl font-bold rounded-sm"
            >
              Mostrar Resultados
            </button>
          ) : (
            <button
              onClick={endGame}
              className="uppercase p-2 w-96 bg-accent hover:bg-red-500 transition-all text-3xl font-bold rounded-sm"
            >
              Terminar Jogo (Mostrar Winners)
            </button>
          )}
        </>
      ) : (
        <>
          {started && !showSOSResults && (
            <div
              className={`h-full w-full grid grid-cols-2 gap-10 p-10 transition-all duration-500 ${fadeOut ? "opacity-0" : "opacity-100"}`}
            >
              {winningTeam().names.map((name, idx) => (
                <div
                  key={idx}
                  className={`bg-gradient-to-br ${state.SOSAnswers[idx] !== null ? "from-accent/90 to-accent/40 shadow-2xl shadow-accent/30" : "from-accent/10 to-accent/5 ring-2 ring-accent/20"} transition-all duration-300 backdrop-blur-md rounded-2xl flex justify-center items-center text-6xl drop-shadow-md`}
                >
                  {name}
                </div>
              ))}
            </div>
          )}
          {showSOSResults && countDown >= 0 && (
            <div
              className={`${fadeIn ? "opacity-100" : "opacity-0"} transition-all duration-500 text-[40rem] animate-ping`}
            >
              {countDown}
            </div>
          )}
          {showSOSResults && countDown < 0 && (
            <div
              className={`w-full h-full flex flex-col justify-center items-center bg-accent/50 drop-shadow-lg text-9xl ${state.SOSAnswers.filter((r) => r).length === 1 || state.SOSAnswers.every((r) => r) ? "bg-red-700/50" : "bg-green-700/50"} ${fadeReveal ? "opacity-100" : "opacity-0"} transition-all duration-1000`}
            >
              <div className="flex gap-10 items-center">
                {state.SOSAnswers.filter((r) => r).length === 1 && (
                  <p>
                    {winningTeam().names.find(
                      (_, idx) => state.SOSAnswers[idx],
                    )}
                  </p>
                )}
              </div>
              <h1 className="text-[16rem] animate-pulse text-center">
                {state.SOSAnswers.every((r) => r)
                  ? "BOTH STOLE!"
                  : state.SOSAnswers.filter((r) => r).length === 1
                    ? "STOLE!"
                    : "BOTH SPLITTED!"}
              </h1>
            </div>
          )}
        </>
      )}
    </div>
  );
}
