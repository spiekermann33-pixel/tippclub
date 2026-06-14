from ._anvil_designer import stats_rowTemplate
from anvil import *


class stats_row(stats_rowTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.label_name.text = self.item.get("name", "")
    self.label_value.text = self.item.get("value", "")
