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

    # fill drop_down_gameday
    self._set_drop_down_gameday()

  def add_new_tips_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Form1')


  def _set_drop_down_gameday(self):
    """Set the drop-down menu items for the game days."""
    game_days = []
    # Retrieve all game days from the database
    for row in app_tables.top_matches.search():
      game_days.append(str(row["gameday"]))
    game_days.sort(reverse=True)
    # Generate a list of all possible game days (1 to 34)
    all_game_days = [str(i) for i in range(1, 35)]
    self.drop_down_gameday.items = all_game_days
    # Determine the highest existing game day
    if game_days:
      highest_existing_gameday = int(game_days[0])
    else:
      highest_existing_gameday = 0
    # Set the selected item to the highest existing game day + 1
    selected_gameday = str(min(highest_existing_gameday + 1, 34))
    self.drop_down_gameday.selected_value = selected_gameday

  def get_gameday(self, ):
    gameday = int(self.drop_down_gameday.selected_value)
    return app_tables.top_matches.get(gameday=gameday)
    
  def button_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    home_team = self.text_box_hometeam.text
    away_team = self.text_box_awayteam.text

    home_goals = self.text_box_home_goals.text
    away_goals = self.text_box_away_goals.text
    
    gameday = self.get_gameday()
    if gameday is not None:
      # update of existing game
      gameday.update(home_team=home_team,away_team=away_team,\
                     home_score=home_goals,away_score=away_goals)
    else:
      gameday = int(self.drop_down_gameday.selected_value)
      jackpot = self.text_box_jackpot.text
      if home_team is not None and away_team is not None and jackpot is not None:
        season = self.label_season.text
        app_tables.top_matches.add_row(gameday=gameday,season=season,home_team=home_team,\
                                    away_team=away_team,home_score=home_goals,\
                                      away_score=away_goals, jackpot=jackpot)
        
  def drop_down_gameday_change(self, **event_args):
    """This method is called when an item is selected"""
    gameday = self.get_gameday()
    if gameday is not None:
      self.text_box_hometeam.text = gameday["home_team"]
      self.text_box_awayteam.text = gameday["away_team"]
      self.text_box_home_goals.text = gameday["home_score"]
      self.text_box_away_goals.text = gameday["away_score"]
      self.text_box_jackpot.text = gameday["jackpot"]
    else:
      self.text_box_hometeam.text = ""
      self.text_box_awayteam.text = ""
      self.text_box_home_goals.text = ""
      self.text_box_away_goals.text = ""

    

