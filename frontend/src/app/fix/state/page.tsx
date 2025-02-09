"use client";

import { useState } from "react";
import * as api from "../../../lib/api";

function UserInput({ onChange }) {
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

export default function State() {
  const [state, setState] = useState<number>();

  const submit = () => {
    api.fixState(state);
  };

  const updateState = (n: number) => {
    setState(n);
  };

  return (
    <div className="flex h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-center uppercase text-5xl font-bold mb-8">
          Select State
        </h1>
        <UserInput onChange={(n) => updateState(n)} />
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
