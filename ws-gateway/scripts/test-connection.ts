import { io } from "socket.io-client";

const socket = io("http://localhost:3000");

socket.on("connect", () => {
  console.log("Conectado al gateway, socket id:", socket.id);
  socket.emit("echo", "Hola gateway");
});

socket.on("echo", (message) => {
  console.log("Eco recibido:", message);
  socket.disconnect();
});