import { useEffect } from "react";
import { State } from "../../../types";

import useSound from "use-sound";

interface GameOverProps {
  state: State;
  role: string;
}

export default function GameOver({ state, role }: GameOverProps) {
  const [playThemeSong, {stop}] = useSound("/sounds/themesong.mp3", { loop: true, volume: 0.5 });

  useEffect(() => {
    playThemeSong();
    if (state.state != 5 && role == "viewer") {
      stop();
    }
  }, [state]);

  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-left space-y-24">
        <h1 className="uppercase text-accent text-8xl font-extrabold text-center">
          Winners
        </h1>
        <ol className="list-decimal uppercase text-xl">
          {state?.players
            ?.sort((a, b) => b.balance - a.balance)
            .map((p, idx) => (
              <li key={idx} className="text-lg my-2">
                <b>{p.name}</b> : {p.balance} tokens
              </li>
            ))}
        </ol>
      </div>
    </div>
  );
}
