"use client";

import { useEffect, useState } from "react";

import GameState from "@/components/GameState";

export default function Host() {
  const [state, setState] = useState("");

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8001");

    socket.addEventListener("message", (event) => {
      const newState = JSON.parse(event.data);
      setState(newState);
    });
  }, []);

  return <GameState state={state} role="host" />;
}
