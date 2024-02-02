"use client";

import { useRouter } from "next/navigation";

import * as api from "../../lib/api";

interface ButtonProps {
  id: number;
  amount: number;
  link: string;
  enabled: boolean;
}

export default function Button({ id, amount, link, enabled }: ButtonProps) {
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
