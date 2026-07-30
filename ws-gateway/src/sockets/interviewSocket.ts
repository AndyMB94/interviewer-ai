import type { Server } from "socket.io";

import { askQuestion, synthesizeSpeech, transcribeAudio } from "../services/djangoClient.js";

const DJANGO_URL = "http://localhost:8000";

export function registerInterviewSocket(io: Server) {
  io.on("connection", (socket) => {
    console.log("cliente conectado:", socket.id);

    let interviewId: number | undefined;

    socket.on("echo", (message) => {
      console.log("mensaje recibido:", message);
      socket.emit("echo", message);
    });

    socket.on("ask", async (question: string) => {
      console.log("pregunta recibida:", question);
      const result = await askQuestion(question, interviewId);
      interviewId = result.interviewId;
      socket.emit("ask", result.answer);
    });

    socket.on("audio", async (buffer: ArrayBuffer) => {
      console.log("audio recibido:", buffer.byteLength, "bytes");

      try {
        const transcript = await transcribeAudio(buffer);
        console.log("transcripción:", transcript);
        socket.emit("transcript", transcript);

        const result = await askQuestion(transcript, interviewId);
        interviewId = result.interviewId;
        console.log("respuesta del LLM:", result.answer, "| interview_id:", interviewId);

        const audioUrl = await synthesizeSpeech(result.answer);
        console.log("audio de respuesta:", audioUrl);
        socket.emit("audio-response", `${DJANGO_URL}${audioUrl}`);
      } catch (error) {
        console.error("ERROR en el flujo de audio:", error);
      }
    });
  });
}