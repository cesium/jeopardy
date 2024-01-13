import Button from "../Button";

export default function Category({ name, questions }) {
  return (
    <div className="coluna">
      <h1 className="categoria">{name}</h1>
      {questions.map((q) => (
        <Button
          id={q.id}
          key={q.id}
          amount={q.value}
          link={`/staff/question/${q.id}`}
          enabled={!q.answered}
        />
      ))}
    </div>
  );
}
