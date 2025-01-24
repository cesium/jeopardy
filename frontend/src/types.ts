export type Team = {
  names: string[];
  balance: number;
};

export type Question = {
  id: number;
  statement: string;
  answer: string;
  image: string;
  value: number;
  category: string;
  answered: boolean;
};

export type State = {
  teams: Team[];
  questions: Question[];
  state: number;
  currentQuestion: Question;
  currentTeam: Team;
  selectingTeam: number;
  alreadyAnswered: number[];
  playCorrectSound: boolean;
  playWrongSound: boolean;
  playStartAccepting: boolean;
  playBuzzerSound: boolean;
};
