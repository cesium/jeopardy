"use client";

import { useEffect, useState } from "react";

import * as api from "../../lib/api";

import { Player } from "../../types";

export default function Winners() {
  const [winners, setWinners] = useState<Player[]>([]);
  useEffect(() => {
    api.getWinners().then((w) => setWinners(w.sort((a,b) => b.balance - a.balance)));
  }, []);
  return (
    <div className="flex background h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-5xl font-bold text-center mb-12">Vencedores</h1>
        <ol className="list-decimal">
          {winners.map((w, idx) => (
            <li key={idx} className="text-lg">
              {w.name} : {w.balance} tokens
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
