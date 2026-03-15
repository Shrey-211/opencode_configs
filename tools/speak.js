import { tool } from "@opencode-ai/plugin";
import { z } from "zod";
import { spawn } from "child_process";
import path from "path";
import os from "os";

const speakTool = tool({
  description: "Convert text to speech using Microsoft Edge TTS",
  args: {
    text: z.string().describe("The text to convert to speech"),
    voice: z
      .string()
      .default("en-US-AriaNeural")
      .describe("The voice to use for speech synthesis"),
    rate: z
      .string()
      .default("+0%")
      .describe("The speech rate adjustment"),
    volume: z
      .string()
      .default("+0%")
      .describe("The speech volume adjustment"),
  },
  async execute(args) {
    const { text, voice, rate, volume } = args;

    const homeDir = os.homedir();
    const pythonScriptPath = path.join(homeDir, ".config", "opencode", "tools", "speak.py");

    const inputJson = JSON.stringify({
      text,
      voice,
      rate,
      volume,
    });

    const result = await new Promise((resolve, reject) => {
      const pythonProcess = spawn("python", [pythonScriptPath], {
        stdio: ["pipe", "pipe", "pipe"],
      });

      let stdout = "";
      let stderr = "";

      pythonProcess.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      pythonProcess.on("close", (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout.trim());
            resolve(result);
          } catch {
            resolve({
              success: false,
              message: `Failed to parse output: ${stdout}`,
            });
          }
        } else {
          resolve({
            success: false,
            message: stderr || `Script exited with code ${code}`,
          });
        }
      });

      pythonProcess.on("error", (error) => {
        resolve({
          success: false,
          message: `Failed to execute: ${error.message}`,
        });
      });

      pythonProcess.stdin.write(inputJson);
      pythonProcess.stdin.end();
    });

    if (!result.success) {
      throw new Error(result.message);
    }

    return result.message;
  },
});

export default speakTool;
