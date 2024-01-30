export default function GameOver({ state }) {
  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-center">
        <h1 className="uppercase text-accent text-5xl font-extrabold mb-12">
          Winners
        </h1>
        <ol className="list-decimal uppercase text-xl">
          {state?.players?.map((w, idx) => (
            <li key={idx} className="text-lg my-2">
              <b>{w.name}</b> : {w.balance} tokens
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
