from typing import Callable
from functools import partial
import time
from logging import Logger
from sbc_statemachine.skilldatahandle import SkillDataHandle, ST_Parameter
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


class PythonFunctionExecuteSkill(BaseSkill):
    """Implementation for skill executing single python funtion, privided in constructor.
    All skill parameters will be set automaticly.
    Attention: see SUPPORTED_PARAMETER_TYPES + SUPPORTED_RETURN_TYPES!
    Examples:
        def custom_function(p1:float=1.0, p2:str="Test", p3:int=12)->int:
            ''' description for custom_function'''
            ...
        def custom_function2()->tuple[float, float, str, int]:
            ''' description for custom_function2'''
            ...
    """

    SUPPORTED_PARAMETER_TYPES = ["str", "int", "float"]
    SUPPORTED_RETURN_TYPES = ["str", "int", "float", "tuple"]
    RETURN_PARAMETER_NAME = "Return"

    def __init__(
        self,
        python_function: Callable,
        name_suffix: str = "",
        logger: Logger = None,
        **kwargs,
    ) -> None:
        """Implementation for skill executing single python funtion, privided in constructor.
            All skill parameters will be set automaticly.
            Attention: see SUPPORTED_PARAMETER_TYPES + SUPPORTED_RETURN_TYPES!

        Args:
            python_function (callable): python fucntion to warp with skill.
            logger (logging.Logger, optional): logger for logging. Defaults to None.
            **kwargs () : additional keyword arguments for skillstatemachine.SkillStateMachine.__init__
        """
        self.python_function: Callable = python_function

        # create skilldatahandle with function nam as skill name
        data = SkillDataHandle(skillName=python_function.__name__ + name_suffix)
        # set description by function doc string, replace line breaks and 3-spaces
        data.stSkillDataDefault.strDescription = (
            str(python_function.__doc__ if python_function.__doc__ else "")
            .replace("\n", "")
            .replace("   ", "")
        )

        # get kwarg names, types and defaults, seperate return
        self.kwarg_names = list(python_function.__annotations__.keys())
        self.kwarg_types = list(python_function.__annotations__.values())
        self.return_type = None
        if self.kwarg_names[-1] == "return":
            self.return_type = self.kwarg_types.pop(-1)
            self.kwarg_names.pop(-1)
        self.kwarg_defaults = (
            list(python_function.__defaults__) if python_function.__defaults__ else []
        )
        # check default value for each kwarg?
        if len(self.kwarg_names) != len(self.kwarg_defaults):
            raise KeyError(
                f"Set default value for each keyword argument of function '{python_function.__name__}'!"
            )
        # set parameters for kwargs
        for kwarg_name, kwarg_type, kwarg_default in zip(
            self.kwarg_names, self.kwarg_types, self.kwarg_defaults
        ):
            # check type
            if kwarg_type.__name__ not in self.SUPPORTED_PARAMETER_TYPES:
                raise TypeError(
                    f"Parameter type '{kwarg_type.__name__}' for kw argument '{kwarg_name}' of function '{python_function.__name__}' not supported!"
                )
            # add parameter
            data.stSkillDataDefault.astParameters.append(
                ST_Parameter(
                    strName=kwarg_name,
                    strDescr=f"type = '{str(kwarg_type.__name__)}'",
                    strValue=str(kwarg_default),
                )
            )
            data.stSkillDataDefault.iParameterCount += 1

        # add return parameter, if any
        if self.return_type:
            # check return type
            if self.return_type.__name__ not in self.SUPPORTED_RETURN_TYPES:
                raise TypeError(
                    f"Parameter type '{self.return_type.__name__}' for return value of function '{python_function.__name__}' not supported!"
                )

            # define function for adding return params
            def _add_return_param(ret_type, name_suffix: str = ""):
                if ret_type.__name__ not in self.SUPPORTED_PARAMETER_TYPES:
                    raise TypeError(
                        f"Parameter type '{ret_type.__name__}' for return of function '{python_function.__name__}' not supported!"
                    )
                return_default = "" if ret_type.__name__ == "str" else 0
                data.stSkillDataDefault.astParameters.append(
                    ST_Parameter(
                        strName=self.RETURN_PARAMETER_NAME + name_suffix,
                        strDescr=f"type = '{str(ret_type.__name__)}'",
                        strValue=str(return_default),
                    )
                )
                data.stSkillDataDefault.iParameterCount += 1

            # handle tuple as multiple return parameters
            if self.return_type.__name__ != "tuple":
                _add_return_param(self.return_type)
            else:
                # return is tuple
                # iterate __args__ and add parameters with name suffix
                for idx, sub_return_type in enumerate(list(self.return_type.__args__)):
                    _add_return_param(sub_return_type, f"_{idx+1}")

        # reset command data and init super class
        data.reset_SkillDataCommand()
        super().__init__(data=data, logger=logger, **kwargs)

    def S02_Execute_Execute(self) -> EStateResult:
        """get parameters as kwargs, execute python function, handle return"""
        # get kwargs from parameters
        kwargs = []
        for kwarg_name, kwarg_type in zip(self.kwarg_names, self.kwarg_types):
            kwargs.append(
                kwarg_type(self.data.get_Parameter_byName(kwarg_name, False).strValue)
            )
        # call python_function withs kwargs as args and get return
        try:
            ret = partial(self.python_function, *kwargs)()
        except Exception as e:
            print(
                f"Eecute Exception in skill '{self.data.stSkillDataDefault.strName}': {e}"
            )
        # handle return
        if self.return_type and ret:
            # handle return tuple
            if self.return_type.__name__ != "tuple":
                # set "Return" parameter as single value
                self.data.get_Parameter_byName(
                    self.RETURN_PARAMETER_NAME, False
                ).strValue = self.return_type(ret)
            else:
                # set multiple "Return_" parameters
                for idx, ret_type in enumerate(list(self.return_type.__args__)):
                    self.data.get_Parameter_byName(
                        self.RETURN_PARAMETER_NAME + f"_{idx+1}", False
                    ).strValue = str(ret_type(ret[idx]))
        return EStateResult.Done
