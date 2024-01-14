import GameAnsweringQuestion from "./GameAnsweringQuestion";
import GameSelectingQuestion from "./GameSelectingQuestion"
import GameWaiting from "./GameWaiting"

export default function GameState({state, role}) {
    console.log(state);
    switch(state.state) {
        case 1:
            return (<GameSelectingQuestion state={state}/>);
        case 2:
            return (<GameAnsweringQuestion state={state}/>)
        case 3:
            return (<GameOver state={state}/>)
        case 0:
        default:
            return (<GameWaiting state={state}/>);
    }
}