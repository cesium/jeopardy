import Button from "../Button";

import { Question } from "../../types";

interface CategoryProps {
  name: string;
  questions: Question[];
}

export default function Category({ name, questions }: CategoryProps) {
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
