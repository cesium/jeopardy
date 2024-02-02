"use client";

import { useEffect, useState } from "react";

import { useRouter } from "next/navigation";

import * as api from "../../lib/api";

import Category from "../../components/Category";

import { Question, Player } from "../../types";

export default function Home() {
  const router = useRouter();

  const [categories, setCategories] = useState<Question[][]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  useEffect(() => {
    api.getQuestions().then((c) => setCategories(c));
    api.getPlayers().then((p) => setPlayers(p));
  }, []);

  useEffect(() => {
    const remaining = categories
      .map((c) => c.filter((q) => !q.answered).length)
      .reduce((s, a) => s + a, 0);

    if (remaining == 0 && categories.length > 0) router.push("/winners");
  }, [categories, router]);
  return (
    <main className="quadro">
      {categories.map((c, idx) => (
        <Category key={idx} name={c[0].category} questions={c} />
      ))}
      <div>
        {players.map((p, idx) => (
          <div key={idx}>
            {p.name}: {p.balance}
          </div>
        ))}
      </div>
    </main>
  );
}
