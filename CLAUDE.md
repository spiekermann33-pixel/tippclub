# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TippClub is a Bundesliga (German football) tipping/prediction game app built with **Anvil** — a Python full-stack web framework where both client and server are written in Python. The app lets users submit score predictions (Tipps) for top matches, tracks results, and generates shareable tip sheets.

## Development Workflow

This is an **Anvil cloud app**, not a traditional pip-installable application. There are no local build/test/lint commands.

- **Edit**: Via Anvil IDE (cloud) or directly via git in this repo (bidirectional sync)
- **Run**: Anvil IDE "Run" button (cloud preview)
- **Deploy**: Anvil IDE "Publish" button
- **Dependencies**: Defined in `server_code/requirements.txt` — managed by Anvil, not pip locally

To run the app locally via uplink:
```bash
pip install anvil-uplink
python -m anvil.run_app_via_uplink <AppPackageName>
```

## Architecture

### Client/Server Split

- `client_code/` — Frontend Python compiled to JavaScript by Anvil runtime. No DOM access; uses Anvil UI components and event handlers.
- `server_code/ServerModule1.py` — Backend Python running in Anvil's sandboxed server. Decorated with `@anvil.server.callable` to expose functions to the client.

### Key Forms (`client_code/Form1/`)

- **Form1**: Main page — gameday selector, matchup display, user tip entry grid, save/download
- **tip_evaluation/**: Statistics page with Plotly charts (wins, prize money per player, matchday filter)
- **add_new_match/**: Admin form to add/edit matches; has auto-calculate via football-data.org API
- **add_tips_json/**: JSON import subform
- **RowTemplate1–4, ItemTemplate1**: Templates used inside `RepeatingPanel` components

### Server Functions (`server_code/ServerModule1.py`)

- `create_tip_image()`: Generates an HTML/CSS card-style tip sheet and converts to PNG via WeasyPrint
- `find_top_match()`: Calls football-data.org API to fetch Bundesliga standings/fixtures and determines the top match by team rank
- `get_user_tips()`, `get_matchup_jackpot()`: Data aggregation helpers

### Database (Anvil Data Tables)

Schema defined in `anvil.yaml`, managed via Anvil dashboard:

| Table | Key Columns |
|---|---|
| `users` | user_name, user_id, sex, active, fav_teams (link) |
| `top_matches` | season, gameday, home_team, away_team, home_score, away_score, jackpot |
| `tips` | gameday (link→top_matches), user (link→users), home_score, away_score |
| `fav_teams` | team_id, team_name, logo |

### External API

Football-data.org API key is stored as an Anvil secret: `anvil.secrets.get_secret('football-data-api')`. Never hardcode this value.

## Key Patterns

- **Server callables**: Long-running or privileged operations (image gen, API calls, DB writes) live in `ServerModule1.py` with `@anvil.server.callable`; client calls them via `anvil.server.call('function_name', ...)`
- **RepeatingPanel**: Used throughout for dynamic lists; each row uses an `ItemTemplate` or `RowTemplate` form
- **Data binding**: Anvil data binding links UI component properties to Python attributes
- **UI language**: German (Spieltag, Tipp, Preisgeld, Tippzettel, etc.) — keep UI strings in German

## Configuration Files

- `anvil.yaml`: Central config — app name, DB schema, runtime (Python 3.10), secrets, startup form
- `.anvil_editor.yaml`: Unique IDs for forms/assets used by Anvil IDE — do not edit manually
- `theme/parameters.yaml`: Material Design 3 color scheme (primary: #6750A4 purple)
