"use client";

import { useEffect, useState } from "react";
import useSound from "use-sound";

import { State } from "../../types.js";

import GameState from "../../components/GameState";

const Staff = () => {
  const [state, setState] = useState<State>(null);

  useEffect(() => {
    const socket = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    socket.addEventListener("message", (event) => {
      const newState: State = JSON.parse(event.data);
      setState(newState);
    });
  }, []);

  return state != null && <GameState state={state} role="staff" />;
};

export default Staff;
