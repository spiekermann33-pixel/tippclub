from ._anvil_designer import tip_evaluationTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from plotly import graph_objects as go
import anvil.tables.query as q

class tip_evaluation(tip_evaluationTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens

  @handle("plot_tip_evaluation", "show")
  def plot_tip_evaluation_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    user_tip_evaluation = {}
    top_matches = app_tables.top_matches.search(season="2025/2026",
                                               home_score=q.not_(None),
                                               away_score=q.not_(None))
    for top_match in top_matches:
      # print(top_match["home_team"],top_match["away_team"],top_match["jackpot"])
      users_with_correct_tip = app_tables.tips.search(gameday=top_match,
                                                    home_score=top_match['home_score'],
                                                    away_score=top_match['away_score'])
      for user in users_with_correct_tip:
        user_name = user['user']["user_name"]
        user_evaluation = user_tip_evaluation.get(user_name, 
                                        {"won_games" : 0,"won_money" : 0})
        user_evaluation["won_games"] += 1
        user_evaluation["won_money"] += top_match["jackpot"] / len(users_with_correct_tip)

        user_tip_evaluation.update({user_name : user_evaluation})

      # print(user_tip_evaluation)

    user_tip_evaluation = sorted(user_tip_evaluation.items(), key=lambda x: x[1]["won_games"], reverse=True)
    
    names = [item[0] for item in user_tip_evaluation]
    won_games = [item[1]["won_games"] for item in user_tip_evaluation]
    
    fig = go.Figure(
      data=[go.Bar(
        x=names,
        y=won_games
      )]
    )
    
    fig.update_layout(
      title="Gewonnene Spiele pro Spieler",
      xaxis_title="Tipper",
      yaxis_title="Gewonnene Spiele"
    )
    
    self.plot_tip_evaluation.figure = fig

    # nach gewonnenem Geld sortieren
    user_tip_money = sorted(
      user_tip_evaluation,
      key=lambda x: x[1]["won_money"],
      reverse=True
    )
    
    names_money = [item[0] for item in user_tip_money]
    won_money = [item[1]["won_money"] for item in user_tip_money]
    
    fig_money = go.Figure(
      data=[go.Bar(
        x=names_money,
        y=won_money
      )]
    )
    
    fig_money.update_layout(
      title="Gewonnenes Geld pro Spieler",
      xaxis_title="Tipper",
      yaxis_title="Gewonnenes Geld (€)"
    )
    
    self.plot_tip_money.figure = fig_money

  def button_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Form1')