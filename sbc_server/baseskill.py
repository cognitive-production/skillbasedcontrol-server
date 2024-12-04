import time
import logging
import uuid
from sbc_statemachine.skillstatemachine import SkillStateMachine
from sbc_statemachine.skillstatemachinetypes import EStateResult
from sbc_statemachine.skilldatahandle import SkillDataHandle
from sbc_statemachine.skilldatatypes import ST_SkillData


class BaseSkill(SkillStateMachine):
    """base class for implementing skills in python.
    Implement funcionality in method S02_Execute_Execute and other state methods.
    """

    def __init__(
        self, data: SkillDataHandle = None, logger: logging.Logger = None, **kwargs
    ) -> None:
        """base class for implementing skills in python.
        Implement funcionality in method S02_Execute_Execute and other state methods.

        Args:
            data (SkillDataHandle, optional): skill data handle with fille stSkillDataDefault. Defaults to None.
            logger (logging.Logger, optional): logger for logging. Defaults to None.
            **kwargs () : additional keyword arguments for skillstatemachine.SkillStateMachine.__init__
        """
        if data is None:
            data = SkillDataHandle()
            data.stSkillDataDefault = ST_SkillData(
                strName=(
                    str(self.__class__.__name__) + "_" + str(uuid.uuid4())
                ).replace("-", ""),
                strType=str(self.__class__.__name__),
            )
        super().__init__(skill_data_handle=data, logger=logger, **kwargs)
        self.data.reset_SkillDataCommand()
        self.data.stSkillState.stCommandEnabled.ResetEnabled = True
        self.data.stSkillState.stCommandEnabled.StartEnabled = True
        self.data.stSkillState.stCommandEnabled.StopEnabled = True
        self.data.stSkillState.stCommandEnabled.HoldEnabled = True
        self.data.stSkillState.stCommandEnabled.UnholdEnabled = True
        self.data.stSkillState.stCommandEnabled.AbortEnabled = True

    def run_cycle(self):
        """Run skill."""
        super().run_cycle(
            reset=self.data.stSkillCommand.stCommand_State.Reset,
            start=self.data.stSkillCommand.stCommand_State.Start,
            stop=self.data.stSkillCommand.stCommand_State.Stop,
            hold=self.data.stSkillCommand.stCommand_State.Hold,
            unhold=self.data.stSkillCommand.stCommand_State.Unhold,
            pause=self.data.stSkillCommand.stCommand_State.Pause,
            resume=self.data.stSkillCommand.stCommand_State.Resume,
            abort=self.data.stSkillCommand.stCommand_State.Abort,
            restart=self.data.stSkillCommand.stCommand_State.Restart,
            complete=self.data.stSkillCommand.stCommand_State.Complete,
            mode_offline=self.data.stSkillCommand.stCommand_Mode.Offline,
            mode_operator=self.data.stSkillCommand.stCommand_Mode.Operator,
            mode_automatic_internal=self.data.stSkillCommand.stCommand_Mode.Automatic_Intern,
            mode_automatic_external=self.data.stSkillCommand.stCommand_Mode.Automatic_Extern,
        )
        self._set_SkillState()
        self._reset_CommandsMode()
        self._reset_CommandsState()

    def _set_SkillState(self) -> None:
        """set strings for mode and state in stSkillState."""
        self.data.stSkillState.eActiveMode = self.mode.value
        self.data.stSkillState.strActiveMode = self.mode.name
        self.data.stSkillState.eActiveState = self.state.value
        self.data.stSkillState.strActiveState = self.state.name
        self.data.stSkillState.eActiveCommand = self.command.value
        self.data.stSkillState.strActiveCommand = self.command.name

    def _reset_CommandsMode(self) -> None:
        """reset all skill mode commands."""
        self.data.stSkillCommand.stCommand_Mode.Offline = False
        self.data.stSkillCommand.stCommand_Mode.Operator = False
        self.data.stSkillCommand.stCommand_Mode.Automatic_Intern = False
        self.data.stSkillCommand.stCommand_Mode.Automatic_Extern = False

    def _reset_CommandsState(self) -> None:
        """reset all skill state commands."""
        self.data.stSkillCommand.stCommand_State.Abort = False
        self.data.stSkillCommand.stCommand_State.Stop = False
        self.data.stSkillCommand.stCommand_State.Hold = False
        self.data.stSkillCommand.stCommand_State.Pause = False
        self.data.stSkillCommand.stCommand_State.Reset = False
        self.data.stSkillCommand.stCommand_State.Start = False
        self.data.stSkillCommand.stCommand_State.Complete = False
        self.data.stSkillCommand.stCommand_State.Unhold = False
        self.data.stSkillCommand.stCommand_State.Resume = False
        self.data.stSkillCommand.stCommand_State.Restart = False

    ## State Methods to reimplement by specific skill implementations

    def S00_Idle_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S01_Starting_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S02_Execute_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S03_Completing_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S04_Completed_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S05_Pausing_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S06_Paused_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S07_Resuming_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S08_Holding_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S09_Held_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S10_Unholding_Execute(self) -> EStateResult:
        self.data.stSkillState.bError = False
        return EStateResult.Done

    def S11_Stopping_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S12_Stopped_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S13_Aborting_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S14_Aborted_Execute(self) -> EStateResult:
        return EStateResult.Done

    def S15_Resetting_Execute(self) -> EStateResult:
        self.data.stSkillState.bError = False
        self.data.stSkillState.udiErrorID = 0
        self.data.stSkillState.strErrorMsg = ""
        return EStateResult.Done

    ## end of state Methods to reimplement by specific skill implementations


class DelayedSkill(BaseSkill):
    def __init__(self, data: SkillDataHandle = None, delay: float = 5) -> None:
        """simple 'dummy' skill with delay time.

        :param data: skill data handle, defaults to None
        :type data: SkillDataHandle, optional
        :param delay: delay time in seconds, defaults to 5 sec
        :type delay: float, optional
        """
        super().__init__(data)
        self.delay_time = delay

    def S02_Execute_Execute(self):
        time.sleep(self.delay_time)
        return EStateResult.Done


class ExternalExecute(BaseSkill):
    def S02_Execute_Execute(self):
        if self.data.stSkillCommand.StateComplete:
            self.data.stSkillCommand.StateComplete = False
            return EStateResult.Done
        else:
            return EStateResult.Busy
