import express from "express";
import { createServer } from "http";
import { Server } from "socket.io";

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer);

const PORT = 3000;

app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

io.on("connection", (socket) => {
  console.log("cliente conectado:", socket.id);
});

httpServer.listen(PORT, () => {
  console.log(`ws-gateway escuchando en el puerto ${PORT}`);
});