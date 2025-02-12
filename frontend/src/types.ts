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
  tta: number; // seconds
};

export type State = {
  teams: Team[];
  questions: Question[];
  state: number;
  currentQuestion: Question;
  currentTeam: number;
  selectingTeam: number;
  alreadyAnswered: number[];
  SOSAnswers: boolean[];
  actions: {
    playCorrectSound: boolean;
    playWrongSound: boolean;
    playStartAccepting: boolean;
    playBuzzerSound: boolean;
    playEndSound: boolean;
    stopTimer: boolean;
    showSOS: boolean;
    showTiebreakQuestion: boolean;
    playThemeSong: boolean;
    playQuestionSelectionSound: boolean;
    playSelectingQuestionSound: boolean;
  };
};
