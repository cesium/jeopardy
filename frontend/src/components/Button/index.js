"use client";
import Link from "next/link";

export default function Button({ amount, link }) {
  return (
    <Link href={link}>
      <div className="tile">{amount}</div>
    </Link>
  );
}
