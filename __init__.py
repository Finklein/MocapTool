bl_info = {
    "name": "MocapTool",
    "description": "Tool for retargeting etc.",
    "author": "Fink Sophie",
    "version": (0, 0, 3),
    "blender": (2, 82, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

##https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui initial UI setup source

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       Scene
                       )

from . import create_base_rig
from . import retarget
#from . import optimize_bone

# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):

##Properties to later define sliders to adjust the variables for the optimization
    alpha: FloatVectorProperty(
        name = "alpha",
        description="move bones closer to motion capture data",
        default=(0.0, 0.0, 0.0),
        min= 0.0, # float
        max = 10.0
        )

    beta: FloatProperty(
        name = "beta",
        description = "give the bones the same distance as the corresponding motion capture bones",
        default = 0.0,
        min = 0.00,
        max = 200.0
        )

    gamma: FloatProperty(
        name = "gamma",
        description = "keeps hands and feet from losing connection to the rig",
        default = 0.0,
        min = 0.00,
        max = 100.0
        )

    zeta: FloatProperty(
        name = "zeta",
        description = "makes sure that the rotation difference between mocap parent bone and rig parent bone isn't too large",
        default = 0.0,
        min = 0.00,
        max = 100.0
        )

##Properties for selecting the bones for optimization
    IK_bone_l: StringProperty(
        name="IK Bone L",
        description=":",
        default="",
        maxlen=1024,
        )

    IK_bone_r: StringProperty(
        name="IK Bone R",
        description=":",
        default="",
        maxlen=1024,
        )
##Properties for selecting the Mocap Data/BVH(1), FK-Rig(2), IK-Rig(3)
    rig_1: StringProperty(
        name="rig_1",
        description=":",
        default="",
        maxlen=1024,
        )

    rig_2: StringProperty(
        name="rig_2",
        description=":",
        default="",
        maxlen=1024,
        )

    rig_3: StringProperty(
        name="rig_3",
        description=":",
        default="",
        maxlen=1024,
        )


# https://blender.stackexchange.com/questions/130911/how-can-i-create-multiple-variables-in-a-propertygroup   shows how to loop to create multiple variables
# https://letsmake.games/projects/prototypes/posts/0012.bpy-stinks.html source for declaring a StringProperty for Prop search
##initializes StringProperties which can be later drawn as prop searches for selecting the corresponding bones to the mocap bones
class BoneMap(PropertyGroup):
    __annotations__ = {'map%d' % i: bpy.props.StringProperty(name="map%d" % i)
        for i in range(53)}

##initializes EnumProperties which are later used to draw dropdown menus for each bone in which the ik bones are selected
class check_ik_bone(PropertyGroup):
    __annotations__ = {'ik_bone%d' % i: bpy.props.EnumProperty(name="ik_bone%d" % i, description="choose which bone is which",
        items=[ ('OP1', "None", ""),
                ('OP2', "HandRight", ""),
                ('OP3', "HandLeft", ""),
                ('OP4', "FootRight", ""),
                ('OP5', "FootLeft", ""),
               ])
        for i in range(53)}


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------
##maps own bones to mocap bones if the name is the same
class AutomaticMapping(Operator):
    bl_label = "Automatic bone mapping"
    bl_idname = "wm.b_mapping"

    def execute(self, context):
        scene = bpy.context.scene
        mytool = scene.my_tool
        mbone = scene.map_bone

        i=0
        for bone in bpy.data.objects[mytool.rig_1].data.bones:
            if bone.name in bpy.data.objects[mytool.rig_2].data.bones:
                setattr(mbone, 'map'+str(i), bone.name)
            i+=1

        return {'FINISHED'}

##calls the function to create a basic FK Rig which can be used to retarget to
class CreateBaseRigFK(Operator):
    bl_label = "Create Base Rig FK"
    bl_idname = "wm.cbrf"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        create_base_rig.create_FK_Rig()
        print("Hello World")

        return {'FINISHED'}

##calls a function to copy the bone roll from the mocap rig to the own rig. The target is always the rig in the second slot
class COPYROLL(Operator):
    bl_label = "Copy bone roll from Mocap rig"
    bl_idname = "wm.copyroll"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        mbone = scene.map_bone
        ikBone = scene.ik_Bone

        i=0
        bMap = []
        ##the bones from the mocap rig will be accessed by their indeces because they can be called upon by numbers and they are in the right order anyway
        ##creates a list which is used to transfer which FK bone corresponds to which mocap bone and which bone is and IK-Bone
        for bone in bpy.data.objects[mytool.rig_1].data.bones:
            bMap.append((getattr(mbone, 'map'+str(i)), getattr(ikBone, 'ik_bone'+str(i))))
            i+=1

        create_base_rig.copy_roll(str(mytool.rig_1), str(mytool.rig_2), bMap)

        return {'FINISHED'}

##uses the rig in the second rig selection slot to built an IK-Rig
class CreateBaseRigIK(Operator):
    bl_label = "Create Base Rig IK"
    bl_idname = "wm.cbri"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        ##try, except block so there is no error when trying to built an IK-RIg with an empty FK slot
        try:
            create_base_rig.create_IK_Rig(str(mytool.rig_2))
        except:
            print("A FK-rig to build the ik rig upon needs to be selected.")

        return {'FINISHED'}

##retargets and transfers the retargeted animation directly from the FK to the IK-rig
class RETARGET(Operator):
    bl_label = "Retarget"
    bl_idname = "wm.retarget"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        mbone = scene.map_bone
        ikBone = scene.ik_Bone

        i=0
        bMap = []
        for bone in bpy.data.objects[mytool.rig_1].data.bones:
            bMap.append((getattr(mbone, 'map'+str(i)), getattr(ikBone, 'ik_bone'+str(i))))

            i+=1

        retarget.Retarget(str(mytool.rig_1), str(mytool.rig_2), bMap)

        retarget.TransferIk(str(mytool.rig_2), str(mytool.rig_3), bMap)

        return {'FINISHED'}

##calls the optimize function and optimizes the two selected bones for the current frame range
#class OPTIMIZE_BONES_ALL(Operator):
#    bl_label = "optimize bones all"
#    bl_idname = "wm.op_bones_all"

#    def execute(self, context):
#        scene = context.scene
#        mytool = scene.my_tool
#        mbone = scene.map_bone
#        bone_m_r = ''
#        bone_m_l = ''
#        i = 0
        ##gets the selected bones which are to be optimised
#        for bone in bpy.data.objects[mytool.rig_1].data.bones:
#            if getattr(mbone, 'map'+str(i))== getattr(mytool, 'IK_bone_r'):
#                bone_m_r = bone.name
#            elif getattr(mbone, 'map'+str(i))== getattr(mytool, 'IK_bone_l'):
#                bone_m_l = bone.name
#
#            i+=1

#        alpha_list = []
#        beta_list = []
#        gamma_list = []
#        zeta_list = []

#        for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end+1):
#            bpy.context.scene.frame_set(i)
#            alpha_list.append(mytool.alpha)
#            beta_list.append(mytool.beta)
#            gamma_list.append(mytool.gamma)
#            zeta_list.append(mytool.zeta)

#        optimize_bone.optimize_bones_all(str(mytool.rig_1),str(mytool.rig_3) ,str(mytool.rig_2), bone_m_r, bone_m_l, getattr(mytool, 'IK_bone_r'), getattr(mytool, 'IK_bone_l'), alpha_list, beta_list, gamma_list, zeta_list)

#        return {'FINISHED'}

##resets all the optimization for the whole framerange
#class OPTIMIZE_BONES_ALL_RESET(Operator):
#    bl_label = "reset bones all"
#    bl_idname = "wm.op_reset_all"

#    def execute(self, context):
#        scene = context.scene
#        mytool = scene.my_tool

#        for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end+1):
#            bpy.context.scene.frame_set(i)
#            optimize_bone.reset_optimizeBone(str(mytool.rig_2), str(mytool.rig_3), getattr(mytool, 'IK_bone_r'), getattr(mytool, 'IK_bone_l'), i)

#        return {'FINISHED'}

##optimizes the two bones for only the current frame and keys the result
#class OPTIMIZE_BONES_SINGLE(Operator):
#    bl_label = "optimize bones single"
#    bl_idname = "wm.op_bones_single"

#    def execute(self, context):
#        scene = context.scene
#        mytool = scene.my_tool
#        mbone = scene.map_bone
#        i=0
#        for bone in bpy.data.objects[mytool.rig_1].data.bones:
#            if getattr(mbone, 'map'+str(i))== getattr(mytool, 'IK_bone_r'):
#                bone_m_r = bone.name
#            elif getattr(mbone, 'map'+str(i))== getattr(mytool, 'IK_bone_l'):
#                bone_m_l = bone.name
#
#            i+=1

#        optimize_bone.optimizeBone(str(mytool.rig_1),str(mytool.rig_3), str(mytool.rig_2),bone_m_r, bone_m_l, getattr(mytool, 'IK_bone_r'), getattr(mytool, 'IK_bone_l'), mytool.alpha, mytool.beta, mytool.gamma, mytool.zeta, bpy.context.scene.frame_current)

#        print("single")

#        return {'FINISHED'}

##resets optimization for a single frame
#class OPTIMIZE_BONES_SINGLE_RESET(Operator):
#    bl_label = "reset bones single"
#    bl_idname = "wm.op_reset_single"

#    def execute(self, context):
#        scene = context.scene
#        mytool = scene.my_tool

#        optimize_bone.reset_optimizeBone(str(mytool.rig_2), str(mytool.rig_3), getattr(mytool, 'IK_bone_r'), getattr(mytool, 'IK_bone_l'), bpy.context.scene.frame_current)

#        print("single")

#        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel in Object Mode with nested panels
# ------------------------------------------------------------------------

class ObjPanel(Panel):
    bl_label = "MocapTransfer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MocapTool"
    bl_context = "objectmode"

class OBJECT_PT_Parent(ObjPanel):
    bl_label = "Parent"
    def draw(self, context):
        layout = self.layout

class OBJECT_PT_World1(ObjPanel):
    bl_parent_id = "OBJECT_PT_Parent"
    bl_label = "Select/Create Rigs"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.label(text = "Source Rig(BVH): ")
        ##prop_search allows user to search in scene for the object
        layout.prop_search(mytool, "rig_1", bpy.data, "objects", text ='')
        layout.label(text = "Goal Rig FK: ")
        layout.prop_search(mytool, "rig_2", bpy.data, "objects", text ='')
        layout.label(text = "Goal Rig IK: ")
        layout.prop_search(mytool, "rig_3", bpy.data, "objects", text ='')


        layout.operator("wm.cbrf")
        layout.operator("wm.copyroll")
        layout.operator("wm.cbri")
        layout.operator("wm.b_mapping")
        layout.operator("wm.retarget")


class OBJECT_PT_World2(ObjPanel):
    bl_parent_id = "OBJECT_PT_Parent"
    bl_label = "Bone Mapping"

    @classmethod
    def poll(self,context):
        obj = context.object
        return obj.type == 'ARMATURE' and context.active_object is not None and context.mode in {'EDIT_ARMATURE','POSE','OBJECT'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        mbone = scene.map_bone
        ikBone = scene.ik_Bone

##layout for Bone remapping heavily inspired by the Mocap Plugin from Benjy Cook #https://developer.blender.org/T28321 alternatively in the preinstalled addons from Blender 2.64 to 2.79
        MappingRow = layout.row(align=False)
        footCol = MappingRow.column(align=True)
        nameCol = MappingRow.column(align=True)
        nameCol.scale_x = 1.2
        mapCol = MappingRow.column(align=True)
        mapCol.scale_x = 1.5
        selectCol = MappingRow.column(align=True)
        twistCol = MappingRow.column(align=True)
        IKCol = MappingRow.column(align=True)
        IKCol.scale_x = 1.2
        IKLabel = MappingRow.column(align=True)
        IKLabel.scale_x = 0.2

##very important when the properties are in one class together bpy.context.scene becomes bpy.context.scene.my_tool as an example
        try:
            i=0
            ##draws all the slots to select the FK rig's corresponding bones to the mocap ones
            for bone in bpy.data.objects[mytool.rig_1].data.bones:
                nameCol.label(text = bone.name)
                k = "map%d" % i
                mapCol.prop_search(mbone, k, bpy.data.objects[mytool.rig_2].data, 'bones', text = '')
                m = 'ik_bone%d' % i
                IKCol.prop(ikBone, m, text = '')
                i+=1

        except BaseException as e:
            print("Works not", e)



class OBJECT_PT_World3(ObjPanel):
    bl_parent_id = "OBJECT_PT_Parent"
    bl_label = "Hand/Feet Optimization"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        try:
            layout.label(text = "Left IK Bone")
            layout.prop_search(mytool,'IK_bone_l', bpy.data.objects[mytool.rig_3].data, 'bones', text = '')
            layout.label(text = "Right IK Bone")
            layout.prop_search(mytool,'IK_bone_r', bpy.data.objects[mytool.rig_3].data, 'bones', text = '')
        except:
            print("Select IK Rig")


        layout.prop(mytool, "alpha", slider = True)
        layout.prop(mytool, "beta", slider = True)
        layout.prop(mytool, "gamma", slider = True)
        layout.prop(mytool, "zeta", slider = True)


        #layout.operator("wm.op_bones_all")
        #layout.operator("wm.op_reset_all")
        #layout.operator("wm.op_bones_single")
        #layout.operator("wm.op_reset_single")

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    BoneMap,
    check_ik_bone,
    AutomaticMapping,
    OBJECT_PT_Parent,
    OBJECT_PT_World1,
    OBJECT_PT_World2,
    OBJECT_PT_World3,
    CreateBaseRigFK,
    CreateBaseRigIK,
    COPYROLL,
    RETARGET,
#    OPTIMIZE_BONES_ALL,
#    OPTIMIZE_BONES_ALL_RESET,
#    OPTIMIZE_BONES_SINGLE,
#    OPTIMIZE_BONES_SINGLE_RESET
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

#here the variable for the PointerProperty is assigned like my_tool or map_bone. Those names are then used to assign properties in the layout to them.
#the type is the classname in which the properties were initialised
    Scene.map_bone = PointerProperty(type=BoneMap)
    Scene.my_tool = PointerProperty(type=MyProperties)
    Scene.ik_Bone = PointerProperty(type=check_ik_bone)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del Scene.map_bone
    del Scene.my_tool
    del Scene.ik_Bone

if __name__ == "__main__":
    register()
