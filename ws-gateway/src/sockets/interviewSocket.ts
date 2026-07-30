import type { Server } from "socket.io";

import { askQuestion, transcribeAudio } from "../services/djangoClient.js";

export function registerInterviewSocket(io: Server) {
  io.on("connection", (socket) => {
    console.log("cliente conectado:", socket.id);

    socket.on("echo", (message) => {
      console.log("mensaje recibido:", message);
      socket.emit("echo", message);
    });

    socket.on("ask", async (question: string) => {
      console.log("pregunta recibida:", question);
      const answer = await askQuestion(question);
      socket.emit("ask", answer);
    });

    socket.on("audio", async (buffer: ArrayBuffer) => {
      console.log("audio recibido:", buffer.byteLength, "bytes");
      const transcript = await transcribeAudio(buffer);
      console.log("transcripción:", transcript);
      socket.emit("transcript", transcript);
    });
  });
}