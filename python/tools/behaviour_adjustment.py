from python.helpers import behaviour
from python.helpers.tool import Tool, Response
from agent import Agent
from python.helpers.log import LogItem


# adjustments that mean "wipe the custom ruleset and go back to default"
RESET_KEYWORDS = {"", "reset", "clear", "default", "reset to default", "reset to defaults"}


class UpdateBehaviour(Tool):

    async def execute(self, adjustments="", **kwargs):

        # stringify adjustments if needed
        if not isinstance(adjustments, str):
            adjustments = str(adjustments)

        # allow clearing a stale / bad ruleset from within a chat (no shell access needed)
        if adjustments.strip().lower() in RESET_KEYWORDS:
            existed = behaviour.reset_rules(self.agent)
            self.log.update(
                result="Behaviour reset to default" if existed else "No custom behaviour to reset"
            )
            return Response(
                message=self.agent.read_prompt("behaviour.updated.md"), break_loop=False
            )

        await update_behaviour(self.agent, self.log, adjustments)
        return Response(
            message=self.agent.read_prompt("behaviour.updated.md"), break_loop=False
        )


async def update_behaviour(agent: Agent, log_item: LogItem, adjustments: str):

    # get system message and current ruleset
    system = agent.read_prompt("behaviour.merge.sys.md")
    current_rules = behaviour.read_rules(agent)

    # log query streamed by LLM
    async def log_callback(content):
        log_item.stream(ruleset=content)

    msg = agent.read_prompt(
        "behaviour.merge.msg.md", current_rules=current_rules, adjustments=adjustments
    )

    # call util llm to merge the adjustments into the ruleset
    adjustments_merge = await agent.call_utility_model(
        system=system,
        message=msg,
        callback=log_callback,
    )

    # update rules file (single source of truth; capped on read)
    behaviour.write_rules(agent, adjustments_merge)
    log_item.update(result="Behaviour updated")
