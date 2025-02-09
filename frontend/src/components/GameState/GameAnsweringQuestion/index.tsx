import { useState, useEffect, useCallback } from "react";
import useSound from "use-sound";
import { State } from "../../../types";
import * as api from "../../../lib/api";

interface GameAnsweringQuestionProps {
  state: State;
  role: "viewer" | "staff" | "host";
  fadeOut: boolean;
  inView: boolean;
}

function CountdownTimer({ initialSeconds, refreshRate, role }) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [playEndSound] = useSound("/sounds/wrong.mp3", { interrupt: true });

  useEffect(() => setSeconds(initialSeconds), [initialSeconds]);

  useEffect(() => {
    if (seconds <= 0 && role === "viewer") {
      playEndSound();
      return;
    }

    // Set up the timer
    const timer = setInterval(() => {
      setSeconds((prevSeconds) => Math.max(0, prevSeconds - 1 / refreshRate));
    }, 1000.0 / refreshRate);

    // Clean up the timer
    return () => clearInterval(timer);
  }, [seconds, refreshRate, playEndSound, role]);

  const percentage = (seconds / initialSeconds) * 100;

  return (
    <div
      className={`fixed top-0 h-8 transition-colors ${percentage >= 50 ? "bg-accent" : percentage >= 20 ? "bg-amber-300" : "bg-red-700"}`}
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
  const [playTimerSound, { stop: timerStop }] = useSound("/sounds/timer.mp3", {
    interrupt: true,
    volume: 0.5,
  });
  const [playBuzzSound] = useSound("/sounds/buzz.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playCorrectSound] = useSound("/sounds/correct.mp3", {
    interrupt: true,
    volume: 1,
  });
  const [playWrongSound] = useSound("/sounds/wrong.mp3", {
    interrupt: true,
    volume: 1,
  });
  const [playStart] = useSound("/sounds/start.mp3", {
    interrupt: true,
    volume: 2,
  });
  const [playTension, { stop: tensionStop }] = useSound("/sounds/tension.mp3", {
    interrupt: true,
    volume: 0.5,
  });
  const [started, setStarted] = useState<boolean>(false);
  const [timerEnded, setTimerEnded] = useState<boolean>(false);

  const timer = useCallback(() => {
    if (state.state === 4) {
      const values = new Set(state.questions.map((q) => q.value));
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      const minTimer = 10;
      const maxTimer = 30;
      const currentValue = state.currentQuestion.value;
      const percentage = (currentValue - minValue) / (maxValue - minValue);
      return minTimer + percentage * (maxTimer - minTimer);
    }
    return 10;
  }, [state]);

  useEffect(() => {
    if (role === "viewer") {
      if (state.actions.playCorrectSound) {
        playCorrectSound();
      }
      if (state.actions.playWrongSound) {
        playWrongSound();
      }
      if (state.actions.playStartAccepting) {
        playStart();
        playTension();
        setTimeout(() => tensionStop(), timer() * 1000 + 1000);
      }
      if (state.actions.playBuzzerSound) {
        tensionStop();
        playBuzzSound();
        playTimerSound();
        setTimeout(
          () => {
            timerStop();
          },
          timer() * 1000 + 1000,
        );
      }
      if (state.actions.stopTimer || state.state !== 4) {
        timerStop();
      }
      if (state.state !== 3) {
        tensionStop();
      }
    }
    if (state.actions.playBuzzerSound) {
      setTimerEnded(false);
      setTimeout(() => {
        setTimerEnded(true);
      }, timer() * 1000);
    }
  }, [
    state,
    playCorrectSound,
    playWrongSound,
    playStart,
    playBuzzSound,
    playTimerSound,
    timerStop,
    role,
    timer,
    playTension,
    tensionStop,
  ]);

  const startQuestion = () => {
    api.startQuestion().then(() => setStarted(true));
  };
  const skipQuestion = () => {
    api.skipQuestion().then(() => {
      setTimeout(() => setStarted(false), 1000);
    });
  };
  const submit = async (res) => {
    api.answer(res).then(() => setStarted(false));
  };
  const stopTimer = async () => {
    api.stopTimer();
  };

  return (
    <div
      className={`w-screen h-screen transition-all duration-500 ${fadeOut ? "opacity-0" : "opacity-100"}`}
    >
      <div
        className={`${inView ? "opacity-100" : "opacity-0"} transition-all duration-500 w-full h-full flex flex-col items-center justify-center`}
      >
        {(state.state === 3 || state.state === 4) &&
          !state.actions.stopTimer && (
            <CountdownTimer
              role={role}
              initialSeconds={timer()}
              refreshRate={60}
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
            {state.actions.stopTimer ? (
              <>
                <div className="w-3/4 grid grid-cols-2 gap-4 mt-12 m-auto">
                  <button
                    className="w-full bg-red-700 py-2 text-4xl rounded-sm"
                    onClick={() => {
                      submit(false);
                    }}
                  >
                    Errado
                  </button>
                  <button
                    className="w-full bg-green-700 py-2 text-4xl rounded-sm"
                    onClick={() => {
                      submit(true);
                    }}
                  >
                    Certo
                  </button>
                </div>
              </>
            ) : (
              !timerEnded &&
              state.state === 4 && (
                <div className="w-3/4 mt-12 m-auto">
                  <button
                    className="w-full bg-accent py-2 text-4xl rounded-sm"
                    onClick={() => {
                      stopTimer();
                    }}
                  >
                    Respondeu
                  </button>
                </div>
              )
            )}
            <div className="w-full flex justify-center items-center">
              <button
                className="w-3/4 bg-amber-700 py-2 text-4xl mt-4 rounded-sm"
                onClick={() => {
                  skipQuestion();
                }}
              >
                Skip
              </button>
            </div>
          </>
        )}
        {role == "staff" && !started && (
          <div className="w-full flex content-center">
            <button
              className="w-1/2 m-auto mt-12 bg-yellow-700 py-2 text-4xl rounded-sm"
              onClick={() => startQuestion()}
            >
              Aceitar Buzz
            </button>
          </div>
        )}
        <div className="flex items-center justify-center my-24 text-center uppercase">
          {state.teams.map((p, idx) => (
            <div
              key={`team-${idx}`}
              className={`mx-12 ${state.state == 4 && state.currentTeam === idx ? "text-primary" : ""}`}
            >
              <div className="flex flex-col space-y-0.5">
                {p.names.map((name, index) => (
                  <p
                    key={index}
                    className={`font-extrabold text-4xl ${state.state === 4 && state.currentTeam === idx && "text-primary animate-bounce"}`}
                  >
                    {name}
                  </p>
                ))}
              </div>
              <p className="font-bold text-3xl mt-2">{p.balance}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
