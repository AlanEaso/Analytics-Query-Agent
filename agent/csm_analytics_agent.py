import os
import sys

parent_dir = os.path.dirname(os.getcwd())
sys.path.append(parent_dir)

from knowledge_base.reports import Report

class CSMAnalytsgent:
  def __init__(self):
    self.knowledge_base = Report()

  def search_reports(self, query: str, top_k: int = 3):
    return self.knowledge_base.search_reports(query, top_k)