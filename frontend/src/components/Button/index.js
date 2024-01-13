"use client";

import { useRouter } from "next/navigation";

import * as api from "@/lib/api";

export default function Button({ id, amount, link, enabled }) {
  const router = useRouter();
  const onClick = () => {
    api.setQuestion(id).then((_) => router.push(link));
  };

  return (
    <button onClick={(_) => onClick()} disabled={!enabled}>
      <div className="tile">{amount}</div>
    </button>
  );
}
