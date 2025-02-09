import GameAnsweringQuestion from "./GameAnsweringQuestion";
import GameSelectingQuestion from "./GameSelectingQuestion";
import GameWaiting from "./GameWaiting";
import GameOver from "./GameOver";
import { State } from "../../types";
import { useCallback, useEffect, useState } from "react";
import { processState } from "../../lib/utils";
import GameSplitOrSteal from "./GameSplitOrSteal";

interface GameStateProps {
  state: State;
  role: "viewer" | "staff" | "host";
}

export default function GameState({ state, role }: GameStateProps) {
  const [startOpenAnimation, setStartOpenAnimation] = useState<boolean>(false);
  const [startFadeOutAnimation, setStartFadeOutAnimation] =
    useState<boolean>(false);
  const [selectingQuestionInView, setSelectingQuestionInView] =
    useState<boolean>(false);
  const [animationPosition, setAnimationPosition] = useState<number>(0);
  const [selectingQuestion, setSelectingQuestion] = useState<boolean>(false);
  const [answeringQuestion, setAnsweringQuestion] = useState<boolean>(false);
  const [answeringQuestionInView, setAnsweringQuestionInView] =
    useState<boolean>(false);
  const [splitOrStealInView, setSplitOrStealInView] = useState<boolean>(false);
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [waiting, setWaiting] = useState<boolean>(false);
  const [splitOrSteal, setSplitOrSteal] = useState<boolean>(false);
  const [gameOverFadeIn, setGameOverFadeIn] = useState<boolean>(false);

  const getCellNr = useCallback(() => {
    const [categories, points] = processState(state);

    const cq = state.currentQuestion;
    const column = categories.indexOf(cq.category);
    const row = points.indexOf(cq.value);
    const columnsNr = categories.length;

    return row * columnsNr + column;
  }, [state]);

  useEffect(() => {
    console.log(state);
    switch (state.state) {
      case 1:
        setTimeout(() => {
          setStartFadeOutAnimation(true);
        }, 500);
        setTimeout(() => {
          setStartFadeOutAnimation(false);
          setSelectingQuestion(true);
          setAnsweringQuestion(false);
          setAnsweringQuestionInView(false);
          setGameOver(false);
          setGameOverFadeIn(false);
          setWaiting(false);
          setSplitOrSteal(false);
          setSplitOrStealInView(false);
        }, 1000);
        setTimeout(() => {
          setSelectingQuestionInView(true);
        }, 1100);
        break;
      case 2:
        setAnimationPosition(getCellNr());
        setTimeout(() => {
          setStartOpenAnimation(true);
        }, 1000);
        setTimeout(() => {
          setStartOpenAnimation(false);
          setAnsweringQuestion(true);
          setSelectingQuestion(false);
          setSelectingQuestionInView(false);
          setGameOver(false);
          setGameOverFadeIn(false);
          setWaiting(false);
          setSplitOrSteal(false);
          setSplitOrStealInView(false);
        }, 2000);
        setTimeout(() => {
          setAnsweringQuestionInView(true);
        }, 2100);
        break;
      case 3:
        break;
      case 4:
        break;
      case 5:
        setTimeout(() => {
          setStartFadeOutAnimation(true);
        }, 500);
        setTimeout(() => {
          setStartFadeOutAnimation(false);
          setSplitOrSteal(true);
          setSelectingQuestion(false);
          setAnsweringQuestion(false);
          setAnsweringQuestionInView(false);
          setGameOver(false);
          setGameOverFadeIn(false);
          setWaiting(false);
        }, 1000);
        setTimeout(() => {
          setSplitOrStealInView(true);
        }, 1100);
        break;
      case 6:
        setSplitOrStealInView(false);
        setTimeout(() => {
          setGameOver(true);
          setSplitOrSteal(false);
          setSelectingQuestion(false);
          setSelectingQuestionInView(false);
          setAnsweringQuestion(false);
          setAnsweringQuestionInView(false);
          setWaiting(false);
        }, 500);
        setTimeout(() => {
          setGameOverFadeIn(true);
        }, 1500);
        break;
      case 0:
      default:
        setWaiting(true);
        setSelectingQuestion(false);
        setSelectingQuestionInView(false);
        setAnsweringQuestion(false);
        setAnsweringQuestionInView(false);
        setGameOver(false);
        setGameOverFadeIn(false);
        setSplitOrSteal(false);
        setSplitOrStealInView(false);
        break;
    }
  }, [state, getCellNr]);

  return (
    <>
      {selectingQuestion && (
        <GameSelectingQuestion
          state={state}
          startOpenAnimation={startOpenAnimation}
          inView={selectingQuestionInView}
          animationPosition={animationPosition}
          role={role}
        />
      )}
      {answeringQuestion && (
        <GameAnsweringQuestion
          state={state}
          role={role}
          fadeOut={startFadeOutAnimation}
          inView={answeringQuestionInView}
        />
      )}
      {gameOver && (
        <GameOver state={state} role={role} inView={gameOverFadeIn} />
      )}
      {waiting && <GameWaiting state={state} role={role} />}
      {splitOrSteal && (
        <GameSplitOrSteal
          state={state}
          role={role}
          inView={splitOrStealInView}
        />
      )}
    </>
  );
}
