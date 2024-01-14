"use client";

import { useEffect, useState } from "react";
import io from "socket.io-client";

import GameState from "@/components/GameState";

const socket = io('http://localhost:8001', {transports: ["websocket"],});

export default function Host() {
    const [state, setState] = useState("");

    useEffect(() => {
        socket.on((message) => {
            alert(message);
            setState(message);
        });
    }, []);

    return (
        <GameState state={state} role="host"/>
    );
};