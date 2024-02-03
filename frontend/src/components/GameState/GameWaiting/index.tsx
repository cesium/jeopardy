"use client";

import { useState } from "react";

import { State } from "../../../types";

import * as api from "../../../lib/api";

interface GameWaitingProps {
  state: State;
  role: string;
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

function GameWaitingNonStaff({ state }: GameWaitingProps) {
  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-center">
        <h1 className="uppercase text-accent text-8xl font-extrabold mb-12">
          SEI OU NÃO SEI
        </h1>
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
    api.setPlayers(names);
  };

  return (
    <div className="flex h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-center uppercase text-5xl font-bold mb-8">
          Selecionar Jogadores
        </h1>
        {[0, 1, 2, 3].map((i) => (
          <PlayerInput key={i} id={i + 1} onChange={(n) => updateNames(n, i)} />
        ))}
        <button
          className="py-4 w-full m-auto mt-8 bg-green-700 uppercase text-xl"
          onClick={(_) => submit()}
        >
          Start
        </button>
      </div>
    </div>
  );
}

export default function GameWaiting({ state, role }: GameWaitingProps) {
  if (role == "staff") return <GameWaitingStaff state={state} role={role} />;
  else return <GameWaitingNonStaff state={state} role={role} />;
}
