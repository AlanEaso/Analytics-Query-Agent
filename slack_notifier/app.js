const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;
const EXTERNAL_SLACK_NOTIFIER_API_KEY = process.env.EXTERNAL_SLACK_NOTIFIER_API_KEY

const verifyApiKey = (req, res, next) => {
  const providedKey = req.headers['x-api-key'];
  
  if (!providedKey || providedKey !== EXTERNAL_SLACK_NOTIFIER_API_KEY) {
      return res.status(401).json({ error: 'Invalid API key' });
  }
  next();
};

app.post('/notify', verifyApiKey, async (req, res) => {
  try {
      const { message } = req.body;
      await axios.post(SLACK_WEBHOOK_URL, {
          text: message
      });
      console.log(`Successfully sent notification: ${message}`);
      res.status(200).json({ success: true });
  } catch (error) {
      console.error('Error sending notification:', error);
      res.status(500).json({ 
          success: false, 
          error: 'Failed to send notification' 
      });
  }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});