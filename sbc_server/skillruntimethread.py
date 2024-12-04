from typing import Callable
import time
import logging
import threading
from sbc_statemachine.skillstatemachinetypes import ESkillStates
from .cycletimer import CycleTimer
from .baseskill import BaseSkill


ERROR_HOLD_SKILL_STATES = [
    ESkillStates.Starting,
    ESkillStates.Execute,
    ESkillStates.Unholding,
    ESkillStates.Pausing,
    ESkillStates.Paused,
    ESkillStates.Resuming,
]


class SkillRuntimeThread(threading.Thread):
    """Runs skill implemented by BaseSkill class with a fixed cycletime as a thread."""

    def __init__(
        self,
        skill: BaseSkill,
        read_skill_data_extern: Callable[[BaseSkill], None] = None,
        write_skill_data_extern: Callable[[BaseSkill], None] = None,
        cycletime: float = 0.1,
        **kwargs,
    ) -> None:
        """Runs skill implemented by BaseSkill class with a fixed cycletime as a thread.

        Args:
            skill (BaseSkill): instance object of BaseSkill class
            read_skill_data_extern (Callable[[str], None], optional): external method for reading skill data before running skill cycle. Defaults to None.
            write_skill_data_extern (Callable[[str], None], optional): external method for writing skill data after running skill cycle. Defaults to None.
            cycletime (float, optional): cycletime for skill run call. Defaults to 0.1.
            **kwargs (): additional arguments for threading.Thread.__init__
        """
        super().__init__(**kwargs)
        self.skill: BaseSkill = skill
        self.read_skill_data_extern: Callable[[str], None] = read_skill_data_extern
        self.write_skill_data_extern: Callable[[str], None] = write_skill_data_extern
        self.cycletime = cycletime
        self.running = False

    def run(self) -> None:
        """Overrided method from Thread class. Will run when thread is started with .start()"""
        cycle_timer = CycleTimer(
            cycletime=self.cycletime, use_cycletime_correction=False
        )
        self.running = True
        while self.running:
            cycle_timer.start_cycle()
            if self.read_skill_data_extern is not None:
                self.read_skill_data_extern(self.skill)
            self.run_skill()
            if self.write_skill_data_extern is not None:
                self.write_skill_data_extern(self.skill)
            cycle_timer.end_cycle()
        self.stop_skill()

    def run_skill(self) -> bool:
        """call skill run method and check for exceptions

        Returns:
            bool: True, if skill runs without exception
        """
        try:
            self.skill.run_cycle()
            return True
        except Exception as e:
            logging.error(
                f"Exception while running skill '{self.skill.data.stSkillDataDefault.strName}' in state {self.skill.data.stSkillState.strActiveState}: {e}"
            )
            if self.skill.state in ERROR_HOLD_SKILL_STATES:
                self.skill.state = ESkillStates.Holding
            else:
                self.skill.state = ESkillStates.Stopping
            return False

    def stop_skill(self) -> None:
        """set stop command to skill and wait for stopped or aborted state"""
        self.skill.data.stSkillCommand.stCommand_State.Stop = True
        while not (
            self.skill.data.stSkillState.eActiveState == ESkillStates.Stopped
            or self.skill.data.stSkillState.eActiveState == ESkillStates.Aborted
        ):
            if not self.run_skill():
                break

    def start(self):
        """Start the thread's activity. also wait for running"""
        super().start()
        while not self.running:
            time.sleep(0.001)

    def stop(self):
        """external method for stopping skill runtime thread"""
        self.running = False
        self.join()
