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

export async function getPlayers() {
  const response = await API.get("/players");

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

export async function setPlayers(players: string[]) {
  const response = await API.post("/players", {
    players: players,
  });

  return response.data;
}

export async function answer(correct: boolean) {
  const response = await API.post("/answer", {
    correct: correct,
  });

  return response.data;
}
