from python.helpers.extension import Extension
from agent import LoopData
from python.helpers import behaviour


class BehaviourPrompt(Extension):

    async def execute(self, system_prompt: list[str] = [], loop_data: LoopData = LoopData(), **kwargs):
        # inject the (fail-safe, size-capped) behaviour ruleset at the top of the prompt
        system_prompt.insert(0, behaviour.read_rules(self.agent))
