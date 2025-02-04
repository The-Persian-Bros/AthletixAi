"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Button } from "../../components/ui/button";
import { Camera, Send } from "lucide-react";
import type React from "react";

export default function Dashboard() {
  const [isStreaming, setIsStreaming] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Chat state (if needed)
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState<{ role: string; content: string }[]>([
    { role: "assistant", content: "Hello! I'm your AI coach. How can I help you today? 🏋️‍♂️" },
  ]);

  // Ensure client-only rendering
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);

  // Set up signaling WebSocket (publisher endpoint)
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:3001/ingest");
    ws.onopen = () => {
      console.log("WebSocket connected (publisher).");
    };
    ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "answer") {
          if (pcRef.current) {
            await pcRef.current.setRemoteDescription(data);
            console.log("Remote description set from answer.");
          }
        } else if (data.type === "candidate") {
          if (pcRef.current) {
            try {
              await pcRef.current.addIceCandidate(data.candidate);
              console.log("Added ICE candidate (publisher).");
            } catch (err) {
              console.error("Error adding ICE candidate:", err);
            }
          }
        }
      } catch (err) {
        console.error("Error handling message:", err);
      }
    };
    ws.onerror = (err) => console.error("WebSocket error (publisher):", err);
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const startStreaming = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
      });
      pcRef.current = pc;

      pc.onicecandidate = (event) => {
        if (event.candidate && wsRef.current) {
          wsRef.current.send(JSON.stringify({ type: "candidate", candidate: event.candidate }));
        }
      };

      stream.getTracks().forEach((track) => {
        pc.addTrack(track, stream);
      });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      console.log("Sending offer:", offer);
      if (wsRef.current) {
        wsRef.current.send(JSON.stringify(offer));
      }
      setIsStreaming(true);
    } catch (err) {
      console.error("Error starting streaming:", err);
    }
  };

  const stopStreaming = () => {
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (videoRef.current && videoRef.current.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      setChatMessages([...chatMessages, { role: "user", content: message }]);
      setTimeout(() => {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "I've received your message. As an AI coach, I'm here to help you improve your performance. Could you please provide more details about your training goals? 🎯",
          },
        ]);
      }, 1000);
      setMessage("");
    }
  };

  return (
    <div className="relative min-h-screen">
      <div className="absolute inset-0 bg-gradient-animate opacity-10"></div>
      <div className="relative z-10 container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8 text-center text-gradient">
          Your AI Training Dashboard
        </h1>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-background/80 backdrop-blur-lg rounded-lg p-6 shadow-lg"
          >
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Camera className="mr-2" />
              Camera Feed
            </h2>
            <div className="aspect-w-16 aspect-h-9 bg-black rounded-lg overflow-hidden mb-4">
              {mounted && (
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="object-cover w-full h-full"
                />
              )}
            </div>
            {!isStreaming ? (
              <Button onClick={startStreaming} className="w-full hover-lift">
                Turn On Camera &amp; Stream
              </Button>
            ) : (
              <Button onClick={stopStreaming} className="w-full hover-lift">
                Turn Off Camera
              </Button>
            )}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-background/80 backdrop-blur-lg rounded-lg p-6 shadow-lg"
          >
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Send className="mr-2" />
              AI Coach
            </h2>
            <div className="h-64 bg-background/50 rounded-lg p-4 mb-4 overflow-y-auto">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`mb-2 ${msg.role === "user" ? "text-right" : "text-left"}`}
                >
                  <span
                    className={`inline-block p-2 rounded-lg ${
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-secondary text-secondary-foreground"
                    }`}
                  >
                    {msg.content}
                  </span>
                </div>
              ))}
            </div>
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask your AI coach a question..."
                className="flex-grow p-2 border rounded"
              />
              <Button type="submit" className="hover-lift">
                Send
              </Button>
            </form>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
