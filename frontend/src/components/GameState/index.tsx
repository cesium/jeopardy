import GameAnsweringQuestion from "./GameAnsweringQuestion";
import GameSelectingQuestion from "./GameSelectingQuestion";
import GameWaiting from "./GameWaiting";
import GameOver from "./GameOver";

import { State } from "../../types";

import { useEffect, useState } from "react";

interface GameStateProps {
  state: State;
  role: string;
}

export default function GameState({ state, role }: GameStateProps) {
  const [startAnimation, setStartAnimation] = useState<boolean>(false);
  const [animationPosition, setAnimationPosition] = useState<number>(1);

  const [selectingQuestion, setSelectingQuestion] = useState<boolean>(false);
  const [answeringQuestion, setAnsweringQuestion] = useState<boolean>(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [waiting, setWaiting] = useState<boolean>(false);

  function getCellNr(): number {
    const cq = state.currentQuestion;
    const value = cq.value;
    const categories: string[] = [
      ...new Set(state.questions.map((q) => q.category)),
    ];
    const column = categories.indexOf(cq.category);
    let row = 0;

    switch (value) {
      case 100:
        row = 0;
        break;
      case 200:
        row = 1;
        break;
      case 300:
        row = 2;
        break;
      case 400:
        row = 3;
        break;
      case 500:
        row = 4;
        break;
      default:
        break;
    }

    console.log("cellNr", row * 5 + column + 1);

    return row * 5 + column + 1;
  }

  useEffect(() => {
    switch (state.state) {
      case 1:
        setSelectingQuestion(true);
        setAnsweringQuestion(false);
        setGameOver(false);
        setWaiting(false);
        break;
      case 2:
      case 3:
      case 4:
        setAnimationPosition(getCellNr());
        setTimeout(() => {
          setStartAnimation(true);
        }, 1100);
        setTimeout(() => {
          setStartAnimation(false);
          setSelectingQuestion(false);
        }, 2200);
        setAnsweringQuestion(true);
        setGameOver(false);
        setWaiting(false);
        break;
      case 5:
        setSelectingQuestion(false);
        setAnsweringQuestion(false);
        setGameOver(true);
        setWaiting(false);
        break;
      case 0:
      default:
        setSelectingQuestion(false);
        setAnsweringQuestion(false);
        setGameOver(false);
        setWaiting(true);
        break;
    }
  }, [state]);

  return (
    <>
      {selectingQuestion && (
        <GameSelectingQuestion
          state={state}
          startAnimation={startAnimation}
          animationPosition={animationPosition}
          role={role}
        />
      )}
      {answeringQuestion && <GameAnsweringQuestion state={state} role={role} />}
      {gameOver && <GameOver state={state} role={role} />}
      {waiting && <GameWaiting state={state} role={role} />}
    </>
  );
}
