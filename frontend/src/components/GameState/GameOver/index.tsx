import { useEffect } from "react";
import { State } from "../../../types";

import useSound from "use-sound";
import Image from "next/image";

interface GameOverProps {
  state: State;
  role: "viewer" | "staff" | "host";
  inView: boolean;
}

export default function GameOver({ state, role, inView }: GameOverProps) {
  const [playThemeSong] = useSound("/sounds/themesong.mp3", {
    loop: true,
    volume: 0.5,
  });

  function winningTeam() {
    const maxPoints = Math.max(...state.teams.map((t) => t.balance));
    return state.teams.find((t) => t.balance === maxPoints);
  }

  useEffect(() => {
    if (role === "viewer" && state.actions.playEndSound) {
      playThemeSong();
    }
  }, [state, playThemeSong, role]);

  return (
    <div
      className={`flex items-center h-screen justify-center text-white ${inView ? "opacity-100" : "opacity-0"} transition-opacity duration-500`}
    >
      <div className="block text-left space-y-16">
        <div className="space-y-6">
          <Image
            alt="seiounaosei_logo"
            width={500}
            height={500}
            src="/images/seiounaosei.png"
            className="w-[30rem] m-auto"
          />
          <h1 className="uppercase text-primary text-7xl font-extrabold text-center animate-pulse">
            Winners
          </h1>
        </div>
        <div className="uppercase text-xl">
          {state?.teams
            ?.sort((a, b) => b.balance - a.balance)
            .map((p, idx) => (
              <li
                key={idx + p.names.toString()}
                className={`${idx === 0 && "text-8xl animate-bounce text-primary"} ${idx === 1 && "text-7xl"} ${idx === 2 && "text-6xl"} ${idx === 3 && "text-5xl"} ${idx === 4 && "text-4xl"} ${idx === 5 && "text-3xl"} ${idx === 6 && "text-2xl"} ${idx === 7 && "text-xl"} my-2 flex place-content-between space-x-32`}
              >
                <div className="flex items-center gap-4 drop-shadow-lg">
                  {p.names.map((n, idx) => (
                    <div key={idx} className="flex items-center gap-4">
                      <b>{n}</b>
                      {idx < p.names.length - 1 && <b>+</b>}
                    </div>
                  ))}
                </div>
                <span>{p.balance} tokens</span>
              </li>
            ))}
        </div>
        <div className="space-y-16">
          <h1 className="text-7xl font-bold text-center uppercase text-primary animate-pulse">
            Final Earnings
          </h1>
          <div className="text-6xl uppercase space-y-2">
            {winningTeam().names.map((name, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <b>{name}</b>
                <p>
                  {Math.max(
                    state.SOSAnswers.every((a) => a)
                      ? 0
                      : state.SOSAnswers[idx]
                        ? winningTeam().balance
                        : state.SOSAnswers.some((a) => a)
                          ? 0
                          : Math.round(winningTeam().balance / 2),
                    0,
                  )}{" "}
                  TOKENS
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
