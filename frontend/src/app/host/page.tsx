"use client";

import { useEffect, useState } from "react";

import GameState from "../../components/GameState";

import { State } from "../../types";

export default function Host() {
  const [state, setState] = useState<State>(null);

  useEffect(() => {
    const socket = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    socket.addEventListener("message", (event) => {
      const newState = JSON.parse(event.data);
      setState(newState);
    });
  }, []);

  return state && <GameState state={state} role="host" />;
}
