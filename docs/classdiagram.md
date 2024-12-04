```plantuml

class sbc_statemachine.SkillStateMachine{}
class sbc_server.BaseSkill{}
SkillStateMachine <|-- BaseSkill
class threading.Thread{}
class sbc_server.SkillRuntimeThread{}
Thread <|-- SkillRuntimeThread
SkillRuntimeThread o-- BaseSkill
class sbc_server.SkillServer{}
Thread <|-- SkillServer
SkillServer o-- SkillRuntimeThread
class asyncua.sync.Server{}
class sbc_server.SkillServerOPCUA{}
SkillServer <|-- SkillServerOPCUA
Server o-- SkillServerOPCUA
class sbc_server.SkillServerOPCUA_VC{}
SkillServerOPCUA <|-- SkillServerOPCUA_VC
entity sbc_server.runskillserverhelper


namespace USE {
    class CustomSkill
    note left: 1. Implement custom skill
    BaseSkill <|-- CustomSkill
    object custom_skill
    note left: 2. Create custom skill object
    CustomSkill --> custom_skill : instance
    object skill_server_opcua
    note left: 3. Create skill server object and inject skills\n4. call start() or use runskillserverhelper
    SkillServerOPCUA --> skill_server_opcua : instance
    custom_skill "*" --> skill_server_opcua : inject at init

}
```