from ._anvil_designer import stats_row_nettoTemplate
from anvil import *


class stats_row_netto(stats_row_nettoTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.label_name.text = self.item.get("name", "")
    self.label_brutto.text = self.item.get("brutto", "")
    self.label_strafe.text = self.item.get("strafe", "")
    self.label_netto.text = self.item.get("netto", "")
