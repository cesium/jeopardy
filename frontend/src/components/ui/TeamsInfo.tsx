import { State } from "../../types";

export default function TeamsInfo({ state }: { state: State }) {
  return (
    <div className="flex items-center justify-center h-full gap-24">
      {state.teams.map((p, idx) => (
        <div key={`team-${idx}`} className="uppercase">
          <p className="font-bold text-4xl">{p.names}</p>
          <p className="font-medium text-3xl mt-2">{p.balance}</p>
        </div>
      ))}
    </div>
  );
}
