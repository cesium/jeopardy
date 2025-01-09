import { State, Question } from "../types";

export function processState(state: State): [string[], number[], Question[]] {
  const categories: string[] = [
    ...new Set(state.questions.map((q) => q.category)),
  ];

  const questions: Question[] = state.questions.sort((a, b) => {
    const res = a.value - b.value;
    if (res == 0) {
      return categories.indexOf(a.category) - categories.indexOf(b.category);
    } else {
      return res;
    }
  });

  const points: number[] = [...new Set(questions.map((q) => q.value))];

  return [categories, points, questions];
}
