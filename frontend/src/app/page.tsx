"use client";

import { useEffect, useState } from "react";
import useSound from "use-sound";

import { State } from "../types.js";

import GameState from "../components/GameState";

//const socket = io('http://192.168.1.200:8001');

const Viewer = () => {
  //In order to play sound, the user must interact with the page. We force this
  // by making the user click a button before showing the game state
  const [interacted, setInteracted] = useState<boolean>(false);

  const [state, setState] = useState<State>(null);

  useEffect(() => {
    const socket = new WebSocket(process.env.NEXT_PUBLIC_WS_URL);

    socket.addEventListener("message", (event) => {
      const newState: State = JSON.parse(event.data);
      setState(newState);
    });
  }, []);

  return (
    <div className="flex flex-col w-screen h-screen">
      {!interacted && (
        <div className="absolute w-screen h-screen flex items-center justify-center">
          <button
            className="text-white bg-accent rounded-sm mt-12 py-2 px-4 text-3xl font-extrabold w-fit"
            onClick={() => setInteracted(true)}
          >
            JOGAR
          </button>
        </div>
      )}
      {interacted && state != null && <GameState state={state} role="viewer" />}
    </div>
  );
};

export default Viewer;
