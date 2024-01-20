function processState(state) {
  const categories = [...new Set(state.questions.map((q) => q.category))];

  const questions = state.questions.sort((a, b) => {
    const res = a.value - b.value;
    if (res == 0) {
      return categories.indexOf(a.category) - categories.indexOf(b.category);
    } else {
      return res;
    }
  });

  return [categories, questions];
}

export default function GameSelectingQuestion({ state }) {
  const [categories, questionsPerAmount] = processState(state);
  console.log(questionsPerAmount);
  return (
    <div className="p-4 uppercase text-center">
      <div
        className={`grid gap-1 grid-cols-${categories.length} text-5xl font-extrabold`}
      >
        {categories.map((c, idx) => (
          <div className="bg-secondary mb-2 py-3" key={`cat-${idx}`}>
            {c}
          </div>
        ))}

        {questionsPerAmount.map((q, idx) => (
          <div
            className="bg-secondary text-accent py-7"
            key={`question-${idx}`}
          >
            {q.value}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-center mt-12">
        {state.players.map((p, idx) => (
          <div key={`player-${idx}`} className="mx-12">
            <p className="font-extrabold text-3xl">{p.name}</p>
            <p className="font-bold text-2xl mt-2">{p.balance}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
