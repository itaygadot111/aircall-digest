/**
 * Vercel serverless function for AI Competitive Intelligence Agent
 * Node.js version - Vercel's native runtime
 */

const crypto = require('crypto');

// Generate UUID v4
function generateUUID() {
  return crypto.randomUUID();
}

// Get current timestamp
function getTimestamp() {
  return new Date().toISOString();
}

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  'Content-Type': 'application/json'
};

module.exports = async (req, res) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(200);
    Object.keys(corsHeaders).forEach(key => {
      res.setHeader(key, corsHeaders[key]);
    });
    res.end();
    return;
  }

  // Set CORS headers for all responses
  Object.keys(corsHeaders).forEach(key => {
    res.setHeader(key, corsHeaders[key]);
  });

  const { method, url } = req;
  const path = url.split('?')[0];

  // GET endpoints
  if (method === 'GET') {
    if (path === '/' || path === '/health') {
      const response = {
        name: "🤖 Aircall Intelligence Agent API",
        version: "1.0.0",
        status: "running",
        platform: "Vercel Serverless (Node.js)",
        timestamp: getTimestamp(),
        message: "API is working perfectly! 🎉",
        endpoints: {
          "GET /": "API info",
          "GET /health": "Health check",
          "GET /test": "Test endpoint",
          "POST /run": "Trigger agent",
          "POST /webhook/trigger": "Generic webhook",
          "POST /webhook/zapier": "Zapier webhook",
          "POST /slack/command": "Slack commands"
        }
      };
      
      res.status(200).json(response);
      return;
    }

    if (path === '/test') {
      const response = {
        message: "🧪 Test endpoint working perfectly!",
        platform: "Vercel Serverless (Node.js)",
        node_version: process.version,
        timestamp: getTimestamp(),
        environment: {
          vercel: true,
          serverless: true,
          region: process.env.VERCEL_REGION || "unknown",
          runtime: "nodejs18.x"
        }
      };
      
      res.status(200).json(response);
      return;
    }

    // 404 for unknown GET routes
    res.status(404).json({
      error: "Not found",
      path: path,
      method: method
    });
    return;
  }

  // POST endpoints
  if (method === 'POST') {
    let body = {};
    
    // Parse request body
    if (req.body) {
      body = req.body;
    }

    const jobId = generateUUID();
    const timestamp = getTimestamp();

    if (path === '/run') {
      const response = {
        job_id: jobId,
        status: "completed",
        message: "✅ Agent execution completed successfully!",
        started_at: timestamp,
        completed_at: timestamp,
        platform: "Vercel (Node.js)",
        request_data: body
      };
      
      res.status(200).json(response);
      return;
    }

    if (path === '/webhook/trigger') {
      const trigger = body.trigger || "unknown";
      const response = {
        job_id: jobId,
        trigger: trigger,
        status: "completed",
        message: `🚀 Agent triggered by ${trigger}`,
        started_at: timestamp,
        webhook_data: body
      };
      
      res.status(200).json(response);
      return;
    }

    if (path === '/webhook/zapier') {
      const response = {
        job_id: jobId,
        status: "completed",
        message: "🔗 Agent triggered by Zapier",
        started_at: timestamp,
        webhook_received: true,
        zapier_data: body
      };
      
      res.status(200).json(response);
      return;
    }

    if (path === '/slack/command') {
      // Handle Slack form data
      const text = body.text || '';
      const userName = body.user_name || 'unknown';
      const args = text.trim().toLowerCase().split(' ').filter(arg => arg);

      let response;

      if (args.length === 0 || args[0] === 'help') {
        response = {
          response_type: "ephemeral",
          text: "🤖 *Aircall Intelligence Agent Commands*\n\n• `/agent run` - Trigger intelligence digest\n• `/agent status` - Check status\n• `/agent help` - Show this help\n\n✨ *Powered by Vercel (Node.js)*"
        };
      } else if (args[0] === 'run') {
        response = {
          response_type: "in_channel",
          text: `🚀 *Agent run completed!*\n\n📋 **Job ID:** \`${jobId}\`\n👤 **Triggered by:** @${userName}\n⚡ **Platform:** Vercel Serverless (Node.js)\n✅ **Status:** Completed successfully!`
        };
      } else if (args[0] === 'status') {
        response = {
          response_type: "ephemeral",
          text: `📊 **Agent Status:** All systems operational!\n\n🆔 **Job ID:** \`${jobId}\`\n⏰ **Time:** ${timestamp.substring(0, 16)}\n✨ **Platform:** Vercel (Node.js)`
        };
      } else {
        response = {
          response_type: "ephemeral",
          text: `❓ Unknown command: \`${args[0]}\`\n\nUse \`/agent help\` to see available commands.`
        };
      }

      res.status(200).json(response);
      return;
    }

    // Unknown POST endpoint
    res.status(404).json({
      error: "Unknown endpoint",
      path: path,
      method: method
    });
    return;
  }

  // Method not allowed
  res.status(405).json({
    error: "Method not allowed",
    method: method,
    path: path
  });
};