# BASIC EVENT TRACKER

- For SNUCC SDE inductions
- Started out with Elixir + Phoenix, but due to lack of time ended up doing basic python version of it
- cd into python_script_version and run: `python3 event_tracker.py` for CLI version and `python3 event_management_platform_gui.py` for GUI version
- No point in running Phoenix as of now, can look at code in folder event_management_platform if interested
- Added a JavaScript Version (an attempt), used Vite + React + JS and FastAPI + SQLite + SQLalchemy
- To run the Javascript version, cd into event_tracker_js:
  1) cd into event_tracker_frontend: `npm install` then `npm run dev`
  2) cd into event_tracker_backend: `pip install -r requirements.txt` then ` uvicorn main:app --reload`
  3) UI will be available on http://localhost:5173/
  4) Can check if backend is working on http://localhost:8000/docs
