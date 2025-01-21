from pymongo import MongoClient
from datetime import datetime
import uuid
from loguru import logger
import os

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGODB_URI'))
        self.db = self.client.csm_analytics
        logger.info("Connected to MongoDB")

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

    def create_escalation_ticket(self, conversation_id, original_query, suggested_reports, preliminary_analysis, probing_details):
        ticket = {
            "ticket_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "original_query": original_query,
            "suggested_reports": suggested_reports,
            "probing_details": probing_details,
            "preliminary_analysis": preliminary_analysis,
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.db.escalation_tickets.insert_one(ticket)
        logger.info(f"Created escalation ticket: {ticket['ticket_id']}")
        return ticket["ticket_id"]

    def update_escalation_status(self, ticket_id, status):
        self.db.escalation_tickets.update_one(
            {"ticket_id": ticket_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        # logger.info(f"Updated ticket {ticket_id} status to {status}")

    def log_llm_interaction(self, conversation_id, prompt, response, model, tokens_used, conversation_type):
        log_entry = {
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow(),
            "prompt": prompt,
            "response": response,
            "model": model,
            "tokens_used": tokens_used,
            "converation_type": conversation_type,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.db.llm_logs.insert_one(log_entry)
        logger.info(f"Logged LLM interaction for {conversation_type}")

    def get_all_escalation_tickets(self):
        return list(self.db.escalation_tickets.find())
