import time
from logging import Logger
from sbc_statemachine.skilldatahandle import SkillDataHandle
from sbc_statemachine.skillstatemachinetypes import EStateResult
from .baseskill import BaseSkill


class DelayedSkill(BaseSkill):
    """simple implementation of python skill with delayed Execute state."""

    def __init__(
        self,
        data: SkillDataHandle = None,
        delaytime: float = 1.0,
        logger: Logger = None,
        **kwargs,
    ) -> None:
        """simple implementation of python skill with delayed Execute state

        Args:
            data (SkillDataHandle, optional): skill data handle with fille stSkillDataDefault. Defaults to None.
            delaytime (float, optional): delay time in execute state in seconds. Defaults to 1.0.
            logger (logging.Logger, optional): logger for logging. Defaults to None.
            **kwargs () : additional keyword arguments for skillstatemachine.SkillStateMachine.__init__
        """
        super().__init__(data=data, logger=logger, **kwargs)
        self.delaytime = delaytime

    def S02_Execute_Execute(self) -> EStateResult:
        """Sleep for delaytime in execute."""
        time.sleep(self.delaytime)
        return EStateResult.Done


class DummyJsonSkill(DelayedSkill):
    """Gets data rom json file. simple implementation of python skill with delayed Execute state."""

    def __init__(
        self,
        jsondatafile: str,
        delaytime: float = 1,
        logger: Logger = None,
        **kwargs,
    ) -> None:
        data = SkillDataHandle()
        data.set_fromJsonFile(jsondatafile, toSkillDataDefault=True)
        data.reset_SkillDataCommand()
        super().__init__(data=data, delaytime=delaytime, logger=logger, **kwargs)


class ExternalExecuteSkill(BaseSkill):
    """base implementation for skill waiting for external stSkillCommand.StateComplete set in Execute state"""

    def S02_Execute_Execute(self):
        """Wait for external state complete signal in Execute state."""
        if self.data.stSkillCommand.StateComplete:
            self.data.stSkillCommand.StateComplete = False
            return EStateResult.Done
        else:
            return EStateResult.Busy
