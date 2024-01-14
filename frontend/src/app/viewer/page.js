"use client";

import { useEffect, useState } from "react";

import GameState from "@/components/GameState";

//const socket = io('http://localhost:8001');

export default function Viewer() {
    const [state, setState] = useState({});

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8001")

        socket.addEventListener("message", event => {
            setState(JSON.parse(event.data));
        });
    }, []);

    return (
        <GameState state={state} role="viewer"/>
    );
};