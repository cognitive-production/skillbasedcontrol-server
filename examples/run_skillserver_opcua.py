import logging
from custom_skill_implementations import *
from sbc_server.skillserver_opcua import SkillServer_OPCUA
from sbc_server.skillserver_opcua_vc import SkillServer_OPCUA_VC
from sbc_server.runskillserverhelper import run_skillserver


logger = logging.Logger("TestLogger", level=logging.INFO)
logger.addHandler(logging.StreamHandler())


def main():
    # 1. Implement custom skill class inheriting from BaseSkill
    # see custom_skill_implementations

    # 2. Create object of custom skill class
    skills = [
        AddSkill(logger=logger),
        GripperSkill(logger=logger),
        MovePosByJsonStringSkill(logger=logger),
        SleepSkill(logger=logger),
        NoParamSkill(logger=logger),
        MultiReturnSkill(logger=logger),
        MyJointSpaceSkill(logger=logger),
        CustomExternalExecuteSkill(logger=logger),
    ]

    # 3. create skillserver object and inject custom skill objects
    skill_server_OPCUA = SkillServer_OPCUA_VC(
        skills,
        skill_cycletime=0.1,
        server_cycletime=0.5,
        port=4841,
        logger=logger,
    )
    # 4. start skillserver, for example using run_skillserver from runskillserverhelper
    run_skillserver(skill_server_OPCUA)


if __name__ == "__main__":
    main()
