PY=python3
VENV=env
SPINS?=100
SEED?=42
OUT?=out/runs/$(GAME)_demo
.PHONY: setup run clean
setup:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate; $(PY) -m pip install --upgrade pip
	. $(VENV)/bin/activate; $(PY) -m pip install -r requirements.txt
	. $(VENV)/bin/activate; $(PY) -m pip install -e .
run:
	@if [ -z "$(GAME)" ]; then echo "Usage: make run GAME=<game_id> [SPINS=... SEED=... OUT=...]"; exit 1; fi
	. $(VENV)/bin/activate; $(PY) run.py --game $(GAME) --spins $(SPINS) --seed $(SEED) --out $(OUT)
clean:
	rm -rf $(VENV) build dist *.egg-info
