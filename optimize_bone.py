import bpy
import mathutils
from mathutils import Matrix, Vector
import math
import numpy as np
import scipy.optimize

def optimizeBone(so, ik, fk, bone_m_r, bone_m_l, bone_r, bone_l, alpha, beta, gamma, zeta, cframe):
##so source = mocap data
    riggi_mocap = bpy.data.objects[so]
    riggi_ik = bpy.data.objects[ik]
    riggi_fk = bpy.data.objects[fk]

    def sqr (x):
        return x*x

    def sqrdot (x):
        return np.dot(x,x)

    ###split the x to be used for the optimization since it contains the left and right bone's Vector
    def IK_linker_bone(x):
        return Vector(x[0:3])

    def IK_rechter_bone(x):
        return Vector(x[3:6])

    ###extracts the location form the bone matrix
    def getColumn(matrix, row = 3):
        v = Vector((1.0,1.0,1.0))
        for i in range (len(matrix)-1):
            v[i] = matrix[i][row]
        return v

    ##puts the left and right bone's location vector in one Vector
    def convloc(x,y):
        val = np.empty((6,))
        for i in range(3):
            val[i] = x[i]
            val[i+3] = y[i]
        return val

    ##computes the difference between to angles
    def angle_difference(a,b):
        d = (a-b) % (2.0 * np.pi)
        if (d > np.pi):
            d -= 2.0 * np.pi
        return d

    ##computes all three angle differences x,y,z
    def euler_difference(a,b):
        return np.sqrt(sqr(angle_difference(a.x,b.x)  ) \
                  + sqr(angle_difference(a.y,b.y)  ) \
                  + sqr(angle_difference(a.z,b.z)  ) )

    ################not in use currently #########################################################################################
    #quaternion to matrix trace comparison
    def rotation_difference_trace(a,b):
        # http://www.boris-belousov.net/2016/12/01/quat-dist/
        a_m = a.to_quaternion().to_matrix()
        print("a_m:",a_m)
        b_m = b.to_quaternion().to_matrix()
        b_m.transpose()
        print("b_m:",b_m)
        #b_inv = b.transposed()
        #print("b_inv:",b_inv)
        m_i = a_m @ b_m
        print(m_i)
        # identity matrix has trace = 3 if it's different the matrices aren't the same
        trace = m_i[0][0] + m_i[1][1] + m_i[2][2]
        return sqr(3-trace)

    #elbow moves toward mocapdata
    def rotation_difference_elbow_moves_to_og(a,b):
        # http://www.boris-belousov.net/2016/12/01/quat-dist/
        a_m = a.to_quaternion().to_matrix()
        print("a_m:",a_m)
        b_m = b.to_quaternion().to_matrix()
        #b_m.transpose()
        print("b_m:",b_m)
        trace_a = a_m[0][0] + a_m[1][1] + a_m[2][2]
        trace_b = b_m[0][0] + b_m[1][1] + b_m[2][2]
        #b_inv = b.transposed()
        print("trace_a:",trace_a)
        print("trace_b:",trace_b)
        #m_i = a_m @ b_m
        #print(m_i)
        # identity matrix has trace = 3 if it's different the matrices aren't the same
        #trace = m_i[0][0] + m_i[1][1] + m_i[2][2]
        return sqr(trace_b -trace_a)

    def rotation_difference(a,b):
        # http://www.boris-belousov.net/2016/12/01/quat-dist/
        a_m = a.to_quaternion().to_matrix()
        print("a_m:",a_m)
        b_m = b.to_quaternion().to_matrix()
        #b_m.transpose()
        print("b_m:",b_m)
        trace_a = a_m[0][0] + a_m[1][1] + a_m[2][2]
        trace_b = b_m[0][0] + b_m[1][1] + b_m[2][2]
        angle_a = np.arccos(0.5 * (trace_a - 1))
        angle_b = np.arccos(0.5 * (trace_b - 1))
        #b_inv = b.transposed()
        print("trace_a:",trace_a)
        print("trace_b:",trace_b)
        print("angle_a:",angle_a)
        print("angle_b:",angle_b)

        #m_i = a_m @ b_m
        #print(m_i)
        # identity matrix has trace = 3 if it's different the matrices aren't the same
        #trace = m_i[0][0] + m_i[1][1] + m_i[2][2]
        return sqr(angle_a-angle_b)

    def compareMatrices(bone_ik_r, bone_ik_l, bone_m_r, bone_m_l):
        m_ik_r = riggi_ik.pose.bones[bone_ik_r].matrix
        m_ik_l = riggi_ik.pose.bones[bone_ik_l].matrix

        m_m_r = riggi_mocap.pose.bones[bone_m_r].matrix
        m_m_l = riggi_mocap.pose.bones[bone_m_l].matrix

    #######################not in use currently########################################################################################################

    ##function to be minimized
    def evaluation( b_ol, b_or, alpha, beta, gamma, zeta, bone_l, bone_r, bone_ik_l_p, bone_ik_r_p, o_r_bow_rot, o_l_bow_rot, b_fk_l, b_fk_r ):
        def f(x):
            b_pl = IK_linker_bone(x)
            b_pr = IK_rechter_bone(x)

            ##gives the bones which are contained in bone_l, bone_r the new position to test
            matrix_final = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_l].matrix
            matrix_final[0][3]= b_pl[0]
            matrix_final[1][3]= b_pl[1]
            matrix_final[2][3]= b_pl[2]
            riggi_ik.pose.bones[bone_l].matrix = riggi_ik.matrix_world.inverted() @ matrix_final

            matrix_final = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_r].matrix
            matrix_final[0][3]= b_pr[0]
            matrix_final[1][3]= b_pr[1]
            matrix_final[2][3]= b_pr[2]
            riggi_ik.pose.bones[bone_r].matrix = riggi_ik.matrix_world.inverted() @ matrix_final

            bpy.context.view_layer.update()

            ##gives b_pl and b_pr the world coordinate poition of bone_l and bone_r
            matrix_lf = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_l].matrix
            b_pl = Vector((matrix_lf[0][3], matrix_lf[1][3], matrix_lf[2][3] ))

            matrix_rf = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_r].matrix
            b_pr = Vector((matrix_rf[0][3], matrix_rf[1][3], matrix_rf[2][3] ))

            ##gets the rotation from the bone above the ik bone
            bow_l = riggi_ik.pose.bones[bone_ik_l_p].matrix.to_euler()
            bow_r = riggi_ik.pose.bones[bone_ik_r_p].matrix.to_euler()

            #compareMatrices(bone_ik_r_p, bone_ik_l_p, riggi_mocap.pose.bones[bone_m_r].parent.name, riggi_mocap.pose.bones[bone_m_l].parent.name)

            return sqrdot(np.multiply(alpha, (b_ol - b_pl))) + sqrdot(np.multiply(alpha, (b_or - b_pr))) \
                    + sqrdot(np.multiply(np.subtract(Vector((10.0,10.0,10.0)),alpha), (b_fk_l - b_pl))) + sqrdot(np.multiply(np.subtract(Vector((10.0,10.0,10.0)),alpha), (b_fk_r - b_pr))) \
                   +  beta* sqr((b_or - b_ol).length - (b_pr - b_pl).length) \
                   + gamma* (sqrdot(riggi_ik.pose.bones[bone_l].head - riggi_ik.pose.bones[bone_ik_l_p].tail) \
                    + sqrdot(riggi_ik.pose.bones[bone_r].head - riggi_ik.pose.bones[bone_ik_r_p].tail)) \
                    + zeta * (euler_difference(o_r_bow_rot,bow_r) + euler_difference(o_l_bow_rot,bow_l))

        return f

    #motion capture bone matrix in world coordinates
    b_ol = riggi_mocap.matrix_world @ riggi_mocap.pose.bones[bone_m_l].matrix

    b_or = riggi_mocap.matrix_world @ riggi_mocap.pose.bones[bone_m_r].matrix

    #IK-rig bone matrix in world coordinates
    b_ik_l = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_l].matrix

    b_ik_r = riggi_ik.matrix_world @ riggi_ik.pose.bones[bone_r].matrix

    #FK-rig bone matrix in world coordinates
    b_fk_l = riggi_fk.matrix_world @ riggi_fk.pose.bones[bone_l].matrix

    b_fk_r = riggi_fk.matrix_world @ riggi_fk.pose.bones[bone_r].matrix


    #motion capture rig's IK bone's parent's rotation
    l_o_elbow = riggi_mocap.pose.bones[riggi_mocap.pose.bones[bone_m_l].parent.name].matrix.to_euler()

    r_o_elbow = riggi_mocap.pose.bones[riggi_mocap.pose.bones[bone_m_r].parent.name].matrix.to_euler()

    #IK-Rig IK bone's parent
    bone_ik_l_p = riggi_fk.pose.bones[bone_l].parent.name

    bone_ik_r_p = riggi_fk.pose.bones[bone_r].parent.name


    x0 = np.array(convloc(getColumn(b_ik_l), getColumn(b_ik_r)))

    op = scipy.optimize.minimize(evaluation(b_ol = getColumn(b_ol), b_or = getColumn(b_or), alpha = alpha, beta = beta, gamma = gamma,zeta =  zeta, bone_l = bone_l, bone_r = bone_r,
                                            bone_ik_l_p = bone_ik_l_p ,bone_ik_r_p = bone_ik_r_p, o_r_bow_rot = r_o_elbow,o_l_bow_rot = l_o_elbow, b_fk_l = getColumn(b_fk_l), b_fk_r = getColumn(b_fk_r)), x0, method = 'Nelder-Mead', tol=1e-6, options =  {'maxiter':10000})

    riggi_ik.pose.bones[bone_r].keyframe_insert(data_path = "location", frame = cframe)
    riggi_ik.pose.bones[bone_l].keyframe_insert(data_path = "location", frame = cframe)

##doing the loop in __init__ doesn't bear the same result as doing the loop in this script
##needs lists which contain all variable values over time
def optimize_bones_all(so, ik, fk, bone_m_r, bone_m_l, bone_r, bone_l, alpha, beta, gamma, zeta):
    m = 0
    for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end+1):
        bpy.context.scene.frame_set(i)
        print(beta[m])
        optimizeBone(so, ik, fk, bone_m_r, bone_m_l, bone_r, bone_l, alpha[m], beta[m], gamma[m], zeta[m], i)
        m+=1

##gets the original retarget animation from the FK-rig and transfers that animation to the IK-Rig again
def reset_optimizeBone(so, ta, bone_r, bone_l, cframe):
    riggi_fk = bpy.data.objects[so]
    riggi_ik = bpy.data.objects[ta]

    riggi_fk_bone_l = riggi_fk.pose.bones[bone_l]
    riggi_fk_bone_r = riggi_fk.pose.bones[bone_r]

    riggi_ik_bone_l = riggi_ik.pose.bones[bone_l]
    riggi_ik_bone_r = riggi_ik.pose.bones[bone_r]

    matrix_final_l = riggi_fk.matrix_world @ riggi_fk_bone_l.matrix
    matrix_final_r = riggi_fk.matrix_world @ riggi_fk_bone_r.matrix

    riggi_ik_bone_l.matrix = riggi_ik.matrix_world.inverted() @ matrix_final_l
    riggi_ik_bone_r.matrix = riggi_ik.matrix_world.inverted() @ matrix_final_r

    bpy.context.view_layer.update()

    riggi_ik.pose.bones[bone_l].keyframe_insert(data_path = "location", frame = cframe)
    riggi_ik.pose.bones[bone_r].keyframe_insert(data_path = "location", frame = cframe)
