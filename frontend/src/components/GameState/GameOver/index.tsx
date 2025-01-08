import { useEffect } from "react";
import { State } from "../../../types";

import useSound from "use-sound";

interface GameOverProps {
  state: State;
  role: string;
}

export default function GameOver({ state, role }: GameOverProps) {
  const [playThemeSong, { stop }] = useSound("/sounds/themesong.mp3", {
    loop: true,
    volume: 0.5,
  });

  useEffect(() => {
    if (role === "viewer") {
      playThemeSong();
    }
  }, [state, playThemeSong, role]);

  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-left space-y-24">
        <div className="space-y-6">
          <img src="/images/seiounaosei.svg" className="w-[40rem] m-auto" />
          <h1 className="uppercase text-accent text-8xl font-extrabold text-center">
            Winners
          </h1>
        </div>
        <ol className="list-decimal uppercase text-xl">
          {state?.players
            ?.sort((a, b) => b.balance - a.balance)
            .map((p, idx) => (
              <li
                key={idx}
                className={`${idx == 0 && "text-8xl"} ${idx == 1 && "text-7xl"} ${idx == 2 && "text-6xl"} text-5xl my-2 flex place-content-between space-x-32`}
              >
                <b>{p.name}</b>
                <span>{p.balance} tokens</span>
              </li>
            ))}
        </ol>
      </div>
    </div>
  );
}
