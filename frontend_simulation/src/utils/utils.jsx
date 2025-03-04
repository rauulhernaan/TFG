import axios from "axios";

axios.defaults.withCredentials = true;

const getCSRFToken = async () => {
  try {
    const response = await axios.get("http://localhost:8000/get-csrf-token/");

    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];

    if (!csrfToken) {
      console.error("CSRF token not found in cookies");
      return null;
    }

    axios.defaults.headers.common["X-CSRFToken"] = csrfToken;
    return csrfToken;
  } catch (error) {
    console.error("Error fetching CSRF token:", error);
    return null;
  }
};


export { getCSRFToken };