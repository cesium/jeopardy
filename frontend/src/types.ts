export type Player = {
  name: string;
  balance: number;
};

export type Question = {
  id: number;
  statement: string;
  answer: string;
  value: number;
  category: string;
  answered: boolean;
};

export type State = {
  players: Player[];
  questions: Question[];
  state: number;
  currentQuestion: Question;
  currentPlayer: Player;
  selectingPlayer: number;
  alreadyAnswered: number[];
  playCorrectSound: boolean;
  playWrongSound: boolean;
};
