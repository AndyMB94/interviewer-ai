import type { Server } from "socket.io";

import { askQuestion, finishInterview, synthesizeSpeech, transcribeAudio } from "../services/djangoClient.js";

// URL que usa el NAVEGADOR para descargar el audio de TTS -- distinta de DJANGO_URL en
// djangoClient.ts (esa es para las llamadas del gateway a Django, entre contenedores).
const PUBLIC_DJANGO_URL = process.env.PUBLIC_DJANGO_URL || "http://localhost:8000";

export function registerInterviewSocket(io: Server) {
  io.on("connection", (socket) => {
    console.log("cliente conectado:", socket.id);

    // JWT de acceso, mandado por el cliente en el handshake (io(URL, { auth: { token } })).
    // Fase 11.1: sin token, ni `ask` ni `audio` se procesan -- antes seguían funcionando
    // anónimo (remanente de la demo pública de antes del pivote), lo que dejaba abierto un
    // canal para gastar cuota real de Deepgram/DeepSeek/ElevenLabs sin pasar por el sitio en
    // absoluto (conectándose directo al WebSocket público, sin loguearse nunca).
    const token = socket.handshake.auth?.token as string | undefined;

    // Fase 10.5/10.6: si el cliente ya sabe que está retomando una entrevista en curso (detectada
    // vía GET /api/interviews/en-curso/), manda su id acá para reengancharse en vez de que el
    // backend intente crear una entrevista nueva y choque con la que ya existe (409).
    let interviewId: number | undefined = socket.handshake.auth?.interviewId as number | undefined;

    socket.on("echo", (message) => {
      console.log("mensaje recibido:", message);
      socket.emit("echo", message);
    });

    // postulacionId solo viaja en el primer mensaje (todavía sin interviewId) -- es la postulación
    // elegida en la sala de espera (Frontend 9.7.5). Backend 9.7.3 la usa para crear la Interview.
    socket.on("ask", async (question: string, postulacionId?: number) => {
      if (!token) {
        socket.emit("error", "auth-required");
        return;
      }
      console.log("pregunta recibida:", question);
      const result = await askQuestion(question, interviewId, token, postulacionId);
      interviewId = result.interviewId;
      socket.emit("ask", { answer: result.answer, createdAt: result.createdAt, timedOut: result.timedOut });
    });

    socket.on("audio", async (buffer: ArrayBuffer, postulacionId?: number) => {
      if (!token) {
        socket.emit("error", "auth-required");
        return;
      }
      console.log("audio recibido:", buffer.byteLength, "bytes");

      try {
        const transcript = await transcribeAudio(buffer);
        console.log("transcripción:", transcript);
        socket.emit("transcript", transcript);

        const result = await askQuestion(transcript, interviewId, token, postulacionId);
        interviewId = result.interviewId;
        console.log("respuesta del LLM:", result.answer, "| interview_id:", interviewId);
        socket.emit("ask", { answer: result.answer, createdAt: result.createdAt, timedOut: result.timedOut });

        // Fase 10.9: no vale la pena sintetizar voz para el aviso de "se acabó el tiempo".
        if (result.timedOut) return;

        const audioUrl = await synthesizeSpeech(result.answer);
        console.log("audio de respuesta:", audioUrl);
        socket.emit("audio-response", `${PUBLIC_DJANGO_URL}${audioUrl}`);
      } catch (error) {
        console.error("ERROR en el flujo de audio:", error);
      }
    });

    socket.on("finish", async () => {
      if (interviewId) {
        console.log("finalizando entrevista:", interviewId);
        await finishInterview(interviewId);
      }
    });
  });
}