import { request } from "./api";

export const loginUser = async (username, password) => {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  if (data.access_token) {
    localStorage.setItem("token", data.access_token);
  }
  return data;
};

export const registerUser = async (username, password) => {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
};

export const fetchCurrentUser = async () => {
  return request("/auth/me", {
    method: "GET",
  });
};
