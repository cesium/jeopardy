import { useState, useEffect, useCallback } from "react";
import { State } from "../../../types";
import { processState } from "../../../lib/utils";
import * as api from "../../../lib/api";
import useSound from "use-sound";

interface GameSelectingQuestionProps {
  state: State;
  role: "viewer" | "staff" | "host";
  startOpenAnimation: boolean;
  inView: boolean;
  animationPosition: number;
}

const Animation = ({
  start,
  left,
  top,
  cellWidth,
  cellHeight,
  totalWidth,
  totalHeight,
  disabled,
}) => {
  const startStyle: React.CSSProperties = {
    left: left,
    top: top,
    width: cellWidth,
    height: cellHeight,
  };

  const afterStyle: React.CSSProperties = {
    left: 0,
    top: 0,
    width: totalWidth,
    height: totalHeight,
  };

  if (!(left === 0 || top === 0))
    return (
      <>
        <div
          className={`${disabled ? "hidden" : ""} ${start ? "opacity-100" : ""} rounded-md transition-all duration-1000 z-50 bg-background opacity-0 absolute`}
          style={start ? afterStyle : startStyle}
        />
        <div
          className={`${disabled ? "hidden" : ""} ${start ? "border-none" : ""} border border-primary animate-pulse absolute rounded-md transition-all duration-1000 z-50`}
          style={startStyle}
        />
      </>
    );
};

export default function GameSelectingQuestion({
  state,
  role,
  startOpenAnimation,
  inView,
  animationPosition,
}: GameSelectingQuestionProps) {
  const [categories, points, questions] = processState(state);
  const [left, setLeft] = useState<number>(0);
  const [top, setTop] = useState<number>(0);

  const columnsNr: number = categories.length;
  const totalWidth: number = screen.width;
  const totalHeight: number = screen.height;
  const cellWidth: number =
    (totalWidth - 24 * 2 - 8 * (columnsNr - 1)) / columnsNr;
  const cellHeight: number = 140;

  const getPosition = useCallback(
    (cellNr: number) => {
      const row = Math.floor(cellNr / columnsNr);
      const column = cellNr % columnsNr;
      const left = 24 + column * cellWidth + column * 8;
      const top = 24 + 64 + 12 + row * cellHeight + row * 8;
      setLeft(left);
      setTop(top);
    },
    [cellWidth, columnsNr],
  );

  useEffect(() => {
    getPosition(animationPosition);
  }, [animationPosition, getPosition]);

  useEffect(() => {
    if (role === "viewer" && state.actions.playQuestionSelectionSound) {
      playOpenQuestion();
    }
  }, [state.actions]);

  const [playOpenQuestion] = useSound("/sounds/swoosh-zoom-in.mp3", {
    volume: 1,
    interrupt: true,
  });

  const setQuestion = (id) => {
    api.setQuestion(id);
  };

  return (
    <div
      className={`flex flex-col p-6 uppercase text-center select-none transition-all duration-500 ${inView ? "opacity-100" : "opacity-0"} h-screen`}
    >
      <Animation
        start={startOpenAnimation}
        left={left}
        top={top}
        cellWidth={cellWidth}
        cellHeight={cellHeight}
        totalWidth={totalWidth}
        totalHeight={totalHeight}
        disabled={role == "staff"}
      />

      <div
        className={`grid gap-2 grid-cols-${columnsNr} text-5xl font-extrabold`}
      >
        {categories.map((c, idx) => (
          <div
            className="bg-accent mb-1 py-3 text-4xl rounded-md"
            key={`cat-${idx}`}
          >
            <p className="drop-shadow-md">{c}</p>
          </div>
        ))}
        {questions.map((q, idx) => (
          <button
            className={`bg-gradient-to-br from-accent/90 to-accent/40 backdrop-blur-md text-primary p-10 rounded-md flex space-x-2 place-content-center h-[140px] items-center ${q.answered && "opacity-40"} ${!q.answered && role === "staff" && "hover:border"} border-primary`}
            key={`question-${idx}`}
            disabled={q.answered || role !== "staff"}
            onClick={() => setQuestion(q.id)}
          >
            {!q.answered && (
              <p className="text-8xl drop-shadow-lg">
                {!q.answered && q.value}
              </p>
            )}
          </button>
        ))}
      </div>
      <div className="flex items-center justify-center h-full">
        {state.teams.map((p, idx) => (
          <div
            key={`team-${idx}`}
            className={`mx-12 uppercase ${state.state === 1 && state.selectingTeam === idx && "text-primary"}`}
          >
            <div className="flex flex-col space-y-0.5">
              {p.names.map((name, index) => (
                <p
                  key={index}
                  className={`font-bold text-4xl ${state.state === 1 && state.selectingTeam === idx && "animate-bounce"}`}
                >
                  {name}
                </p>
              ))}
            </div>
            <p className="font-medium text-3xl mt-2">{p.balance}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
