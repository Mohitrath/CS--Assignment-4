const express = require("express");
const { exec, spawn } = require("child_process");
const net = require("net");

const app = express();

app.use(express.json());
app.use(express.static("public"));

// Vulnerable endpoint
app.post("/ping-vulnerable", (req, res) => {
    const ip = req.body.ip;

    exec(`ping -c 4 ${ip}`, (error, stdout, stderr) => {
        res.json({
            output: stdout,
            error: stderr
        });
    });
});

// Secure endpoint
app.post("/ping-secure", (req, res) => {
    const ip = req.body.ip;

    if (typeof ip !== "string" || net.isIP(ip) === 0) {
        return res.status(400).json({
            error: "Invalid IP Address"
        });
    }

    const ping = spawn("ping", ["-c", "4", ip]);

    let output = "";

    ping.stdout.on("data", (data) => {
        output += data.toString();
    });

    ping.on("close", (code) => {
        res.json({
            output: output,
            exitCode: code
        });
    });

    ping.on("error", () => {
        res.status(500).json({
            error: "Ping execution failed"
        });
    });
});

app.listen(3000, () => {
    console.log("Server running at http://localhost:3000");
});