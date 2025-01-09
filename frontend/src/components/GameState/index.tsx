import GameAnsweringQuestion from "./GameAnsweringQuestion";
import GameSelectingQuestion from "./GameSelectingQuestion";
import GameWaiting from "./GameWaiting";
import GameOver from "./GameOver";
import { State } from "../../types";
import { useCallback, useEffect, useState } from "react";
import useSound from "use-sound";
import { processState } from "../../lib/utils";

interface GameStateProps {
  state: State;
  role: string;
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
  const [gameOver, setGameOver] = useState<boolean>(false);
  const [waiting, setWaiting] = useState<boolean>(false);

  // const [playThemeSong, { stop }] = useSound("/sounds/themesong.mp3", {
  //   loop: true,
  //   volume: 0.2,
  // });

  // useEffect(() => {
  //   if (role === "viewer") {
  //     playThemeSong();
  //   }
  // }, [playThemeSong, role]);

  const getCellNr = useCallback(() => {
    const [categories, points] = processState(state);

    const cq = state.currentQuestion;
    const column = categories.indexOf(cq.category);
    const row = points.indexOf(cq.value);
    const columnsNr = categories.length;

    return row * columnsNr + column;
  }, [state]);

  useEffect(() => {
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
          setWaiting(false);
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
          setWaiting(false);
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
        setSelectingQuestion(false);
        setSelectingQuestionInView(false);
        setAnsweringQuestion(false);
        setAnsweringQuestionInView(false);
        setGameOver(true);
        setWaiting(false);
        break;
      case 0:
      default:
        setSelectingQuestion(false);
        setSelectingQuestionInView(false);
        setAnsweringQuestion(false);
        setAnsweringQuestionInView(false);
        setGameOver(false);
        setWaiting(true);
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
      {gameOver && <GameOver state={state} role={role} />}
      {waiting && <GameWaiting state={state} role={role} />}
    </>
  );
}
