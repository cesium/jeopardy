"use client";

import { useState } from "react";
import * as api from "../../../lib/api";


function PlayerInput({ onChange }) {
  return (
    <div className="my-8">
      <input
        type="number"
        placeholder={`0`}
        className="w-full py-2 text-black px-1"
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default function Selecting() {
  const [team, setTeam] = useState<number>();

  const submit = () => {
    api.fixSelectingTeam(team);
  };

  const updateTeam = (n: number) => {
    setTeam(n);
  };

  

  return (
    <div className="flex h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-center uppercase text-5xl font-bold mb-8">
          Select Team
        </h1>
        <PlayerInput onChange={(n) => updateTeam(n)} />
        <button
          className="py-4 w-full m-auto mt-8 bg-green-700 uppercase text-xl"
          onClick={(_) => submit()}
        >
          Submit
        </button>
      </div>
    </div>
  );
}