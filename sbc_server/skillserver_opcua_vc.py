import dataclasses
from asyncua.sync import SyncNode, ua
from .skillserver_opcua import (
    SkillServer_OPCUA,
    Skill_Node_Handle,
)
from .baseskill import BaseSkill

VC_NODE_SUFFIX = "_vc"
VC_NODE_SKILL_COMPLETE = "complete"
VC_NODE_SKILL_STATE = "state"


@dataclasses.dataclass
class Skill_Node_Handle_VC:
    """dataclass for storing opc ua node handles for visual components access for each skill"""

    skill_name: str
    skill_node: SyncNode = None
    skill_statecomplete_node: SyncNode = None
    skill_eActiveState_node: SyncNode = None


class SkillServer_OPCUA_VC(SkillServer_OPCUA):
    """opc ua server providing and running skills with additional nodes for acces from Visual Components skill functionality"""

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
        self.skillNodeHandles_vc: dict[str, Skill_Node_Handle_VC] = {}
        for skill in skills:
            skill_name = skill.data.stSkillDataDefault.strName
            if skill_name in self.skillNodeHandles_vc:
                raise KeyError(f"Skill with name '{skill_name}' already registered!")
            self.skillNodeHandles_vc[skill_name] = Skill_Node_Handle_VC(
                skill_name=skill_name
            )
        return super()._init_skill_node_handles(skills=skills)

    def _addSkill(self, skill_name: str):
        """add skill nodes to opc ua server"""
        super()._addSkill(skill_name=skill_name)
        # add additional visual components skill nodes
        # vc skill node
        skill_node_vc = self.server.nodes.objects.add_folder(
            ua.NodeId(skill_name + VC_NODE_SUFFIX, self.namespaceIndex),
            skill_name + VC_NODE_SUFFIX,
        )
        self.skillNodeHandles_vc[skill_name].skill_node = skill_node_vc
        skill_node_vc.set_modelling_rule(True)
        # vc statecomplete node
        skill_statecomplete_node_vc = skill_node_vc.add_variable(
            ua.NodeId(
                skill_name + VC_NODE_SUFFIX + "." + VC_NODE_SKILL_COMPLETE,
                self.namespaceIndex,
            ),
            VC_NODE_SKILL_COMPLETE,
            False,
        )
        self.skillNodeHandles_vc[skill_name].skill_statecomplete_node = (
            skill_statecomplete_node_vc
        )
        skill_statecomplete_node_vc.set_writable(True)
        # vc skill state node
        skill_eActiveState_node_vc = skill_node_vc.add_variable(
            ua.NodeId(
                skill_name + VC_NODE_SUFFIX + "." + VC_NODE_SKILL_STATE,
                self.namespaceIndex,
            ),
            VC_NODE_SKILL_STATE,
            0,
        )
        self.skillNodeHandles_vc[skill_name].skill_eActiveState_node = (
            skill_eActiveState_node_vc
        )

    def read_skill_data(self, skill: BaseSkill) -> None:
        """read skill data from opc ua server

        Args:
            skill_name (str): name of skill
        """
        super().read_skill_data(skill=skill)
        # read additional vc nodes
        skill.data.stSkillCommand.StateComplete = self.skillNodeHandles_vc[
            skill.data.stSkillDataDefault.strName
        ].skill_statecomplete_node.read_value()

    def write_skill_data(self, skill: BaseSkill) -> None:
        """write skill data to opc ua server nodes

        Args:
            skill_name (str): name of skill
        """
        super().write_skill_data(skill=skill)
        # write additional vc nodes
        self.skillNodeHandles_vc[
            skill.data.stSkillDataDefault.strName
        ].skill_statecomplete_node.write_value(
            bool(skill.data.stSkillCommand.StateComplete)
        )
        self.skillNodeHandles_vc[
            skill.data.stSkillDataDefault.strName
        ].skill_eActiveState_node.write_value(int(skill.data.stSkillState.eActiveState))
