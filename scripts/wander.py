"""Run the simulator's ``cook`` command with idle chefs wandering.

The default PDDL controller leaves a chef standing still when the plan gives
it nothing to do, which looks flat in a crowded kitchen. This wrapper makes
those chefs stroll about instead. A chef that holds something, or still has
plan steps left, is left alone, so the cooking is unchanged apart from the
extra foot traffic.

record-hero.py runs this in the simulator's environment in place of ``cook``:

    cd ../overcooked-2
    uv run python ../too-many-chefs-landing/scripts/wander.py agent --level ...
"""

from __future__ import annotations

import random

from controllers.pddl.default_controller import DefaultPDDLController
from main import main
from simulator.entities import ORIENTATION_DELTAS
from simulator.mutations import MoveAgentForward, TurnAgent
from simulator.mutations.move_agent import is_walkable

# Seeded, so a recording comes out the same each time.
rng = random.Random(0)
planned_actions = DefaultPDDLController.get_actions

# How often a wandering chef keeps walking straight on when it can.
KEEP_GOING = 0.75


def get_actions(self, environment, context):
    actions = planned_actions(self, environment, context)
    if self.is_busy() or not self._has_planned:
        return actions

    acting = {getattr(action, "agent_id", None) for action in actions}
    for agent in self.controllable_agents(environment):
        if agent.id in acting or agent.held_item_id is not None:
            continue
        progress = self.plan_progress(agent.id)
        if progress is not None and progress[0] < progress[1]:
            continue

        def clear(orientation):
            dx, dy = ORIENTATION_DELTAS[orientation]
            return is_walkable(environment, agent.x + dx, agent.y + dy)

        if clear(agent.orientation) and rng.random() < KEEP_GOING:
            actions.append(MoveAgentForward(agent_id=agent.id))
            continue
        turns = [o for o in ORIENTATION_DELTAS if o != agent.orientation and clear(o)]
        if turns:
            actions.append(TurnAgent(agent_id=agent.id, orientation=rng.choice(turns)))
    return actions


DefaultPDDLController.get_actions = get_actions

if __name__ == "__main__":
    main()
