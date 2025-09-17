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
      output_row = {"name" : user["user_name"],
                    "user": user, }
      tip = app_tables.tips.get(user=user, gameday=topmatch)
      output_row.update({"tip_row" : tip})
      if tip:
        output_row.update({
          "tip":f"{tip['home_score']} : {tip['away_score']}"
        })
      
      user_tips.append(output_row)
    self.repeating_panel_user_tips.items = user_tips

  def drop_down_gameday_change(self, **event_args):
    """This method is called when an item is selected"""
    self._set_data_grid_user_tips(int(self.drop_down_gameday.selected_value))

  def button_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    gameday = app_tables.top_matches.get(season="2025/2026",gameday=int(self.drop_down_gameday.selected_value))
    for item in self.repeating_panel_user_tips.items:
      user = item['user']
      tip_text = item.get("tip","")

      try:
        home_score, away_score = [int(x) for x in tip_text.split(":")]
      except Exception:
        home_score, away_score = None, None  # ungültig oder leer      

      user_tip = app_tables.tips.get(gameday=gameday, user=user)
      # wenn user bereits tipp abgegeben hat
      if user_tip:
        user_tip.update(home_score=home_score,away_score=away_score)
      elif home_score and away_score:
        app_tables.tips.add_row(gameday=gameday,user=user,home_score=home_score,away_score=away_score)