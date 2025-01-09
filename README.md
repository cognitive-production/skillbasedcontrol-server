<h1 style="text-align:center;">
<span style="color:#005B7F;">SkillBasedControl (SBC)</span> Server
</h1>

## Description
This python package includes all necessary classes for implementing skills in python and provide them via an opc ua server. It makes it possible to call python functions vie the skill interface based on the Module Type Package (MTP) service interface. It is developed and used by Fraunhofer Institute for Machine Tools and Forming Technology, department of IIOT-Controls and Technical Cybernetics to provide machine and robot functions to an skill orchestration system.

For detailed information on the Module Type Package (MTP), see:  
[VDI/VDE/NAMUR 2658 Blatt 4, Automation engineering of modular systems in the process industry - Modelling of module services](https://www.vdi.de/en/home/vdi-standards/details/vdivdenamur-2658-blatt-4-automation-engineering-of-modular-systems-in-the-process-industry-modelling-of-module-services)

## How to pip install
#### with existing python evnironment:
```
pip install git+https://github.com/cognitive-production/skillbasedcontrol-server
```
#### with new conda environment:
```
conda create -n sbc-server python=3.10
conda activate sbc-server
pip install git+https://github.com/cognitive-production/skillbasedcontrol-server
```

## How to use

#### Short:
1. Implement custom skill class inheriting from [BaseSkill](sbc_server/baseskill.py)
2. Create object of custom skill class
3. create skillserver object and inject custom skill objects
2. start skillserver using runskillserverhelper

see examples [custom_skill_implementations](examples/custom_skill_implementations.py) and [run_skillserver_opcua ](examples/run_skillserver_opcua.py).

#### Long:
To provide python functions via skill interfaces, you first have to implement new skill classes inheriting from the [BaseSkill](sbc_server/baseskill.py) class inside this package.
There are some base implementations located in [skillimplementations](sbc_server/skillimplementations.py). For more examples on how to implement custom skills see [custom_skill_implementations](examples/custom_skill_implementations.py).
After implementing the skills, they can be provided via an OPC UA server with the [SkillServer_OPCUA](sbc_server/skillserver_opcua.py) class. See the [run_skillserver_opcua](examples/run_skillserver_opcua.py) example for creating and running the server. For standalone execution of the server you can use the [runskillserverhelper](sbc_server/runskillserverhelper.py).


## Documentation
For class overview, see [classdiagram](docs/classdiagram.md).  


## Release Notes

### [1.0.2](https://github.com/cognitive-production/skillbasedcontrol-server/releases/tag/1.0.2) (2025-01-09)
#### [Changes to 1.0.0](https://github.com/cognitive-production/skillbasedcontrol-server/compare/1.0.0...1.0.2)
> fix "over-write bug" when skills run "too fast" in skillserver_opcua; implement PythonFunctionExecuteSkill


### Upgrade Steps
* see "How to pip install"

#### Breaking Changes
* None

#### New Features
* implement PythonFunctionExecuteSkill in skillimplementations

#### Bug Fixes
* fix over-write bug when skills run "too fast" in skillserver_opcua

#### Performance Improvements
* None

#### Other Changes
* extend example with custom python function and PythonFunctionExecuteSkill
* fix links in README
---
### [1.0.0](https://github.com/cognitive-production/skillbasedcontrol-server/releases/tag/1.0.0) (2024-12-04)
> Stable release on github.
---


## License
MIT License, see [LICENSE](LICENSE)