import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

import { registerInterviewSocket } from "./sockets/interviewSocket.js";

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

const PORT = 3000;

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

registerInterviewSocket(io);

httpServer.listen(PORT, () => {
  console.log(`ws-gateway escuchando en el puerto ${PORT}`);
});