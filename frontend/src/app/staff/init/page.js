"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import * as api from "@/lib/api";

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

export default function Init() {
  const router = useRouter();
  const [names, setNames] = useState(["", "", "", ""]);

  const updateNames = (n, i) => {
    let newNames = [...names];
    newNames[i] = n;
    setNames(newNames);
  };

  const submit = () => {
    api.setPlayers(names).then((_) => router.push("/staff"));
  };

  return (
    <div className="flex background h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-center text-5xl font-bold mb-8">
          Selecionar Jogadores
        </h1>
        {[0, 1, 2, 3].map((i) => (
          <PlayerInput key={i} id={i + 1} onChange={(n) => updateNames(n, i)} />
        ))}
        <button
          className="py-4 w-full m-auto mt-8 bg-green-700"
          onClick={(_) => submit()}
        >
          Start
        </button>
      </div>
    </div>
  );
}
