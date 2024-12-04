import time
from sbc_server.baseskill import BaseSkill
from sbc_server.skillserver_opcua import (
    SkillServer_OPCUA,
    ST_Parameter,
)
from sbc_statemachine.skilldatahandle import SkillDataHandle


class TestSkill(BaseSkill):
    def __init__(self, name: str = "SleepSkill"):
        data = SkillDataHandle()
        data.stSkillDataDefault.strName = name
        data.stSkillDataDefault.astParameters.append(
            ST_Parameter(strName="Count", strValue="1")
        )
        data.stSkillDataDefault.iParameterCount = 1
        super().__init__(data)


def test_skillserver_opcua():
    skill_server_OPCUA = SkillServer_OPCUA(
        [TestSkill(), TestSkill(name="TestSkill2")],
        port=4841,
    )
    skill_server_OPCUA.start()
    assert (
        list(skill_server_OPCUA.skillNodeHandles.values())[0].skill_name == "SleepSkill"
    )
    assert (
        list(skill_server_OPCUA.skillNodeHandles.values())[1].skill_name == "TestSkill2"
    )
    for skillNodeHandle in list(skill_server_OPCUA.skillNodeHandles.values()):
        assert skillNodeHandle.skill_node is not None
        assert skillNodeHandle.skill_Command_node is not None
        assert skillNodeHandle.skill_State_node is not None
        assert skillNodeHandle.skill_DataDefault_node is not None
        assert skillNodeHandle.skill_DataCommand_node is not None
    # wait
    time.sleep(1.0)
    skill_server_OPCUA.stop()
