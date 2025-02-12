"use client";

import { useEffect, useState } from "react";

import { State } from "../../../types";

import * as api from "../../../lib/api";
import useSound from "use-sound";

interface GameWaitingProps {
  state: State;
  role: "viewer" | "staff" | "host";
}

function PlayerInput({ id, onChange }) {
  return (
    <div className="my-8">
      <input
        type="text"
        placeholder={`Jogador ${id}`}
        className="w-full py-2 text-black px-1"
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

function GameWaitingNonStaff({ state, role }: GameWaitingProps) {
  const [playThemeSong, { stop: stopThemeSong, pause: pauseThemeSong }] =
    useSound("/sounds/themesong.mp3", {
      loop: true,
      volume: 0.5,
      interrupt: true,
    });
  const [playWalkInSong, { stop: stopWalkInSong }] = useSound(
    "/sounds/walkin.mp3",
    {
      volume: 1,
      interrupt: true,
    }
  );

  useEffect(() => {
    if (role === "viewer") {
      if (state.actions.playThemeSong) playThemeSong();
      if (state.actions.playWalkInSong) {
        pauseThemeSong();
        playWalkInSong();
      } else {
        stopWalkInSong();
        playThemeSong();
      }
    }
    if (state.state !== 0) stopThemeSong();
  }, [
    state,
    playThemeSong,
    stopThemeSong,
    role,
    playWalkInSong,
    stopWalkInSong,
    pauseThemeSong,
  ]);

  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-center">
        <video className="w-full" autoPlay muted loop>
          <source src="videos/logo.mp4" type="video/mp4" />
        </video>
      </div>
    </div>
  );
}

function GameWaitingStaff({ state }: GameWaitingProps) {
  const [names, setNames] = useState<string[]>(["", "", "", ""]);

  const updateNames = (n: string, i: number) => {
    let newNames = [...names];
    newNames[i] = n;
    setNames(newNames);
  };

  const submit = () => {
    api.setTeams(names.map((n) => n.split(";")));
  };
  const handlePlayWalkInSong = () => {
    api.playWalkInSong();
  };
  const handleStopWalkInSong = () => {
    api.stopWalkInSong();
  };

  return (
    <div className="flex h-screen w-screen items-center justify-center text-white">
      <div className="block space-y-4">
        <h1 className="text-center uppercase text-5xl font-bold mb-8">
          Selecionar Jogadores
        </h1>
        {[0, 1, 2, 3].map((i) => (
          <PlayerInput key={i} id={i + 1} onChange={(n) => updateNames(n, i)} />
        ))}
        <button
          className="py-4 w-full m-auto mt-8 bg-green-700 uppercase text-xl rounded-sm"
          onClick={() => submit()}
        >
          Start
        </button>
        <div className="flex flex-col gap-2 justify-center font-semibold">
          <button
            onClick={() => handlePlayWalkInSong()}
            className="bg-accent p-1 w-full"
          >
            Play Walk In Song
          </button>
          <button
            onClick={() => handleStopWalkInSong()}
            className="bg-red-700 w-full p-1"
          >
            Stop Walk In Song
          </button>
        </div>
      </div>
    </div>
  );
}

export default function GameWaiting({ state, role }: GameWaitingProps) {
  if (role == "staff") return <GameWaitingStaff state={state} role={role} />;
  else return <GameWaitingNonStaff state={state} role={role} />;
}
