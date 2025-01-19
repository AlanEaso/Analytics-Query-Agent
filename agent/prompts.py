class Prompt:
  def __init__(self):
    pass

  def kb_summary(self):
    return """
        {
          "supported_domains": ["win_loss", "cac", "mrr", "lead_cost", "feature_adoption", "deal_conversion", "sales_performance"],
          
          "industry_sectors": [
            "healthcare", "technology", "financial_services", "manufacturing", 
            "retail", "education", "government", "professional_services", "smb"
          ],
          
          "regions": ["north_america", "emea", "latam", "global"],
          
          "common_metrics": {
            "win_loss": ["win_rate", "loss_rate", "conversion_rate"],
            "cac": ["cac", "roi", "customer_lifetime_value"],
            "mrr": ["mrr", "churn_rate", "expansion_rate"],
            "lead_cost": ["cost_per_lead", "conversion_rate", "campaign_roi"],
            "feature_adoption": ["adoption_rate", "usage_frequency", "user_satisfaction"],
            "deal_conversion": ["conversion_rate", "deal_velocity", "average_deal_size"],
            "sales_performance": ["revenue", "growth_rate", "market_share"]
          },

          "common_dimensions": [
            "region", "country", "industry", "company_size", "product_line",
            "customer_segment", "sales_channel", "time_period"
          ]
        }
        """