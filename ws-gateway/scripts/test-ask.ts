import { io } from "socket.io-client";

const socket = io("http://localhost:3000");

socket.on("connect", () => {
  console.log("Conectado al gateway, socket id:", socket.id);
  socket.emit("ask", "Qué es una API REST?");
});

socket.on("ask", (answer) => {
  console.log("Respuesta del LLM:", answer);
  socket.disconnect();
});