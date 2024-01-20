import GameAnsweringQuestion from "./GameAnsweringQuestion";
import GameSelectingQuestion from "./GameSelectingQuestion";
import GameWaiting from "./GameWaiting";
import GameOver from "./GameOver";

export default function GameState({ state, role }) {
  switch (state.state) {
    case 1:
      return <GameSelectingQuestion state={state} />;
    case 2:
    case 3:
      return <GameAnsweringQuestion state={state} />;
    case 4:
      return <GameOver state={state} />;
    case 0:
    default:
      return <GameWaiting state={state} />;
  }
}
