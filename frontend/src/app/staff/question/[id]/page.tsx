"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import { useSound } from "use-sound";

import * as api from "../../../../lib/api";

export default function Question({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [playCorrectSound] = useSound("/sounds/correct.mp3", { interrupt: true });
  const [playWrongSound] = useSound("/sounds/end.mp3", { interrupt: true });

  const [started, setStarted] = useState(false);
  const [question, setQuestion] = useState({
    id: 0,
    statement: "",
    answer: "",
  });
  const id = params.id;

  useEffect(() => {
    api.getQuestion(id).then((q) => setQuestion(q));
  }, [id]);

  const startQuestion = () => {
    api.startQuestion().then((_) => setStarted(true));
  };

  const submit = (res) => {
    if (res) {
      playCorrectSound();
    }
    else {
      playWrongSound();
    }
    api.answer(res);
    setTimeout(() => router.push("/staff"), 5000);
  };

  return (
    <div className="flex background h-screen w-screen items-center justify-center">
      <div className="block text-white w-3/4">
        <h1 className="text-5xl font-bold">{question.statement}</h1>
        <h2 className="mt-12 text-xl font-bold">Resposta:</h2>
        <p className="text-3xl">{question.answer}</p>
        {started && (
          <div className="grid grid-cols-2 gap-4 mt-12">
            <button
              className="w-full bg-red-700 py-2 text-4xl"
              onClick={(_) => submit(false)}
            >
              Errado
            </button>
            <button
              className="w-full bg-green-700 py-2 text-4xl"
              onClick={(_) => submit(true)}
            >
              Certo
            </button>
          </div>
        )}
        {!started && (
          <div className="w-full flex content-center">
            <button
              className="w-1/2 m-auto mt-12 bg-yellow-700 py-2 text-4xl"
              onClick={(_) => startQuestion()}
            >
              Aceitar Buzz
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
