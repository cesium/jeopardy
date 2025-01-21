import { useState, useEffect } from "react";
import useSound from "use-sound";
import { State } from "../../../types";
import * as api from "../../../lib/api";

interface GameAnsweringQuestionProps {
  state: State;
  role: string;
  fadeOut: boolean;
  inView: boolean;
}

function CountdownTimer({ initialSeconds, refreshRate, endSound }) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [playEndSound] = useSound("/sounds/wrong.mp3", { interrupt: true });

  useEffect(() => setSeconds(initialSeconds), [initialSeconds]);

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
  }, [seconds, refreshRate, endSound, playEndSound]);

  const percentage = (seconds / initialSeconds) * 100;

  return (
    <div
      className={`fixed top-0 h-8 transition-colors ${percentage >= 50 ? "bg-green-700" : percentage >= 20 ? "bg-amber-300" : "bg-red-700"}`}
      style={{ width: percentage + "vw" }}
    ></div>
  );
}

export default function GameAnsweringQuestion({
  state,
  role,
  fadeOut,
  inView,
}: GameAnsweringQuestionProps) {
  const [playTimerSound, { stop }] = useSound("/sounds/timer.mp3", {
    interrupt: true,
    volume: 3,
  });
  const [playBuzzSound] = useSound("/sounds/buzz.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playCorrectSound] = useSound("/sounds/correct.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playWrongSound] = useSound("/sounds/wrong.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playStart] = useSound("/sounds/start.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [started, setStarted] = useState<boolean>(false);

  useEffect(() => {
    if (role === "viewer" && state.state === 4) {
      playBuzzSound();
      setTimeout(() => playTimerSound(), 500);
      setTimeout(() => stop(), 7000);
    } else stop();
  }, [state, playBuzzSound, role, playTimerSound, stop]);

  useEffect(() => {
    if (state && state.state === 3) playStart();
  }, [state, playStart]);

  useEffect(() => {
    if (role === "viewer") {
      if (state.playCorrectSound) {
        playCorrectSound();
      }
      if (state.playWrongSound) {
        playWrongSound();
      }
    }
  }, [state, playCorrectSound, playWrongSound, role]);

  const startQuestion = () => {
    api.startQuestion().then((_) => setStarted(true));
  };
  const skipQuestion = () => {
    api.skipQuestion().then((_) => setStarted(false));
  };
  const submit = async (res) => {
    api.answer(res).then((_) => setStarted(false));
  };

  return (
    <div
      className={`w-screen h-screen transition-all duration-500 ${fadeOut ? "opacity-0" : "opacity-100"}`}
    >
      <div
        className={`${inView ? "opacity-100" : "opacity-0"} transition-all duration-500 w-full h-full flex flex-col items-center justify-center`}
      >
        {(state.state === 3 || state.state === 4) && (
          <CountdownTimer
            initialSeconds={state.state === 4 ? 7 : 10}
            refreshRate={60}
            endSound={role === "viewer"}
          />
        )}
        <div className="my-24 text-center">
          <p className="font-extrabold text-3xl uppercase">
            {state.currentQuestion.category}
          </p>
          <p className="font-bold text-3xl mt-2 text-primary">
            {state.currentQuestion.value}
          </p>
        </div>
        <div className="uppercase grow items-center flex flex-col font-extrabold w-[80vw] text-center space-y-16">
          {state.currentQuestion.image &&
            state.currentQuestion.image !== "" && (
              <img
                src={`/images/questions/${state.currentQuestion.image}`}
                alt="Question Image"
                className={`${role === "staff" ? "h-[16rem]" : "h-[26rem]"} rounded-xl`}
              />
            )}
          <p
            className={`w-fit m-auto ${state.currentQuestion.image !== "" ? "text-4xl" : "text-6xl"}`}
          >
            {state.currentQuestion.statement}
          </p>
        </div>
        {role !== "viewer" && (
          <div className="uppercase font-extrabold text-2xl text-primary w-full text-center pt-10">
            <u>RESPOSTA:</u> {state.currentQuestion.answer}
          </div>
        )}
        {role === "staff" && started && (
          <>
            <div className="w-3/4 grid grid-cols-2 gap-4 mt-12 m-auto">
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
            <div className="w-full flex justify-center items-center">
              <button
                className="w-3/4 bg-amber-700 py-2 text-4xl mt-4"
                onClick={(_) => skipQuestion()}
              >
                Skip
              </button>
            </div>
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
        <div className="flex items-center justify-center my-24 text-center uppercase">
          {state.players.map((p, idx) => (
            <div
              key={`player-${idx}`}
              className={`mx-12 ${state.state == 4 && state.currentPlayer.name == p.name ? "text-primary" : ""}`}
            >
              <p className="font-extrabold text-4xl">{p.name}</p>
              <p className="font-bold text-3xl mt-2">{p.balance}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
