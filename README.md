# My Agent

A small test project for managing `levels` and `spaces` through typed tools.

The project has 2 run modes:

- `run_runner.py` - deterministic runner for the JSON payload from the task
- `run_agent.py` - demo with OpenAI Agents SDK and natural-language prompts in French

## What Is Included

- in-memory store without an external database
- Pydantic models for `Level`, `Space`, and tool responses
- tools for `insert/get/update` operations on `level` and `space`
- a strict runner that resolves placeholders separately for `level_id` and `space_id`

## Installation

```bash
python -m venv venv
venv\Scripts\activate
cp example.env .env
pip install -r requirements.txt
```

Fill the created `.env` file based on `example.env` and set:

- `CHAT_GPT_KEY` - your OpenAI API key
- `MODEL_NAME` - optional, defaults to `gpt-4o-mini`

## Run

Runner with the JSON payload:

```bash
python run_runner.py
```

Agent demo with OpenAI Agents SDK:

```bash
python run_agent.py
```

## Expected Behavior

`run_runner.py` should not crash with a traceback. It executes the payload step by step and prints:

- successful create and update steps
- expected `error` results for invalid cases from the task
- the final in-memory database state

`run_agent.py` should not crash and should:

- create a level
- create a space on that level
- rename the space
- handle a request with a non-existing level correctly
- print the final database state

# My calls traces

---

```bash
❯ python .\run_agent.py
USER: Ajoute un niveau Rez-de-chaussée avec floor_number 0.
INFO [tools] CALL insert_level(args=('Rez-de-chaussée', 0), kwargs={})
INFO [tools] RETURN insert_level -> {"message":"Level created","data":[{"level_id":1,"name":"Rez-de-chaussée","floor_number":0}],"status":"success"}
AGENT: Le niveau "Rez-de-chaussée" a été créé avec succès. Son ID est 1.

USER: Ajoute un espace Cuisine sur le niveau Rez-de-chaussée.
INFO [tools] CALL insert_space(args=(), kwargs={'name': 'Cuisine', 'level_id': 1, 'non_visit_reason': None})
INFO [tools] RETURN insert_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine","level_id":1,"non_visit_reason":null}],"status":"success"}
AGENT: L'espace "Cuisine" a été créé avec succès sur le niveau "Rez-de-chaussée". Son ID est 1.

USER: Renomme la Cuisine en Cuisine ouverte.
INFO [tools] CALL update_space(args=(), kwargs={'space_id': 1, 'name': 'Cuisine ouverte', 'level_id': 1, 'non_visit_reason': None})
INFO [tools] RETURN update_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine ouverte","level_id":1,"non_visit_reason":null}],"status":"success"}
AGENT: L'espace "Cuisine" a été renommé en "Cuisine ouverte" avec succès.

USER: Ajoute une Chambre sur un niveau qui n'existe pas pour vérifier la gestion d'erreur.
INFO [tools] CALL insert_space(args=(), kwargs={'name': 'Chambre', 'level_id': 999, 'non_visit_reason': None})
Level you are trying to get does not exist
INFO [tools] RETURN insert_space -> {"message":"Level you are trying to get does not exist","data":[],"status":"error"}
AGENT: L'ajout de l'espace "Chambre" a échoué, car le niveau spécifié n'existe pas.

level_id=1 name='Rez-de-chaussée' floor_number=0
  space_id=1 name='Cuisine ouverte' level_id=1 non_visit_reason=None
```

---

```bash
❯ python .\run_runner.py
INFO [tools] CALL insert_level(args=(), kwargs={'name': 'Rez-de-chaussée', 'floor_number': 0})
INFO [tools] RETURN insert_level -> {"message":"Level created","data":[{"level_id":1,"name":"Rez-de-chaussée","floor_number":0}],"status":"success"}
INFO [tools] CALL insert_space(args=(), kwargs={'name': 'Cuisine', 'level_id': 1})
INFO [tools] RETURN insert_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine","level_id":1,"non_visit_reason":null}],"status":"success"}
INFO [tools] CALL update_space(args=(), kwargs={'space_id': 1, 'non_visit_reason': 'Pièce fermée à clé'})
INFO [tools] RETURN update_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine","level_id":1,"non_visit_reason":"Pièce fermée à clé"}],"status":"success"}
INFO [tools] CALL update_space(args=(), kwargs={'space_id': 1, 'name': 'Cuisine ouverte'})
INFO [tools] RETURN update_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine ouverte","level_id":1,"non_visit_reason":"Pièce fermée à clé"}],"status":"success"}
INFO [tools] CALL update_space(args=(), kwargs={'space_id': 1, 'non_visit_reason': None})
INFO [tools] RETURN update_space -> {"message":"Space created","data":[{"space_id":1,"name":"Cuisine ouverte","level_id":1,"non_visit_reason":null}],"status":"success"}
INFO [tools] CALL insert_space(args=(), kwargs={'name': 'Chambre', 'level_id': 'lvl_does_not_exist'})
Level you are trying to get does not exist
INFO [tools] RETURN insert_space -> {"message":"Level you are trying to get does not exist","data":[],"status":"error"}
INFO [tools] CALL update_level(args=(), kwargs={'level_id': 1})
INFO [tools] RETURN update_level -> {"message":"Level updated","data":[{"level_id":1,"name":"Rez-de-chaussée","floor_number":0}],"status":"success"}
INFO [tools] CALL insert_level(args=(), kwargs={'floor_number': 1})
name is required
INFO [tools] RETURN insert_level -> {"message":"Validation error: name is required","data":[],"status":"error"}
{'step': 0, 'tool': 'insert_level', 'args': {'name': 'Rez-de-chaussée', 'floor_number': 0}, 'status': 'ok', 'result': '{"message":"Level created","data":[{"level_id":1,"name":"Rez-de-chaussée","floor_number":0}],"status":"success"}'}
{'step': 1, 'tool': 'insert_space', 'args': {'name': 'Cuisine', 'level_id': 1}, 'status': 'ok', 'result': '{"message":"Space created","data":[{"space_id":1,"name":"Cuisine","level_id":1,"non_visit_reason":null}],"status":"success"}'}
{'step': 2, 'tool': 'update_space', 'args': {'space_id': 1, 'non_visit_reason': 'Pièce fermée à clé'}, 'status': 'ok', 'result': '{"message":"Space created","data":[{"space_id":1,"name":"Cuisine","level_id":1,"non_visit_reason":"Pièce fermée à clé"}],"status":"success"}'}
{'step': 3, 'tool': 'update_space', 'args': {'space_id': 1, 'name': 'Cuisine ouverte'}, 'status': 'ok', 'result': '{"message":"Space created","data":[{"space_id":1,"name":"Cuisine ouverte","level_id":1,"non_visit_reason":"Pièce fermée à clé"}],"status":"success"}'}
{'step': 4, 'tool': 'update_space', 'args': {'space_id': 1, 'non_visit_reason': None}, 'status': 'ok', 'result': '{"message":"Space created","data":[{"space_id":1,"name":"Cuisine ouverte","level_id":1,"non_visit_reason":null}],"status":"success"}'}
{'step': 5, 'tool': 'insert_space', 'args': {'name': 'Chambre', 'level_id': 'lvl_does_not_exist'}, 'status': 'error', 'result': '{"message":"Level you are trying to get does not exist","data":[],"status":"error"}', 'error': 'Level you are trying to get does not exist'}
{'step': 6, 'tool': 'update_level', 'args': {'level_id': 1}, 'status': 'ok', 'result': '{"message":"Level updated","data":[{"level_id":1,"name":"Rez-de-chaussée","floor_number":0}],"status":"success"}'}
{'step': 7, 'tool': 'insert_level', 'args': {'floor_number': 1}, 'status': 'error', 'result': '{"message":"Validation error: name is required","data":[],"status":"error"}', 'error': 'Validation error: name is required'}

level_id=1 name='Rez-de-chaussée' floor_number=0
  space_id=1 name='Cuisine ouverte' level_id=1 non_visit_reason=None
```
