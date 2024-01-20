"use client";

import { useEffect, useState } from "react";
import useSound from "use-sound";

import GameState from "@/components/GameState";

//const socket = io('http://localhost:8001');

export default function Viewer() {
  const [playStart] = useSound("/sounds/start.mp3", { interrupt: true });

  //In order to play sound, the user must interact with the page. We force this
  // by making the user click a button before showing the game state
  const [interacted, setInteracted] = useState(false);

  const [state, setState] = useState({});
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8001");

    socket.addEventListener("message", (event) => {
      const newState = JSON.parse(event.data);
      setState(newState);
    });
  }, []);

  useEffect(() => {
    console.log(state);
    if (state.state == 3) playStart();
  }, [state, playStart]);

  return (
    <>
      {!interacted && (
        <button
          className="text-white bg-accent m-auto block mt-12 py-2 px-4 text-3xl font-extrabold"
          onClick={(_) => setInteracted(true)}
        >
          JOGAR
        </button>
      )}
      {interacted && <GameState state={state} />}
    </>
  );
}
