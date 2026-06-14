from ._anvil_designer import tip_evaluationTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class tip_evaluation(tip_evaluationTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self._current_view = 1
    self._populate_gameday_dropdown()
    self._update_views(max_gameday=None)

  def _populate_gameday_dropdown(self):
    played_matches = app_tables.top_matches.search(
      season="2025/2026",
      home_score=q.not_(None),
      away_score=q.not_(None)
    )
    gamedays = sorted(set(m["gameday"] for m in played_matches), reverse=True)
    items = [("Alle Spieltage", None)] + [(f"Spieltag {g}", g) for g in gamedays]
    self.drop_down_gameday.items = items
    self.drop_down_gameday.selected_value = None

  def _compute_stats(self, max_gameday=None):
    """Returns dict {user_name: {correct, money, penalties, net}} for all season participants."""
    if max_gameday is None:
      top_matches = list(app_tables.top_matches.search(
        season="2025/2026",
        home_score=q.not_(None),
        away_score=q.not_(None)
      ))
    else:
      top_matches = list(app_tables.top_matches.search(
        season="2025/2026",
        home_score=q.not_(None),
        away_score=q.not_(None),
        gameday=q.less_than_or_equal_to(max_gameday)
      ))

    stats = {}

    for match in top_matches:
      all_tips_for_match = list(app_tables.tips.search(gameday=match))
      correct_tips = [t for t in all_tips_for_match
                      if t["home_score"] == match["home_score"]
                      and t["away_score"] == match["away_score"]]

      tippers_this_gameday = set()
      for tip in all_tips_for_match:
        user_name = tip["user"]["user_name"]
        tippers_this_gameday.add(user_name)
        if user_name not in stats:
          stats[user_name] = {"correct": 0, "money": 0.0, "penalties": 0.0}

      for tip in correct_tips:
        user_name = tip["user"]["user_name"]
        stats[user_name]["correct"] += 1
        if len(correct_tips) > 0:
          stats[user_name]["money"] += match["jackpot"] / len(correct_tips)

      # 2€ Strafe für jeden Saison-Teilnehmer ohne Tipp an diesem Spieltag
      for user_name in stats:
        if user_name not in tippers_this_gameday:
          stats[user_name]["penalties"] += 2.0

    for user_name in stats:
      s = stats[user_name]
      s["net"] = s["money"] - s["penalties"]

    return stats

  def _update_views(self, max_gameday=None):
    stats = self._compute_stats(max_gameday)
    title_suffix = f" (bis Spieltag {max_gameday})" if max_gameday is not None else ""

    # --- View 1: Richtige Tipps ---
    sorted_correct = sorted(stats.items(), key=lambda x: x[1]["correct"], reverse=True)
    names_c = [u for u, _ in sorted_correct]
    vals_c = [s["correct"] for _, s in sorted_correct]

    fig1 = go.Figure(data=[go.Bar(x=names_c, y=vals_c)])
    fig1.update_layout(
      title="Richtige Tipps pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Richtige Tipps"
    )
    self.plot_correct_tips.figure = fig1
    self.rp_correct.items = [
      {"name": u, "value": str(s["correct"])} for u, s in sorted_correct
    ]

    # --- View 2: Gewinn ---
    sorted_money = sorted(stats.items(), key=lambda x: x[1]["money"], reverse=True)
    names_m = [u for u, _ in sorted_money]
    vals_m = [s["money"] for _, s in sorted_money]

    fig2 = go.Figure(data=[go.Bar(x=names_m, y=vals_m)])
    fig2.update_layout(
      title="Gewinn pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Gewinn (€)"
    )
    self.plot_money.figure = fig2
    self.rp_money.items = [
      {"name": u, "value": f"{s['money']:.2f} €"} for u, s in sorted_money
    ]

    # --- View 3: Strafen ---
    sorted_pen = sorted(stats.items(), key=lambda x: x[1]["penalties"], reverse=True)
    names_p = [u for u, _ in sorted_pen]
    vals_p = [s["penalties"] for _, s in sorted_pen]

    fig3 = go.Figure(data=[go.Bar(x=names_p, y=vals_p)])
    fig3.update_layout(
      title="Strafen pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Strafen (€)"
    )
    self.plot_penalties.figure = fig3
    self.rp_penalties.items = [
      {"name": u, "value": f"{s['penalties']:.2f} €"} for u, s in sorted_pen
    ]

    # --- View 4: Netto Gewinn ---
    sorted_net = sorted(stats.items(), key=lambda x: x[1]["net"], reverse=True)
    names_n = [u for u, _ in sorted_net]
    vals_n = [s["net"] for _, s in sorted_net]

    fig4 = go.Figure(data=[go.Bar(x=names_n, y=vals_n)])
    fig4.update_layout(
      title="Netto Gewinn pro Spieler" + title_suffix,
      xaxis_title="Tipper",
      yaxis_title="Netto Gewinn (€)"
    )
    self.plot_net.figure = fig4
    self.rp_net.items = [
      {
        "name": u,
        "brutto": f"{s['money']:.2f} €",
        "strafe": f"{s['penalties']:.2f} €",
        "netto": f"{s['net']:.2f} €"
      }
      for u, s in sorted_net
    ]

  def _show_view(self, view_index):
    self._current_view = view_index
    panels = [self.panel_view_1, self.panel_view_2, self.panel_view_3, self.panel_view_4]
    buttons = [self.btn_view_1, self.btn_view_2, self.btn_view_3, self.btn_view_4]
    for i, (panel, btn) in enumerate(zip(panels, buttons), start=1):
      panel.visible = (i == view_index)
      btn.role = "filled-button" if i == view_index else "outlined-button"

  def btn_view_1_click(self, **event_args):
    self._show_view(1)

  def btn_view_2_click(self, **event_args):
    self._show_view(2)

  def btn_view_3_click(self, **event_args):
    self._show_view(3)

  def btn_view_4_click(self, **event_args):
    self._show_view(4)

  def drop_down_gameday_change(self, **event_args):
    self._update_views(max_gameday=self.drop_down_gameday.selected_value)

  def button_back_click(self, **event_args):
    open_form('Form1')
