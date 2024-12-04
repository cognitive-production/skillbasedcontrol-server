import time
import unittest
from test_baseskill import BaseSkillImplementation, ESkillStates
from sbc_server.skillruntimethread import SkillRuntimeThread


class TestBaseSkillImplementation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.skill = BaseSkillImplementation("TestSkill")
        cls.cycletime = 0.5
        cls.skill_runtime_thread = SkillRuntimeThread(
            skill=cls.skill, cycletime=cls.cycletime
        )

    @classmethod
    def tearDownClass(cls):
        cls.skill_runtime_thread.stop()

    def test_SkillRuntimeThread(self):
        self.assertIsNotNone(self.skill)
        self.assertIsNotNone(self.skill_runtime_thread)
        self.skill_runtime_thread.start()
        assert self.skill.data.stSkillState.eActiveState == ESkillStates.Idle.value
        self.skill.data.stSkillCommand.stCommand_State.Start = True
        time.sleep(5 * self.cycletime)
        print(self.skill.data.stSkillState.eActiveState)
        print(ESkillStates.Completed.value)
        assert self.skill.data.stSkillState.eActiveState == ESkillStates.Completed.value
        self.skill.data.stSkillCommand.stCommand_State.Reset = True
        time.sleep(5 * self.cycletime)
        assert self.skill.data.stSkillState.eActiveState == ESkillStates.Idle.value
