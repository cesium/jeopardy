import { useState, useEffect } from "react";

import { State, Question } from "../../../types";

function processState(state: State): [string[], Question[]] {
  const categories: string[] = [...new Set(state.questions.map((q) => q.category))];

  const questions: Question[] = state.questions.sort((a, b) => {
    const res = a.value - b.value;
    if (res == 0) {
      return categories.indexOf(a.category) - categories.indexOf(b.category);
    } else {
      return res;
    }
  });

  return [categories, questions];
}

interface GameSelectingQuestionProps {
  state: State;
  startAnimation: boolean;
  animationPosition: number;
}

const Animation = ({start, left, top, cellWidth, cellHeight, totalWidth, totalHeight}) => {
  const startStyle: React.CSSProperties = {
    position: "absolute",
    zIndex: 100,
    left: left,
    top: top,
    width: cellWidth,
    height: cellHeight,
    transition: "all 1s ease-in-out"
  };

  const afterStyle: React.CSSProperties = {
    position: "absolute",
    zIndex: 100,
    left: 0,
    top: 0,
    width: totalWidth,
    height: totalHeight,
    transition: "all 1s ease-in-out"
  };

  return <div className={`${start ? "bg-primary border-none" : "border-accent border-4 bg-transparent"} rounded`} style={start ? afterStyle : startStyle}/>;
};

export default function GameSelectingQuestion({ state, startAnimation, animationPosition }: GameSelectingQuestionProps) {
  const [categories, questionsPerAmount] = processState(state);
  const [left, setLeft] = useState<number>(0);
  const [top, setTop] = useState<number>(0);

  const totalWidth: number = screen.width;
  const totalHeight: number = screen.height;
  const cellWidth: number = (totalWidth - 24*2 - 8*4) / 5;
  const cellHeight: number = 140;

  function getPosition(cellNr: number) {
    const row = Math.floor(cellNr / 5);
    const column = cellNr % 5 - 1;
    console.log("column", column);
    const left = 24 + column * cellWidth + column * 8;
    const top = 24 + 64 + 12 + row * cellHeight + row * 8;
    setLeft(left);
    setTop(top);
  };

  useEffect(() => {
    getPosition(animationPosition);
  }, [animationPosition]);

  return (
    <div className="p-6 uppercase text-center select-none">
      <Animation start={startAnimation} left={left} top={top} cellWidth={cellWidth} cellHeight={cellHeight} totalWidth={totalWidth} totalHeight={totalHeight} />

      <div className={`grid gap-2 grid-cols-5 text-5xl font-extrabold`}>
        {categories.map((c, idx) => (
          <div className="bg-test mb-1 py-3 text-4xl rounded" key={`cat-${idx}`}>
            <p className="drop-shadow-md">
              {c}
            </p>
          </div>
        ))}

        {questionsPerAmount.map((q, idx) => (
          <div
            className={`bg-gradient-to-br from-test to-test/50 text-accent p-10 rounded flex space-x-2 place-content-center h-[140px] ${q.answered && "opacity-40"}`}
            key={`question-${idx}`}
          >
            {!q.answered && (
              <>
                {/* <img src="/images/sei-logo.svg" className="w-[25px] drop-shadow-lg" /> */}
                <p className="text-7xl drop-shadow-lg">
                  {!q.answered && q.value}
                </p>
              </>
            )}
          </div>
        ))}
      </div>
      <div className="flex items-center justify-center mt-12">
        {state.players.map((p, idx) => (
          <div key={`player-${idx}`} className="mx-12 uppercase">
            <p className="font-extrabold text-4xl">{p.name}</p>
            <p className="font-bold text-3xl mt-2">{p.balance}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
