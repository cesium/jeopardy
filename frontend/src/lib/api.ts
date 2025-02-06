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