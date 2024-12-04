import threading
import time
import logging
from .skillruntimethread import SkillRuntimeThread, BaseSkill
from .cycletimer import CycleTimer

BASE_SLEEP_TIME_TICK = 0.05


class SkillServer(threading.Thread):
    """Base server class holding and running skills"""

    def __init__(
        self,
        skills: list[BaseSkill],
        skill_cycletime: float = 0.5,
        server_cycletime: float = 1.0,
        server_name: str = "SkillServer",
        logger: logging.Logger = None,
        **kwargs,
    ) -> None:
        """Base server class holding and running skills

        Args:
            skills (list[BaseSkill]): instance objects of all skills to run
            skill_cycletime (float, optional): skill runtime thread cycletime. Defaults to 0.5.
            server_cycletime (float, optional): server cycletime. Defaults to 1.0.
            server_name (str, optional): server name. Defaults to "SkillServer".
            logger (logging.Logger, optional): logger for logging. Defaults to None.
            **kwargs (): additional arguments for threading.Thread.__init__

        Raises:
            KeyError: if skills with identical skill names detected.
        """
        self.server_name = server_name
        super().__init__(name=f"{server_name}_Thread", **kwargs)
        # set base sleep time tick for waiting cycles dependant to skill_cycletime
        self.base_sleep_time_tick = min(BASE_SLEEP_TIME_TICK, skill_cycletime / 2.0)
        self.server_cycletime = server_cycletime
        # generate skill runtime threads
        self.skill_runtime_threads: dict[str, SkillRuntimeThread] = {}
        for skill in skills:
            skill_name = skill.data.stSkillDataDefault.strName
            if skill_name in self.skill_runtime_threads:
                raise KeyError(f"Skill with name '{skill_name}' already registered!")
            self.skill_runtime_threads[skill_name] = SkillRuntimeThread(
                skill=skill,
                read_skill_data_extern=self.read_skill_data,
                write_skill_data_extern=self.write_skill_data,
                cycletime=skill_cycletime,
                name=skill_name + "_RuntimeThread",
            )
        self.running = False
        self.logger = logger

    def run(self):
        """runs the server with following steps:
        1. start server
        2. run server cycle until self.running is set to False
        3. stop server"""
        self.start_server()
        cycle_timer = CycleTimer(
            cycletime=self.server_cycletime, use_cycletime_correction=False
        )
        self.running = True
        while self.running:
            cycle_timer.start_cycle()
            self.server_cycle()
            cycle_timer.end_cycle()
        self.stop_server()

    def start_server(self):
        """server start method.  Can be overrided with subclass but also call this method!"""
        # start skill_runtime_threads
        self._start_skill_runtime_threads()
        if self.logger:
            self.logger.info(f"SkillServer {self.server_name}: server started.")

    def _start_skill_runtime_threads(self):
        """starts all skill_runtime_threads"""
        for skill_name in self.skill_runtime_threads:
            self.skill_runtime_threads[skill_name].start()

    def server_cycle(self):
        """server cycle method. Override with subclass."""
        if self.logger:
            self.logger.debug(f"SkillServer {self.server_name}: server cycle called.")

    def stop_server(self):
        """server stop method. Can be overrided with subclass but also call this method!"""
        # stop skill_runtime_threads
        self._stop_skill_runtime_threads()
        if self.logger:
            self.logger.info(f"SkillServer {self.server_name}: server stopped.")

    def _stop_skill_runtime_threads(self):
        """stops all skill_runtime_threads"""
        for skill_name in self.skill_runtime_threads:
            self.skill_runtime_threads[skill_name].running = False
        for skill_name in self.skill_runtime_threads:
            self.skill_runtime_threads[skill_name].join()

    def read_skill_data(self, skill_name: str):
        """method for skill to read data from server. Override with subclass

        Args:
            skill_name (str): name of skill
        """
        pass

    def write_skill_data(self, skill_name: str):
        """method for skill to write data to server. Override with subclass

        Args:
            skill_name (str): name of skill
        """
        pass

    def start(self):
        """Start the thread's activity. also wait for running"""
        super().start()
        while not self.running:
            time.sleep(0.001)

    def stop(self):
        """external method for stopping server"""
        self.running = False
        self.join()
