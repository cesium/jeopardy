"use client";

export default function Home({ params }) {
  return (
    <main className="quadro">
      <div className="coluna">
        <h1 className="tile">{JSON.stringify(params)}</h1>
      </div>
    </main>
  );
}
