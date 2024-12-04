import logging
import time
from sbc_statemachine.skilldatahandle import (
    SkillDataHandle,
    ST_Parameter,
)
from sbc_statemachine.skillstatemachinetypes import EStateResult
from sbc_server.baseskill import BaseSkill
from sbc_server.skillimplementations import (
    DelayedSkill,
    ExternalExecuteSkill,
)

# examples for custom skill implementations


class AddSkill(BaseSkill):
    """custom skill calculating sum of two numbers"""

    def __init__(self, logger: logging.Logger = None):
        data = SkillDataHandle()
        data.set_fromJsonFile("examples/skills/AddSkill.json", True)
        data.reset_SkillDataCommand()
        super().__init__(data=data, logger=logger)

    def S02_Execute_Execute(self):
        try:
            op1 = float(self.data.stSkillDataCommand.astParameters[0].strValue)
            op2 = float(self.data.stSkillDataCommand.astParameters[1].strValue)
            result = op1 + op2
            self.data.stSkillDataCommand.astParameters[2].strValue = str(result)
            if self.logger:
                self.logger.info(
                    f"Executed AddSkill operation: {op1} + {op2} = {result}"
                )
        except Exception as e:
            self.data.stSkillDataCommand.astParameters[2].strValue = ""
            self.data.stSkillState.strErrorMsg = (
                f"Executed AddSkill finished with error: {e}"
            )
            if self.logger:
                self.logger.error(self.data.stSkillState.strErrorMsg)
            self.data.stSkillState.bError = True
            return EStateResult.Error
        return EStateResult.Done


class MyJointSpaceSkill(DelayedSkill):
    """custom skill simulating robot movement in joint space."""

    def __init__(self, logger: logging.Logger = None):
        data = SkillDataHandle()
        data.set_fromJsonFile("examples/skills/MyJointSpaceSkill.json", True)
        data.reset_SkillDataCommand()
        super().__init__(data=data, logger=logger)


class GripperSkill(DelayedSkill):
    """custom skill simulating robot gripper."""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("GripperSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 3
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter("Grip_Release", "0", "", "0:Release, 1:Grip")
        )
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "Grip_Range",
                "10.0",
                "mm",
                "Grip ragne in mm, " ": empty means no specific grip range",
            )
        )
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter("Grip_Force", "100", "%", "Gripper force in %")
        )
        super().__init__(data=stSkillDataHandle, delaytime=1.0, logger=logger)

    def S02_Execute_Execute(self):
        grip_release = self.data.stSkillDataCommand.astParameters[0].strValue
        grip_range = self.data.stSkillDataCommand.astParameters[1].strValue
        grip_force = self.data.stSkillDataCommand.astParameters[2].strValue
        match grip_release:
            case "0":
                if self.logger:
                    self.logger.info(f"Release gripper.")
            case "1":
                if self.logger:
                    self.logger.info(
                        f"Grip with range {grip_range}mm and force {grip_force}%."
                    )
            case _:
                if self.logger:
                    self.logger.info(
                        f"Wrong Grip_Release parameter! Is {grip_release}, expected 0 or 1"
                    )
        return super().S02_Execute_Execute()


class MovePosByJsonStringSkill(DelayedSkill):
    """custom skill simulating robot movement in task space by json string parameter."""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("MovePosByJsonStringSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 1
        posString = "{'x':0.0, 'y':0.0, 'z': 0.0}"
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "PositionString",
                posString,
                "mm",
                "x, y, z positions in mm as json string",
            )
        )
        super().__init__(data=stSkillDataHandle, delaytime=1.0, logger=logger)

    def S02_Execute_Execute(self):
        posString = self.data.stSkillDataCommand.astParameters[0].strValue
        if self.logger:
            self.logger.info(
                f"{self.data.stSkillDataDefault.strName}: Moving to {posString}."
            )
        return super().S02_Execute_Execute()


class SleepSkill(BaseSkill):
    """custom skill for waiting / sleeping."""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("SleepSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 1
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "Sleeptime",
                "1",
                "sec",
                "sleeptime in seconds",
            )
        )
        super().__init__(data=stSkillDataHandle, logger=logger)

    def S02_Execute_Execute(self):
        sleeptime = 1.0
        try:
            sleeptime = float(self.data.stSkillDataCommand.astParameters[0].strValue)
            time.sleep(sleeptime)
        except Exception as e:
            print(f"SleepSkill exception: {e}")
        return EStateResult.Done


class NoParamSkill(BaseSkill):
    """custom skill without parameters"""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("NoParamSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 0
        super().__init__(stSkillDataHandle, logger=logger)


class MultiReturnSkill(BaseSkill):
    """custom skill with multiple return/result parameters"""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("MultiReturnSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 3
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "Return_1",
                "0",
                "",
                "return value 1",
            )
        )
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "Return_2",
                "1.123",
                "",
                "return value 2",
            )
        )
        stSkillDataHandle.stSkillDataDefault.astParameters.append(
            ST_Parameter(
                "Return_3",
                "abc",
                "",
                "return value 3",
            )
        )
        super().__init__(stSkillDataHandle, logger=logger)


class CustomExternalExecuteSkill(ExternalExecuteSkill):
    """custom skill waiting for external state complete signal in Execute state."""

    def __init__(self, logger: logging.Logger = None) -> None:
        stSkillDataHandle = SkillDataHandle("CustomExternalExecuteSkill")
        stSkillDataHandle.stSkillDataDefault.iParameterCount = 0
        super().__init__(stSkillDataHandle, logger)
