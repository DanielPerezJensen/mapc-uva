from collections import namedtuple


class BDIAgent():
    def __init__(self):
        self.beliefs = {}

    def update_beliefs(self, msg):
        percept = msg["content"]["percept"]

        print(percept["things"])

        # self.beliefs["things"] = listofthings


"""
"percept": {
  "lastActionParams": [],
  "score": 0,
  "task": "",
  "lastAction": "no_action",
  "things": [
    {
      "x": -1,
      "y": 1,
      "details": "B",
      "type": "entity"
    },
    {
      "x": 0,
      "y": 0,
      "details": "B",
      "type": "entity"
    },
    {
      "x": 0,
      "y": 1,
      "details": "B",
      "type": "entity"
    },
    {
      "x": 0,
      "y": 1,
      "details": "A",
      "type": "entity"
    },
    {
      "x": 0,
      "y": 0,
      "details": "A",
      "type": "entity"
    },
    {
      "x": -1,
      "y": 1,
      "details": "A",
      "type": "entity"
    }
  ],
  "attached": [],
  "disabled": false,
  "terrain": {},
  "lastActionResult": "success",
  "tasks": [],
  "energy": 300
},
"""
