import axios from "axios";

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  responseType: "json",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function getQuestion(id: string) {
  const response = await API.get(`/question/${id}`);

  return response.data;
}

export async function getQuestions() {
  const response = await API.get("/questions");

  return response.data;
}

export async function startQuestion() {
  const response = await API.post("/buzz_start");

  return response.data;
}

export async function skipQuestion() {
  const response = await API.post("/skip");

  return response.data;
}

export async function getTeams() {
  const response = await API.get("/teams");

  return response.data;
}

export async function getWinners() {
  const response = await API.get("/winners");

  return response.data;
}

export async function setQuestion(id: number) {
  const response = await API.post("/question", {
    id: id,
  });

  return response.data;
}

export async function setTeams(teams: string[][]) {
  const response = await API.post("/teams", {
    teams: teams,
  });

  return response.data;
}

export async function answer(correct: boolean) {
  const response = await API.post("/answer", {
    correct: correct,
  });

  return response.data;
}

export async function stopTimer() {
  const response = await API.post("/stop_timer");
  return response.data;
}

export async function showSOSResults() {
  const response = await API.post("/show_sos");
  return response.data;
}

export async function showTiebreakQuestion() {
  const response = await API.post("/show_tiebreaker_question");
  return response.data;
}

export async function playWalkInSong() {
  const response = await API.post("/play_walkin");
  return response.data;
}

export async function stopWalkInSong() {
  const response = await API.post("/stop_walkin");
  return response.data;
}

export async function endGame() {
  const response = await API.post("/end");
  return response.data;
}

export async function fixSelectingTeam(team: number) {
  const response = await API.post("/fix/selecting/", {
    team_id: team,
  });

  return response.data;
}

export async function fixState(state: number) {
  const response = await API.post("/fix/state/", {
    state: state,
  });

  return response.data;
}

export async function fixPoints(team: number, points: number) {
  const response = await API.post("/fix/points/", {
    team_id: team,
    points: points,
  });

  return response.data;
}

export async function fixListSaves() {
  const response = await API.get("/fix/saves/");
  return response.data;
}

export async function fixSaves(save: string) {
  const response = await API.post("/fix/saves/", {
    name: save,
  });
  return response.data;
}
