import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL;

export const encryptMessage = async (message, key) => {
  try {
    const response = await axios.post(`${API_URL}/encryptAES/`, {
      message: message,
      key: key,
    });
    return response.data;
  } catch (error) {
    console.error("Error al encriptar el mensaje:", error);
    throw error;
  }
};

export const decryptMessage = async (encryptedMessage, key, iv) => {
  try {
    const response = await axios.post(`${API_URL}/decryptAES/`, {
      encrypted_message: encryptedMessage.ciphertext,
      key: key,
      iv: iv,
    });
    return response.data.message;
  } catch (error) {
    console.error("Error al desencriptar el mensaje:", error);
    throw error;
  }
};
