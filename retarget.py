import bpy
import mathutils
from mathutils import Matrix, Vector
import math

##retargets the Motion Capture animation to the FK-Rig
def Retarget(so, ta, map):
##so = Mocap-Rig name, ta = FK-Rig name, map = list which was filled in __init__
    riggi = bpy.data.objects[so]
    riggi_fk = bpy.data.objects[ta]


    for i in range(bpy.context.scene.frame_start-1, bpy.context.scene.frame_end+1):
        bpy.context.scene.frame_set(i) ####sets the frame in the scene and updates scene as well
        if(bpy.context.scene.frame_current == bpy.context.scene.frame_start-1):
            bpy.context.scene.frame_set(0)
            ##zeros out the FK rig to calculate the differnence between the Mocap and FK hips location
            bpy.context.scene.frame_set(bpy.context.scene.frame_start-1)
            bpy.data.objects[ta].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[ta]
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='SELECT')
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.loc_clear()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            global_location_ik = riggi_fk.matrix_world @ riggi_fk.pose.bones[map[0][0]].matrix

            global_location = riggi.matrix_world @ riggi.pose.bones[0].matrix

            diff_hips_z = global_location[2][3] - global_location_ik[2][3]

            diff_hips_y = global_location[1][3] - global_location_ik[1][3]

            diff_hips_x = global_location[0][3] - global_location_ik[0][3]

        else:
            i=0
            ##iterate over the mocap rig bones
            for bone in bpy.data.objects[so].data.bones:
                ##check if the mocap bone has a corresponding FK bone
                if(map[i][0] != ''):
                    riggi_fk_bone = riggi_fk.pose.bones[map[i][0]]
                    riggi_bone = riggi.pose.bones[bone.name]
                    #calculate the mocap bone's transform in world coordinates
                    matrix_final = riggi.matrix_world @ riggi_bone.matrix

                    ##check if current bone in loop is root/hips to add the hip transformationto the retargeting
                    if bone.name == riggi.pose.bones[0].name:
                        matrix_final[2][3] -= diff_hips_z
                        matrix_final[1][3] -= diff_hips_y
                        matrix_final[0][3] -= diff_hips_x
                        #update scene to update matrix transformations since there result errors otherwise
                        bpy.context.view_layer.update()

                        riggi_fk_bone.matrix = riggi_fk.matrix_world.inverted() @ matrix_final
                    else:
                        bpy.context.view_layer.update()

                        ##transfer the mocap bone transformation to the FK-bone but then zero the translation since all bones in the FK-rigs are children
                        ##of the hips and shouldn't recieve translation values because of that
                        riggi_fk_bone.matrix = riggi_fk.matrix_world.inverted() @ matrix_final
                        bpy.context.view_layer.update()
                        riggi_fk_bone.location = Vector((0.0,0.0,0.0))

                i+=1



        #####keys all bones ###############
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[ta].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[ta]

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacterSelected')
        bpy.ops.object.mode_set(mode='OBJECT')


##transfers the animation from the FK-Rig to the IK-Rig
def TransferIk(so, ta, map):
    ##so sourcerig(FK), ta targetRig(IK)
    riggi = bpy.data.objects[so]
    riggi_ik = bpy.data.objects[ta]
    ##variables for the storing the ik-bones' names
    hand_r = ''
    hand_l = ''
    foot_r = ''
    foot_l = ''

    ##checking which bones are ik-bones
    for a in range(len(map)):
        if(map[a][1] == 'OP2'):
            hand_r = map[a][0]
        elif(map[a][1] == 'OP3'):
            hand_l = map[a][0]
        elif(map[a][1] == 'OP4'):
            foot_r = map[a][0]
        elif(map[a][1] == 'OP5'):
            foot_l = map[a][0]

    for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end+1):
        bpy.context.scene.frame_set(i)

        for bone in bpy.data.objects[so].data.bones:

            riggi_ik_bone = riggi_ik.pose.bones[bone.name]
            riggi_bone = riggi.pose.bones[bone.name]

            ##checking if bone is hips or an ik-bone because then the whole transform needs to be transferred
            if riggi_ik_bone.name in {map[0][0], hand_r, hand_l, foot_r, foot_l}:

                matrix_final = riggi.matrix_world @ riggi_bone.matrix

                riggi_ik_bone.matrix = riggi_ik.matrix_world.inverted() @ matrix_final

                bpy.context.view_layer.update()

            ##check if bone is foot or hand to adjust the pole vectors, it's currently still hard coded what the pole vectors are called there needs to be
            ##a possibility to select them during further developement
            if riggi_ik_bone.name in {riggi.pose.bones[hand_r].parent.name, riggi.pose.bones[hand_l].parent.name, riggi.pose.bones[foot_r].parent.name, riggi.pose.bones[foot_l].parent.name}:


                matrix_final = riggi.matrix_world @ riggi_bone.matrix
                if riggi_ik_bone.name == riggi.pose.bones[foot_r].parent.name:
                    x = 0
                    y = 0
                    z = 1.0

                    ##moves pole vector outward along the axis of the fk leg knee same for the others
                    trans_mat = mathutils.Matrix(((1,  0, 0, x),
                                              (0, 1, 0,  y),
                                              (0, 0, 1,  z),
                                            ( 0.0000,  0.0000,  0.0000,  1.0000)))
                    riggi_ik.pose.bones['pole_leg.R'].matrix = riggi_ik.matrix_world.inverted() @ matrix_final
                    bpy.context.view_layer.update()
                    riggi_ik.pose.bones['pole_leg.R'].matrix = riggi_ik.pose.bones['pole_leg.R'].matrix @ trans_mat


                if riggi_ik_bone.name == riggi.pose.bones[foot_l].parent.name:
                    x = 0
                    y = 0
                    z = 1.0

                    trans_mat = mathutils.Matrix(((1,  0, 0, x),
                                              (0, 1, 0,  y),
                                              (0, 0, 1,  z),
                                            ( 0.0000,  0.0000,  0.0000,  1.0000)))

                    riggi_ik.pose.bones['pole_leg.L'].matrix = riggi_ik.matrix_world.inverted() @ matrix_final
                    bpy.context.view_layer.update()
                    riggi_ik.pose.bones['pole_leg.L'].matrix = riggi_ik.pose.bones['pole_leg.L'].matrix @ trans_mat


                if riggi_ik_bone.name == riggi.pose.bones[hand_r].parent.name:
                    x = 0
                    y = -1.0
                    z = 0

                    trans_mat = mathutils.Matrix(((1,  0, 0, x),
                                              (0, 1, 0,  y),
                                              (0, 0, 1,  z),
                                            ( 0.0000,  0.0000,  0.0000,  1.0000)))

                    riggi_ik.pose.bones['pole_arm.R'].matrix = riggi_ik.matrix_world.inverted() @ matrix_final
                    bpy.context.view_layer.update()
                    riggi_ik.pose.bones['pole_arm.R'].matrix = riggi_ik.pose.bones['pole_arm.R'].matrix @ trans_mat


                if riggi_ik_bone.name == riggi.pose.bones[hand_l].parent.name:
                    x = 0
                    y = -1.0
                    z = 0

                    trans_mat = mathutils.Matrix(((1,  0, 0, x),
                                              (0, 1, 0,  y),
                                              (0, 0, 1,  z),
                                            ( 0.0000,  0.0000,  0.0000,  1.0000)))

                    riggi_ik.pose.bones['pole_arm.L'].matrix = riggi_ik.matrix_world.inverted() @ matrix_final
                    bpy.context.view_layer.update()
                    riggi_ik.pose.bones['pole_arm.L'].matrix = riggi_ik.pose.bones['pole_arm.L'].matrix @ trans_mat



            ##transfers the rotation the same way as in the Retarget method
            if riggi_ik_bone.name not in {map[0][0], hand_r, hand_l, foot_r, foot_l,
                riggi.pose.bones[hand_r].parent.name, riggi.pose.bones[hand_l].parent.name, riggi.pose.bones[foot_r].parent.name, riggi.pose.bones[foot_l].parent.name,
                riggi.pose.bones[riggi.pose.bones[hand_r].parent.name].parent.name, riggi.pose.bones[riggi.pose.bones[hand_l].parent.name].parent.name,
                riggi.pose.bones[riggi.pose.bones[foot_r].parent.name].parent.name, riggi.pose.bones[riggi.pose.bones[foot_l].parent.name].parent.name}:

                matrix_final = riggi.matrix_world @ riggi_bone.matrix

                bpy.context.view_layer.update()

                riggi_ik_bone.matrix =  riggi_ik.matrix_world.inverted() @ matrix_final

                riggi_ik_bone.location = Vector((0.0, 0.0, 0.0))


        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[ta].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[ta]
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.anim.keyframe_insert_menu(type='WholeCharacterSelected')
        bpy.ops.object.mode_set(mode='OBJECT')
