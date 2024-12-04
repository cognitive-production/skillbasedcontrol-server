from logging import Logger
import unittest
from sbc_statemachine.skilldatahandle import SkillDataHandle
from sbc_statemachine.skillstatemachinetypes import (
    ESkillStates,
    ESkillModes,
    ESkillCommands,
)
from sbc_server.baseskill import BaseSkill


class BaseSkillImplementation(BaseSkill):
    def __init__(
        self,
        skill_name: str,
        logger: Logger = None,
        init_state: ESkillStates = ESkillStates.Idle,
    ) -> None:
        data = SkillDataHandle()
        data.stSkillDataDefault.strName = skill_name
        super().__init__(data=data, logger=logger, init_state=init_state)


class TestBaseSkillImplementation(unittest.TestCase):

    def test_abort(self):
        for state in ESkillStates:
            if state in [
                ESkillStates.Undefined,
                ESkillStates.NotUsed,
                ESkillStates.Aborted,
                ESkillStates.Aborting,
            ]:
                continue
            self.skill = BaseSkillImplementation("TestSkill", init_state=state)
            self.assertEqual(self.skill.state, state)
            self.skill.data.stSkillCommand.stCommand_State.Abort = True
            self.skill.run_cycle()
            self.assertEqual(
                self.skill.state,
                ESkillStates.Aborting,
                msg=f"Not switching to aborting with state {state.name}",
            )
            self.assertEqual(self.skill.command, ESkillCommands.Abort)
            self.skill.run_cycle()
            self.assertEqual(self.skill.state, ESkillStates.Aborted)
            self.assertEqual(self.skill.command, ESkillCommands.Undefined)
            self.skill.data.stSkillCommand.stCommand_State.Reset = True
            self.skill.run_cycle()
            self.assertEqual(self.skill.state, ESkillStates.Resetting)
            self.assertEqual(self.skill.command, ESkillCommands.Reset)

    def test_stop(self):
        for state in ESkillStates:
            if state in [
                ESkillStates.Undefined,
                ESkillStates.NotUsed,
                ESkillStates.Aborted,
                ESkillStates.Aborting,
                ESkillStates.Stopping,
                ESkillStates.Stopped,
            ]:
                continue
            self.skill = BaseSkillImplementation("TestSkill", init_state=state)
            self.assertEqual(self.skill.state, state)
            self.skill.data.stSkillCommand.stCommand_State.Stop = True
            self.skill.run_cycle()
            self.assertEqual(
                self.skill.state,
                ESkillStates.Stopping,
                msg=f"Not switching to stopping with state {state.name}",
            )
            self.assertEqual(self.skill.command, ESkillCommands.Stop)
            self.skill.run_cycle()
            self.assertEqual(self.skill.state, ESkillStates.Stopped)
            self.assertEqual(self.skill.command, ESkillCommands.Undefined)
            self.skill.data.stSkillCommand.stCommand_State.Reset = True
            self.skill.run_cycle()
            self.assertEqual(self.skill.state, ESkillStates.Resetting)
            self.assertEqual(self.skill.command, ESkillCommands.Reset)

    def test_start_execute_complete_reset(self):
        self.skill = BaseSkillImplementation("TestSkill")
        self.assertEqual(self.skill.state, ESkillStates.Idle)
        self.skill.data.stSkillCommand.stCommand_State.Start = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Starting)
        self.assertEqual(self.skill.command, ESkillCommands.Start)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Execute)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Completing)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Completed)
        self.skill.data.stSkillCommand.stCommand_State.Reset = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Resetting)
        self.assertEqual(self.skill.command, ESkillCommands.Reset)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Idle)

    def test_start_execute_hold_unholding_execute(self):
        self.skill = BaseSkillImplementation("TestSkill")
        self.assertEqual(self.skill.state, ESkillStates.Idle)
        self.skill.data.stSkillCommand.stCommand_State.Start = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Starting)
        self.assertEqual(self.skill.command, ESkillCommands.Start)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Execute)
        self.skill.data.stSkillCommand.stCommand_State.Hold = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Holding)
        self.assertEqual(self.skill.command, ESkillCommands.Hold)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Held)
        self.skill.data.stSkillCommand.stCommand_State.Unhold = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Unholding)
        self.assertEqual(self.skill.command, ESkillCommands.Unhold)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Execute)

    def test_start_execute_pause_resuming_execute(self):
        self.skill = BaseSkillImplementation("TestSkill")
        self.skill.set_command_enabled(pause_enabled=True, resume_enabled=True)
        self.assertEqual(self.skill.state, ESkillStates.Idle)
        self.skill.data.stSkillCommand.stCommand_State.Start = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Starting)
        self.assertEqual(self.skill.command, ESkillCommands.Start)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Execute)
        self.skill.data.stSkillCommand.stCommand_State.Pause = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Pausing)
        self.assertEqual(self.skill.command, ESkillCommands.Pause)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Paused)
        self.skill.data.stSkillCommand.stCommand_State.Resume = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Resuming)
        self.assertEqual(self.skill.command, ESkillCommands.Resume)
        self.skill.run_cycle()
        self.assertEqual(self.skill.state, ESkillStates.Execute)

    def test_switch_mode(self):
        self.skill = BaseSkillImplementation("TestSkill")
        self.skill.data.stSkillCommand.stCommand_Mode.Offline = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.mode, ESkillModes.Offline)
        self.skill.data.stSkillCommand.stCommand_Mode.Operator = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.mode, ESkillModes.Operator)
        self.skill.data.stSkillCommand.stCommand_Mode.Automatic_Intern = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.mode, ESkillModes.Automatic_Internal)
        self.skill.data.stSkillCommand.stCommand_Mode.Automatic_Extern = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.mode, ESkillModes.Automatic_External)
        self.skill.data.stSkillCommand.stCommand_Mode.Offline = True
        self.skill.run_cycle()
        self.assertEqual(self.skill.mode, ESkillModes.Offline)
