const BASE_URL = "http://127.0.0.1:8000/api";

export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return token ? { "Authorization": `Bearer ${token}` } : {};
};

export const request = async (endpoint, options = {}) => {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeaders(),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    if (response.status === 401) {
      // Clear token and redirect to login if session expired
      localStorage.removeItem("token");
      if (!window.location.pathname.includes("/login") && !window.location.pathname.includes("/register")) {
        window.location.href = "/login";
      }
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "An error occurred" }));
      throw new Error(errorData.detail || `HTTP error ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error("API Request Failure:", error);
    throw error;
  }
};

export default BASE_URL;
