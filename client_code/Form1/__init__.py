from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    # fill drop_down_gameday
    game_days = []
    for row in app_tables.top_matches.search():
      game_days.append(str(row["gameday"]))
    self.drop_down_gameday.items = game_days

    # fill user tips for gameday
    self.user_tips_rows.items = [
      {"name":"Henrik","club":"Gladbach"}
    ]    