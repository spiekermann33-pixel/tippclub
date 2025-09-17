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
    self._set_drop_down_gameday()

    # fill user tips for gameday
    self._set_data_grid_user_tips(int(self.drop_down_gameday.selected_value))

  def _set_drop_down_gameday(self, ):
    game_days = []
    for row in app_tables.top_matches.search():
      game_days.append(str(row["gameday"]))
    self.drop_down_gameday.items = game_days

  def _set_data_grid_user_tips(self, gameday):
    topmatch = app_tables.top_matches.get(gameday=gameday)

    user_tips = []
    for user in app_tables.users.search(active=True):
      output_row = {"name" : user["user_name"]}
      tip = app_tables.tips.get(user=user, gameday=topmatch)
      if tip:
        output_row.update({
          "tip":f"{tip['home_score']} : {tip['away_score']}"
        })

      user_tips.append(output_row)
    self.repeating_panel_user_tips.items = user_tips

  def drop_down_gameday_change(self, **event_args):
    """This method is called when an item is selected"""
    self._set_data_grid_user_tips(int(self.drop_down_gameday.selected_value))
      