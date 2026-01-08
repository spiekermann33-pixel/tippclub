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
    # 1. Holen der Daten als Integers für korrekte Sortierung
    for row in app_tables.top_matches.search():
      if row["gameday"]:
        game_days.append(int(row["gameday"]))
    # 2. Numerisch sortieren (Absteigend: Höchste Zahl zuerst)
    game_days.sort(reverse=True)
    # 3. Liste für das Dropdown (1 bis 34)
    all_game_days = [str(i) for i in range(1, 35)]
    self.drop_down_gameday.items = all_game_days
    # 4. Höchsten Spieltag ermitteln
    if game_days:
      highest_existing_gameday = game_days[0] # Das ist jetzt sicher eine Zahl
    else:
      highest_existing_gameday = 0
    # 5. Den nächsten Spieltag auswählen (max. 34)
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
      if home_team and away_team and jackpot:
        season = self.label_season.text
        app_tables.top_matches.add_row(gameday=gameday,season=season,home_team=home_team,\
                                    away_team=away_team,home_score=home_goals,\
                                      away_score=away_goals, jackpot=jackpot)
      else:
        self.rich_text_save_error.content = \
              """<span style="color:red">Heim-, Auswärtsteam und Preisgeld muss gepflegt sein</span>."""
        
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
      self.text_box_jackpot.text = "48"

  @handle("button_auto_calculate_matchday", "click")
  def button_auto_calculate_matchday_click(self, **event_args):
    """This method is called when the button is clicked"""
    # function return: 
    #{'home': 'Eintracht Frankfurt', 'away': 'Borussia Dortmund', 'home_rank': 7, 
    #'away_rank': 2, 'sum': 9}
    try:
      game_dict = anvil.server.call('find_top_match')
    except:
      game_dict = None
  
    if game_dict == None:
      print("Berechnen des Spiels fehlgeschlagen")
    else:
      self.text_box_hometeam.text = game_dict["home"]
      self.text_box_awayteam.text = game_dict["away"]

      # set template text for group chat
      template_text = f"""⚽ **Spieltag {self.drop_down_gameday.selected_value}** ⚽\n📅 Am {game_dict['kickoff']} Uhr 🕗\n{game_dict["home"]} - {game_dict["away"]} ⚔️\n\n💰 Im Pott sind aktuell: {self.text_box_jackpot.text}€ 💸\n\nGut Tipp 🤟🍀"""
      self.rich_text_tip_template.content = template_text