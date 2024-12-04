import time
from .skillserver import SkillServer


USER_INPUT_COMMANDS = ["q", "quit"]


def run_skillserver(skill_server: SkillServer):
    """starts the skill_server, runs infinity loop, wait for user input (see USER_INPUT_COMMANDS)

    Args:
        skill_server (SkillServer): SkillServer or subclass object
    """

    skill_server.start()
    while True:
        try:
            user_input = input(f"Enter command {USER_INPUT_COMMANDS}: ")
        except KeyboardInterrupt:
            break
        if user_input in ["q", "quit"]:
            break
    skill_server.stop()
