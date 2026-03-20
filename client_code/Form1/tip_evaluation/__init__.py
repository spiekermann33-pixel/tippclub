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

    # Populate dropdown with played matchdays
    self._populate_gameday_dropdown()

  def _populate_gameday_dropdown(self):
    """Fills the dropdown with all played matchdays (descending) plus 'Alle' option."""
    played_matches = app_tables.top_matches.search(
      season="2025/2026",
      home_score=q.not_(None),
      away_score=q.not_(None)
    )
    gamedays = sorted(set(m["gameday"] for m in played_matches), reverse=True)
    items = [("Alle Spieltage", None)] + [(f"Spieltag {g}", g) for g in gamedays]
    self.drop_down_gameday.items = items
    self.drop_down_gameday.selected_value = None

  def _update_charts(self, max_gameday=None):
    """Draws both charts, optionally filtered up to max_gameday."""
    user_tip_evaluation = {}

    if max_gameday is None:
      top_matches = app_tables.top_matches.search(
        season="2025/2026",
        home_score=q.not_(None),
        away_score=q.not_(None)
      )
    else:
      top_matches = app_tables.top_matches.search(
        season="2025/2026",
        home_score=q.not_(None),
        away_score=q.not_(None),
        gameday=q.less_than_or_equal_to(max_gameday)
      )

    for top_match in top_matches:
      users_with_correct_tip = app_tables.tips.search(
        gameday=top_match,
        home_score=top_match['home_score'],
        away_score=top_match['away_score']
      )
      for user in users_with_correct_tip:
        user_name = user['user']["user_name"]
        user_evaluation = user_tip_evaluation.get(user_name,
                                        {"won_games": 0, "won_money": 0})
        user_evaluation["won_games"] += 1
        user_evaluation["won_money"] += top_match["jackpot"] / len(users_with_correct_tip)
        user_tip_evaluation[user_name] = user_evaluation

    user_tip_evaluation = sorted(
      user_tip_evaluation.items(),
      key=lambda x: x[1]["won_games"],
      reverse=True
    )

    names = [item[0] for item in user_tip_evaluation]
    won_games = [item[1]["won_games"] for item in user_tip_evaluation]

    title_suffix = f" (bis Spieltag {max_gameday})" if max_gameday is not None else ""

    fig = go.Figure(
      data=[go.Bar(x=names, y=won_games)]
    )
    fig.update_layout(
      title="Gewonnene Spiele pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Gewonnene Spiele"
    )
    self.plot_tip_evaluation.figure = fig

    user_tip_money = sorted(
      user_tip_evaluation,
      key=lambda x: x[1]["won_money"],
      reverse=True
    )
    names_money = [item[0] for item in user_tip_money]
    won_money = [item[1]["won_money"] for item in user_tip_money]

    fig_money = go.Figure(
      data=[go.Bar(x=names_money, y=won_money)]
    )
    fig_money.update_layout(
      title="Gewonnenes Geld pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Gewonnenes Geld (€)"
    )
    self.plot_tip_money.figure = fig_money

  @handle("plot_tip_evaluation", "show")
  def plot_tip_evaluation_show(self, **event_args):
    """This method is called when the Plot is shown on the screen"""
    self._update_charts(max_gameday=None)

  def drop_down_gameday_change(self, **event_args):
    """This method is called when the selected gameday changes"""
    selected = self.drop_down_gameday.selected_value
    self._update_charts(max_gameday=selected)

  def button_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    open_form('Form1')
