import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

import { registerInterviewSocket } from "./sockets/interviewSocket.js";

const DEFAULT_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"];
const extraCorsOrigins = process.env.CORS_ORIGINS?.split(",").map((origin) => origin.trim()) ?? [];

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: [...DEFAULT_CORS_ORIGINS, ...extraCorsOrigins],
  },
});

const PORT = 3000;

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

registerInterviewSocket(io);

httpServer.listen(PORT, () => {
  console.log(`ws-gateway escuchando en el puerto ${PORT}`);
});