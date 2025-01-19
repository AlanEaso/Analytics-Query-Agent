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
        }
        """