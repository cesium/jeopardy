import { State } from "../../../types";

interface GameWaitingProps {
  state: State;
}

export default function GameWaiting({ state }: GameWaitingProps) {
  return (
    <div className="flex items-center h-screen justify-center text-white">
      <div className="block text-center">
        <h1 className="uppercase text-accent text-8xl font-extrabold mb-12">
          SEI OU NÃO SEI
        </h1>
      </div>
    </div>
  );
}
