import enum
import time
import logging
import dataclasses
from asyncua.sync import Server, SyncNode, ua, new_struct
import asyncua.common.structures104 as uastr
from sbc_statemachine.skilldatatypes import (
    ST_Skill,
    ST_SkillCommand,
    ST_SkillState,
    ST_SkillData,
    ST_Parameter,
    ST_Base,
)
from .mapVar import mapVar, copy
from .skillserver import SkillServer
from .baseskill import BaseSkill

OPCUA_TYPE_SUFFIX = "_py"  # type suffix for multi vendor servers

OPCUA_Types = {}  # dict for storing opc ua skill types


@dataclasses.dataclass
class Skill_Node_Handle:
    """dataclass for storing opc ua node handles for each skill"""

    skill_name: str
    skill_node: SyncNode = None
    skill_Command_node: SyncNode = None
    skill_State_node: SyncNode = None
    skill_DataDefault_node: SyncNode = None
    skill_DataCommand_node: SyncNode = None
    stSkillCommand_marker: ST_SkillCommand = dataclasses.field(
        default_factory=ST_SkillCommand
    )
    stSkillDataCommand_marker: ST_SkillData = dataclasses.field(
        default_factory=ST_SkillData
    )


class SkillServer_OPCUA(SkillServer):
    def __init__(
        self,
        skills: list[BaseSkill],
        skill_cycletime: float = 0.5,
        server_cycletime: float = 0.1,
        server_name: str = "BaseSkilldControl OPC UA Server",
        hostname: str = "0.0.0.0",
        port: int = 4840,
        namespaceIndex: int = 2,
        logger: logging.Logger = None,
        **kwargs,
    ) -> None:
        """opc ua server providing and running skills

        Args:
            skills (list[BaseSkill]): instance objects of all skills to run
            skill_cycletime (float, optional): skill runtime thread cycletime. Defaults to 0.5.
            server_cycletime (float, optional): server cycletime. Will be set to skill_cycletime/2 if longer! Defaults to 0.1.
            server_name (str, optional): opc ua server name. Defaults to "BaseSkilldControl OPC UA Server".
            hostname (str, optional): hostname like ip. Defaults to "0.0.0.0".
            port (int, optional): opc ua server port. Defaults to 4840.
            namespaceIndex (int, optional): opc ua namespace index for skill nodes. Defaults to 2.
            logger (logging.Logger, optional): logger for logging. Defaults to None.
            **kwargs (): additional arguments for threading.Thread.__init__
        """
        super().__init__(
            skills=skills,
            skill_cycletime=skill_cycletime,
            server_cycletime=server_cycletime,
            server_name=server_name,
            logger=logger,
            **kwargs,
        )
        self.hostname = hostname
        self.port = port
        self.server_name = server_name
        self.server = Server()  # create opc ua server
        self.skillNodeHandles = self._init_skill_node_handles(skills)
        # write_change_struct_markers
        self.namespaceIndex = namespaceIndex

    def _init_skill_node_handles(
        self, skills: list[BaseSkill]
    ) -> dict[str, Skill_Node_Handle]:
        """init skill nodes for opc ua server

        Args:
            skills (list[BaseSkill]): list of skill objects

        Raises:
            KeyError: if skill_name duplicate

        Returns:
            dict[str, SkillNodeHandle]: dictionary of SkillNodeHandles
        """
        skill_nodehandles: dict[str, Skill_Node_Handle] = {}
        for skill in skills:
            skill_name = skill.data.stSkillDataDefault.strName
            if skill_name in skill_nodehandles:
                raise KeyError(f"Skill with name '{skill_name}' already registered!")
            skill_nodehandles[skill_name] = Skill_Node_Handle(
                skill_name=skill_name,
                stSkillCommand_marker=copy.deepcopy(skill.data.stSkillCommand),
                stSkillDataCommand_marker=copy.deepcopy(skill.data.stSkillDataCommand),
            )
        return skill_nodehandles

    def start_server(self):
        """start opc ua server, register skill types and add skills"""
        # init opc ua server
        # self.server.init()
        self.server.set_endpoint(f"opc.tcp://{self.hostname}:{self.port}")
        self.server.set_server_name(self.server_name)
        # start opc ua server
        self.server.start()
        if self.logger:
            self.logger.info(
                f"Started OPC UA Server '{self.server_name}' with endpoint 'opc.tcp://{self.hostname}:{self.port}'."
            )
        # register skill types
        register_skill_type_to_asyncua_server(
            cls=ST_Skill,
            server=self.server,
            OPCUA_Types=OPCUA_Types,
            logger=self.logger,
        )
        if self.logger:
            self.logger.info(
                f"Registered skill types to OPC UA Server '{self.server_name}' with endpoint 'opc.tcp://{self.hostname}:{self.port}'."
            )
        # add skill nodes to server
        for skill_name in self.skillNodeHandles:
            self._addSkill(skill_name=skill_name)
            if self.logger:
                self.logger.info(f"Added skill '{skill_name}' to OPC UA Server.")
        # write skill data
        for skill_name in self.skill_runtime_threads:
            self.write_skill_data_force(
                self.skill_runtime_threads[skill_name].skill, True
            )
        if self.logger:
            self.logger.info(
                f"Added skill nodes to OPC UA Server '{self.server_name}' with endpoint 'opc.tcp://{self.hostname}:{self.port}'."
            )
        # call super method
        super().start_server()
        # wait 2 seconds for opc ua server backgroudn start up
        time.sleep(2.0)

    def stop_server(self):
        """stop"""
        # call super method
        super().stop_server()
        # stop opc ua server
        self.server.stop()
        if self.logger:
            self.logger.info(
                f"Stopped OPC UA Server '{self.server_name}' with endpoint 'opc.tcp://{self.hostname}:{self.port}'."
            )

    def _addSkill(self, skill_name: str):
        """add skill nodes to opc ua server"""
        # skill node
        skill_node = self.server.nodes.objects.add_folder(
            ua.NodeId(skill_name, self.namespaceIndex),
            skill_name,
        )
        self.skillNodeHandles[skill_name].skill_node = skill_node
        # skill command node
        self.skillNodeHandles[skill_name].skill_Command_node = skill_node.add_variable(
            ua.NodeId(skill_name + ".stSkillCommand", self.namespaceIndex),
            "stSkillCommand",
            ua.Variant(OPCUA_Types[ST_SkillCommand](), ua.VariantType.ExtensionObject),
        )
        self.skillNodeHandles[skill_name].skill_Command_node.set_writable()
        # add skill state node
        self.skillNodeHandles[skill_name].skill_State_node = skill_node.add_variable(
            ua.NodeId(skill_name + ".stSkillState", self.namespaceIndex),
            "stSkillState",
            ua.Variant(OPCUA_Types[ST_SkillState](), ua.VariantType.ExtensionObject),
        )
        # add skill data default
        self.skillNodeHandles[skill_name].skill_DataDefault_node = (
            skill_node.add_variable(
                ua.NodeId(skill_name + ".stSkillDataDefault", self.namespaceIndex),
                "stSkillDataDefault",
                ua.Variant(OPCUA_Types[ST_SkillData](), ua.VariantType.ExtensionObject),
                # ua.Variant(ua.ST_SkillData_py(), ua.VariantType.ExtensionObject),
            )
        )
        # add skill data command
        self.skillNodeHandles[skill_name].skill_DataCommand_node = (
            skill_node.add_variable(
                ua.NodeId(skill_name + ".stSkillDataCommand", self.namespaceIndex),
                "stSkillDataCommand",
                ua.Variant(OPCUA_Types[ST_SkillData](), ua.VariantType.ExtensionObject),
                # ua.Variant(ua.ST_SkillData_py(), ua.VariantType.ExtensionObject),
            )
        )
        self.skillNodeHandles[skill_name].skill_DataCommand_node.set_writable()

    def read_skill_data(self, skill: BaseSkill) -> None:
        """read skill data from opc ua server

        Args:
            skill_name (str): name of skill
        """
        skill_name = skill.data.stSkillDataDefault.strName
        skill_node_handle = self.skillNodeHandles[skill_name]
        # stSkillCommand
        d = skill_node_handle.skill_Command_node.read_value()
        mapVar(d, skill.data.stSkillCommand)
        # mark stSkillCommand
        skill_node_handle.stSkillCommand_marker = copy.deepcopy(
            skill.data.stSkillCommand
        )
        # stSkillDataCommand
        d = skill_node_handle.skill_DataCommand_node.read_value()
        mapVar(d, skill.data.stSkillDataCommand)
        # mark stSkillDataCommand
        skill_node_handle.stSkillDataCommand_marker = copy.deepcopy(
            skill.data.stSkillDataCommand
        )

    def write_skill_data(self, skill: BaseSkill) -> None:
        """write skill data to opc ua server nodes

        Args:
            skill_name (str): name of skill
        """
        self.write_skill_data_force(skill)

    def write_skill_data_force(self, skill: BaseSkill, force: bool = False) -> None:
        """write skill data to opc ua server nodes with force option

        Args:
            skill_name (str): name of skill
        """
        skill_name = skill.data.stSkillDataDefault.strName
        skill_node_handle = self.skillNodeHandles[skill_name]
        # stSkillCommand, only if changed since last read_skill_data
        if (
            force
            or skill.data.stSkillCommand != skill_node_handle.stSkillCommand_marker
        ):
            d = OPCUA_Types[ST_SkillCommand]()
            mapVar(skill.data.stSkillCommand, d)
            skill_node_handle.skill_Command_node.write_value(
                d, ua.VariantType.ExtensionObject
            )
        # stSkillState
        d = OPCUA_Types[ST_SkillState]()
        mapVar(skill.data.stSkillState, d)
        skill_node_handle.skill_State_node.write_value(
            d, ua.VariantType.ExtensionObject
        )
        # stSkillDataDefault
        d = OPCUA_Types[ST_SkillData]()
        if skill.data.stSkillDataDefault.iParameterCount > 0:
            d.astParameters = [
                OPCUA_Types[ST_Parameter]()
                for _ in range(skill.data.stSkillDataDefault.iParameterCount)
            ]

        mapVar(skill.data.stSkillDataDefault, d)
        skill_node_handle.skill_DataDefault_node.write_value(
            d, ua.VariantType.ExtensionObject
        )
        # stSkillDataCommand, only if changed since last read_skill_data
        if (
            force
            or skill.data.stSkillDataCommand
            != skill_node_handle.stSkillDataCommand_marker
        ):
            d = OPCUA_Types[ST_SkillData]()
            if skill.data.stSkillDataDefault.iParameterCount > 0:
                d.astParameters = [
                    OPCUA_Types[ST_Parameter]()
                    for _ in range(skill.data.stSkillDataDefault.iParameterCount)
                ]
            mapVar(skill.data.stSkillDataCommand, d)
            skill_node_handle.skill_DataCommand_node.write_value(
                d, ua.VariantType.ExtensionObject
            )


def register_skill_type_to_asyncua_server(
    cls, server: Server, OPCUA_Types: dict, logger: logging.Logger = None
):
    """register skill types to asyncua ua module

    Args:
        server (Server): asyncua.sync.Server object
        OPCUA_Types (dict): dicitonary to keept opc ua type reference

    Raises:
        NotImplementedError: if register routine for sub type is not implemented
    """
    if logger:
        logger.info(f"Creating type: {cls.__name__ + OPCUA_TYPE_SUFFIX}")
    if hasattr(ua, cls.__name__ + OPCUA_TYPE_SUFFIX):
        return
    mem = {k: v for k, v in vars(cls).items() if not k.startswith("_")}
    if isinstance(cls, type):
        ann = cls.__dict__.get("__annotations__", None)
    else:
        ann = getattr(cls, "__annotations__", None)
    if ann:
        mem = ann

    fields = []
    for elem in mem:
        act_type = mem[elem]
        if isinstance(act_type(), ST_Base):
            register_skill_type_to_asyncua_server(
                act_type, server, OPCUA_Types, logger=logger
            )
            fields.append(
                uastr.new_struct_field(
                    elem, ua.NodeId(act_type.__name__ + OPCUA_TYPE_SUFFIX, 2)
                )
            )
        elif isinstance(
            act_type(), list
        ):  # Danger: All Lists are handled like ST_Parameter lists
            if hasattr(act_type, "__args__"):
                if isinstance(act_type.__args__[0](), ST_Base):
                    register_skill_type_to_asyncua_server(
                        act_type.__args__[0], server, OPCUA_Types, logger=logger
                    )
                    fields.append(
                        uastr.new_struct_field(
                            elem,
                            ua.NodeId(
                                act_type.__args__[0].__name__ + OPCUA_TYPE_SUFFIX, 2
                            ),
                            array=True,
                        )
                    )
        elif isinstance(act_type(), bool):
            fields.append(
                uastr.new_struct_field(elem, ua.VariantType.Boolean, array=False)
            )
        elif isinstance(act_type(), str):
            fields.append(
                uastr.new_struct_field(elem, ua.VariantType.String, array=False)
            )
        elif isinstance(act_type(), int) or isinstance(act_type(), enum.IntEnum):
            fields.append(
                uastr.new_struct_field(elem, ua.VariantType.Int32, array=False)
            )
        else:
            raise NotImplementedError("Structure not implemented!")

    new_struct(
        server,
        ua.NodeId(cls.__name__ + OPCUA_TYPE_SUFFIX, 2),
        cls.__name__ + OPCUA_TYPE_SUFFIX,
        fields=fields,
    )

    datatypes = server.load_data_type_definitions()
    OPCUA_Types[cls] = datatypes[cls.__name__ + OPCUA_TYPE_SUFFIX]
    if logger:
        logger.info(f"Registered {cls.__name__ + OPCUA_TYPE_SUFFIX} at opc ua server.")
