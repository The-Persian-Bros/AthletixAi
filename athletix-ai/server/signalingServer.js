// signalingServer.js
import express from "express";
import cors from "cors";
import http from "http";
import { WebSocketServer } from "ws";

const app = express();
app.use(cors());
app.get("/", (req, res) => res.send("WebRTC Signaling Server is running"));

const PORT = process.env.PORT || 3001;
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

// We support one publisher and one viewer for this minimal example.
let publisher = null;
let viewer = null;

wss.on("connection", (ws, req) => {
  // Determine role based on URL:
  // - Publisher should connect to ws://localhost:3001/ingest
  // - Viewer should connect to ws://localhost:3001/stream
  const url = req.url || "";
  console.log("New WebSocket connection with URL:", url);

  if (url.startsWith("/ingest")) {
    publisher = ws;
    console.log("Publisher registered.");
  } else if (url.startsWith("/stream")) {
    viewer = ws;
    console.log("Viewer registered.");
  } else {
    console.log("Unknown connection type; closing connection.");
    ws.close();
    return;
  }

  ws.on("message", (message) => {
    // If the message is not a string, try to convert it.
    if (typeof message !== "string") {
      if (Buffer.isBuffer(message)) {
        message = message.toString("utf-8");
      } else if (message instanceof ArrayBuffer) {
        message = Buffer.from(message).toString("utf-8");
      } else {
        console.log("Ignoring non-JSON message of unknown type.");
        return;
      }
    }
    try {
      const data = JSON.parse(message);
      // Relay signaling messages between publisher and viewer.
      if (ws === publisher && viewer && viewer.readyState === viewer.OPEN) {
        console.log("Relaying message from publisher to viewer:", data.type);
        viewer.send(message);
      } else if (ws === viewer && publisher && publisher.readyState === publisher.OPEN) {
        console.log("Relaying message from viewer to publisher:", data.type);
        publisher.send(message);
      } else {
        console.log("No peer available to relay message of type", data.type);
      }
    } catch (err) {
      console.error("Error parsing JSON message, ignoring:", err);
    }
  });

  ws.on("close", () => {
    if (ws === publisher) {
      console.log("Publisher disconnected.");
      publisher = null;
    }
    if (ws === viewer) {
      console.log("Viewer disconnected.");
      viewer = null;
    }
  });
});

server.listen(PORT, () => {
  console.log(`Signaling server is running on port ${PORT}`);
});
