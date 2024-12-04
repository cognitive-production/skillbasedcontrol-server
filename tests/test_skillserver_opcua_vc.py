import time
from sbc_server.skillimplementations import ExternalExecuteSkill
from sbc_server.skillserver_opcua_vc import (
    SkillServer_OPCUA_VC,
)
from sbc_statemachine.skilldatahandle import SkillDataHandle, ST_Parameter


class TestSkill(ExternalExecuteSkill):
    def __init__(self, name: str = "SleepSkill"):
        data = SkillDataHandle()
        data.stSkillDataDefault.strName = name
        data.stSkillDataDefault.astParameters.append(
            ST_Parameter(strName="Count", strValue="1")
        )
        data.stSkillDataDefault.iParameterCount = 1
        super().__init__(data)


def test_skillserver_opcua_vc():
    skill_server_OPCUA_vsc = SkillServer_OPCUA_VC(
        [TestSkill(), TestSkill(name="TestSkill2")],
        port=4841,
    )
    skill_server_OPCUA_vsc.start()
    assert (
        list(skill_server_OPCUA_vsc.skillNodeHandles_vc.values())[0].skill_name
        == "SleepSkill"
    )
    assert (
        list(skill_server_OPCUA_vsc.skillNodeHandles_vc.values())[1].skill_name
        == "TestSkill2"
    )
    for skillNodeHandle_vsc in list(
        skill_server_OPCUA_vsc.skillNodeHandles_vc.values()
    ):
        assert skillNodeHandle_vsc.skill_node is not None
        assert skillNodeHandle_vsc.skill_statecomplete_node is not None
        assert skillNodeHandle_vsc.skill_eActiveState_node is not None
    # wait
    time.sleep(1.0)
    skill_server_OPCUA_vsc.stop()
