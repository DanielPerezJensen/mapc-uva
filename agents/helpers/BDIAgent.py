from collections import namedtuple
from collections import deque



class BDIAgent():
    def __init__(self):
        self.beliefs = {}
        self.intentions = []

    def update_beliefs(self, msg):
        pass

        # self.beliefs["things"] = listofthings

    def add_intention(self, intention):
        self.intentions.append(intention)

    def drop_intention(self):
        for intention in self.intentions:
            # drop impossible intentions
            pass

    def execute_intentions(self):
        # execute first intention
        intention = self.intentions[0]
        # pop intention if succesful
        if intention:
            # pop
            pass
        else:
            self.drop_intention()



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
