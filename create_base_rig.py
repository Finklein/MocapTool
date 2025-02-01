import bpy
from mathutils import Vector


##creates the FK Baserig which the user has to match to his character as an intermediate skeleton before binding his character to the IK rig
def create_FK_Rig ():

    #xsens rig bone names
    bone_names_xsens = ["Hips","Chest", "Chest2", "Chest3", "Chest4","Neck", "Head", "LeftCollar", "LeftShoulder",   "LeftElbow",  "LeftWrist","LeftHip", "LeftKnee",   "LeftAnkle", "LeftToe"]

    bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
    bpy.context.view_layer.objects.active.name = "BaseRig_FK"

    bpy.ops.object.editmode_toggle()

    #creates Bones for the rig and names them
    bpy.context.object.data.edit_bones["Bone"].name = "LeftToe"
    for i in range (14):
        bpy.ops.armature.bone_primitive_add(name = bone_names_xsens[i])

    #moving the bones to their default positions

    bpy.context.object.data.edit_bones["Hips"].head = Vector((0.0, 0.0, 3.61))
    bpy.context.object.data.edit_bones["Hips"].tail = Vector((0.0, 0.0, 3.75))

    bpy.context.object.data.edit_bones["Chest"].head = Vector((0.0, 0.0, 4.03))
    bpy.context.object.data.edit_bones["Chest"].tail = Vector((0.0, 0.0, 4.38))

    bpy.context.object.data.edit_bones["Chest2"].head = Vector((0.0, 0.0, 4.38))
    bpy.context.object.data.edit_bones["Chest2"].tail = Vector((0.0, 0.0, 4.71))

    bpy.context.object.data.edit_bones["Chest3"].head = Vector((0.0, 0.0, 4.71))
    bpy.context.object.data.edit_bones["Chest3"].tail = Vector((0.0, 0.0, 5.03))

    bpy.context.object.data.edit_bones["Chest4"].head = Vector((0.0, 0.0, 5.03))
    bpy.context.object.data.edit_bones["Chest4"].tail = Vector((0.0, 0.0, 5.36))

    bpy.context.object.data.edit_bones["Neck"].head = Vector((0.0, 0.0, 5.5))
    bpy.context.object.data.edit_bones["Neck"].tail = Vector((0.0, 0.0, 5.9))

    bpy.context.object.data.edit_bones["Head"].head = Vector((0.0, 0.0, 5.9))
    bpy.context.object.data.edit_bones["Head"].tail = Vector((0.0, 0.0, 6.71))

    bpy.context.object.data.edit_bones["LeftCollar"].head = Vector((0.11, 0.0, 5.29))
    bpy.context.object.data.edit_bones["LeftCollar"].tail = Vector((0.71, 0.0, 5.29))

    bpy.context.object.data.edit_bones["LeftShoulder"].head = Vector((0.71, 0.0, 5.29))
    bpy.context.object.data.edit_bones["LeftShoulder"].tail = Vector((1.78, 0.0, 5.29))

    bpy.context.object.data.edit_bones["LeftElbow"].head = Vector((1.78, 0.0, 5.29))
    bpy.context.object.data.edit_bones["LeftElbow"].tail = Vector((2.66, 0.0, 5.29))

    bpy.context.object.data.edit_bones["LeftWrist"].head = Vector((2.66, 0.0, 5.29))
    bpy.context.object.data.edit_bones["LeftWrist"].tail = Vector((3.33, 0.0, 5.29))

    bpy.context.object.data.edit_bones["LeftHip"].head = Vector((0.35, 0.0, 3.62))
    bpy.context.object.data.edit_bones["LeftHip"].tail = Vector((0.35, 0.0, 1.93))

    bpy.context.object.data.edit_bones["LeftKnee"].head = Vector((0.35, 0.0, 1.93))
    bpy.context.object.data.edit_bones["LeftKnee"].tail = Vector((0.35, 0.0, 0.33))

    bpy.context.object.data.edit_bones["LeftAnkle"].head = Vector((0.35, 0.0, 0.33))
    bpy.context.object.data.edit_bones["LeftAnkle"].tail = Vector((0.35, -0.67, 0.03))

    bpy.context.object.data.edit_bones["LeftToe"].head = Vector((0.35, -0.67, 0.03))
    bpy.context.object.data.edit_bones["LeftToe"].tail = Vector((0.35, -0.95, -0.02))

    #setting the bone's relations
    bpy.context.object.data.edit_bones["Chest"].parent = bpy.context.object.data.edit_bones["Hips"]

    bpy.context.object.data.edit_bones["Chest2"].parent = bpy.context.object.data.edit_bones["Chest"]
    bpy.context.object.data.edit_bones["Chest2"].use_connect = True

    bpy.context.object.data.edit_bones["Chest3"].parent = bpy.context.object.data.edit_bones["Chest2"]
    bpy.context.object.data.edit_bones["Chest3"].use_connect = True

    bpy.context.object.data.edit_bones["Chest4"].parent = bpy.context.object.data.edit_bones["Chest3"]
    bpy.context.object.data.edit_bones["Chest4"].use_connect = True

    bpy.context.object.data.edit_bones["Neck"].parent = bpy.context.object.data.edit_bones["Chest4"]

    bpy.context.object.data.edit_bones["Head"].parent = bpy.context.object.data.edit_bones["Neck"]
    bpy.context.object.data.edit_bones["Head"].use_connect = True

    bpy.context.object.data.edit_bones["LeftCollar"].parent = bpy.context.object.data.edit_bones["Chest4"]

    bpy.context.object.data.edit_bones["LeftShoulder"].parent = bpy.context.object.data.edit_bones["LeftCollar"]
    bpy.context.object.data.edit_bones["LeftShoulder"].use_connect = True

    bpy.context.object.data.edit_bones["LeftElbow"].parent = bpy.context.object.data.edit_bones["LeftShoulder"]
    bpy.context.object.data.edit_bones["LeftElbow"].use_connect = True

    bpy.context.object.data.edit_bones["LeftWrist"].parent = bpy.context.object.data.edit_bones["LeftElbow"]
    bpy.context.object.data.edit_bones["LeftWrist"].use_connect = True

    bpy.context.object.data.edit_bones["LeftHip"].parent = bpy.context.object.data.edit_bones["Hips"]

    bpy.context.object.data.edit_bones["LeftKnee"].parent = bpy.context.object.data.edit_bones["LeftHip"]
    bpy.context.object.data.edit_bones["LeftKnee"].use_connect = True

    bpy.context.object.data.edit_bones["LeftAnkle"].parent = bpy.context.object.data.edit_bones["LeftKnee"]
    bpy.context.object.data.edit_bones["LeftAnkle"].use_connect = True

    bpy.context.object.data.edit_bones["LeftToe"].parent = bpy.context.object.data.edit_bones["LeftAnkle"]
    bpy.context.object.data.edit_bones["LeftToe"].use_connect = True


    #mirrors the exxisting bones to the other side
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.armature.select_all(action='TOGGLE')

    bpy.ops.armature.symmetrize()


##creates an IK Rig from the FK rig to bind the users character to
def create_IK_Rig(fk_rig):
    #duplicate old rig https://blender.stackexchange.com/questions/135597/how-to-duplicate-an-object-in-2-8-via-the-python-api-without-using-bpy-ops-obje

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[fk_rig].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[fk_rig]
    bpy.ops.object.duplicate()
    bpy.context.view_layer.objects.active.name = "BaseRig_IK"

    riggi_fk = bpy.data.objects[fk_rig]
    riggi_ik = bpy.data.objects["BaseRig_IK"]

##still dependent that the FK-Rig has the same names as above
##gets the ik Bones
    p_leg_l = riggi_fk.pose.bones['LeftAnkle'].parent.name
    p_leg_r = riggi_fk.pose.bones['RightAnkle'].parent.name

    p_arm_l = riggi_fk.pose.bones['LeftWrist'].parent.name
    p_arm_r = riggi_fk.pose.bones['RightWrist'].parent.name
    #adds the missing pole vectors

    #create and move pole vectors to the right position
    bpy.ops.object.editmode_toggle()
    bpy.ops.armature.bone_primitive_add(name = 'pole_arm.L')
    bpy.context.object.data.edit_bones['pole_arm.L'].head = bpy.context.object.data.edit_bones[p_arm_l].head + Vector((0.0, 0.80, 0.00))
    bpy.context.object.data.edit_bones['pole_arm.L'].tail = bpy.context.object.data.edit_bones[p_arm_l].head + Vector((0.0, 1.40, 0.00))

    bpy.ops.armature.bone_primitive_add(name = 'pole_leg.L')
    bpy.context.object.data.edit_bones['pole_leg.L'].head = bpy.context.object.data.edit_bones[p_leg_l].head + Vector((0.0, -1.50, 0.00))
    bpy.context.object.data.edit_bones['pole_leg.L'].tail = bpy.context.object.data.edit_bones[p_leg_l].head + Vector((0.0, -2.50, 0.00))

    bpy.ops.armature.bone_primitive_add(name = 'pole_arm.R')
    bpy.context.object.data.edit_bones['pole_arm.R'].head = bpy.context.object.data.edit_bones[p_arm_r].head + Vector((0.0, 0.80, 0.00))
    bpy.context.object.data.edit_bones['pole_arm.R'].tail = bpy.context.object.data.edit_bones[p_arm_r].head + Vector((0.0, 1.40, 0.00))

    bpy.ops.armature.bone_primitive_add(name = 'pole_leg.R')
    bpy.context.object.data.edit_bones['pole_leg.R'].head = bpy.context.object.data.edit_bones[p_leg_r].head + Vector((0.0, -1.50, 0.00))
    bpy.context.object.data.edit_bones['pole_leg.R'].tail = bpy.context.object.data.edit_bones[p_leg_r].head + Vector((0.0, -2.50, 0.00))


    #delete parent so the IK Bones can move freely
    bpy.context.object.data.edit_bones["LeftAnkle"].parent = None
    bpy.context.object.data.edit_bones["RightAnkle"].parent = None
    bpy.context.object.data.edit_bones["LeftWrist"].parent = None
    bpy.context.object.data.edit_bones["RightWrist"].parent = None

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='POSE')

    ##add ik constraint to hand and feet
    l_arm_ik = riggi_ik.pose.bones[riggi_fk.pose.bones['LeftWrist'].parent.name]
    r_arm_ik = riggi_ik.pose.bones[riggi_fk.pose.bones['RightWrist'].parent.name]

    l_leg_ik = riggi_ik.pose.bones[riggi_fk.pose.bones['LeftAnkle'].parent.name]
    r_leg_ik = riggi_ik.pose.bones[riggi_fk.pose.bones['RightAnkle'].parent.name]

    l_arm_ik.constraints.new(type='IK')
    l_arm_ik.constraints["IK"].target = riggi_ik
    l_arm_ik.constraints["IK"].subtarget = "LeftWrist"
    l_arm_ik.constraints["IK"].pole_target = riggi_ik
    l_arm_ik.constraints["IK"].pole_subtarget = "pole_arm.L"
    l_arm_ik.constraints["IK"].chain_count = 2

    r_arm_ik.constraints.new(type='IK')
    r_arm_ik.constraints["IK"].target = riggi_ik
    r_arm_ik.constraints["IK"].subtarget = "RightWrist"
    r_arm_ik.constraints["IK"].pole_target = riggi_ik
    r_arm_ik.constraints["IK"].pole_subtarget = "pole_arm.R"
    r_arm_ik.constraints["IK"].chain_count = 2

    l_leg_ik.constraints.new(type='IK')
    l_leg_ik.constraints["IK"].target = riggi_ik
    l_leg_ik.constraints["IK"].subtarget = "LeftAnkle"
    l_leg_ik.constraints["IK"].pole_target = riggi_ik
    l_leg_ik.constraints["IK"].pole_subtarget = "pole_leg.L"
    l_leg_ik.constraints["IK"].chain_count = 2

    r_leg_ik.constraints.new(type='IK')
    r_leg_ik.constraints["IK"].target = riggi_ik
    r_leg_ik.constraints["IK"].subtarget = "RightAnkle"
    r_leg_ik.constraints["IK"].pole_target = riggi_ik
    r_leg_ik.constraints["IK"].pole_subtarget = "pole_leg.R"
    r_leg_ik.constraints["IK"].chain_count = 2

    bpy.ops.object.mode_set(mode='OBJECT')

#should copy over the bone roll so the bones rotate in the right direction while retargeting
#https://blenderartists.org/t/iterate-through-bones-of-armature/667942/2  shows how to iterate over edit bones
def copy_roll(mocap_rig, fk_rig, bmap):
    #list of the mocap rigs bone roll
    m_roll = []
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[mocap_rig].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[mocap_rig]
    bpy.ops.object.editmode_toggle()

#fills a list with the bone roll since aquiring this value is only possible in Edit mode which only one armature at a time can be actively in
    for i in bpy.data.armatures[mocap_rig].edit_bones:
        m_roll.append(i.roll)

    bpy.ops.object.editmode_toggle()

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[fk_rig].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[fk_rig]

    bpy.ops.object.editmode_toggle()
    ##change the bone roll of the target rig
    for i in range(len(m_roll)):
        if bmap[i][0] != "":
            bpy.context.object.data.edit_bones[bmap[i][0]].roll = m_roll[i]

    bpy.ops.object.editmode_toggle()
