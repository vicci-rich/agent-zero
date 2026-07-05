### behaviour_adjustment:
update agent behaviour per user request
write instructions to add or remove to adjustments arg
to wipe all custom rules and restore defaults, set adjustments to "reset"
usage:
~~~json
{
    "thoughts": [
        "...",
    ],
    "headline": "Adjusting agent behavior per user request",
    "tool_name": "behaviour_adjustment",
    "tool_args": {
        "adjustments": "remove...",
    }
}
~~~
