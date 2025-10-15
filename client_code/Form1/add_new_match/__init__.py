from ._anvil_designer import add_new_matchTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class add_new_match(add_new_matchTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.

  def add_new_tips_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Form1')
