"""file for containing functions for face pose estimation"""
import cv2
import mediapipe as mp
import numpy as np

def face_pose_analysis(mp_face_mesh,cap,mp_drawing, mp_drawing_styles) -> None:
    """analysis for face pose estimation

    Args:
        mp_face_mesh (_type_): _description_
        cap (_type_): _description_
        mp_drawing (_type_): _description_
        mp_drawing_styles (_type_): _description_
    """
    # DETECT THE FACE LANDMARKS
    with mp_face_mesh.FaceMesh\
        (min_detection_confidence=0.7, min_tracking_confidence=0.7) as face_mesh:
        while True:
            success, image = cap.read()
            # Flip the image horizontally and convert the color space from BGR to RGB
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            # To improve performance
            image.flags.writeable = False
            # Detect the face landmarks
            results = face_mesh.process(image)
            # To improve performance
            image.flags.writeable = True
            # Convert back to the BGR color space
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            img_h, img_w, img_c = image.shape
            face_3d = []
            face_2d = []
            # Draw the face mesh annotations on the image.
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    for idx, lm in enumerate(face_landmarks.landmark):
                        if idx == 33 or idx == 263 or idx == 1 \
                            or idx == 61 or idx == 291 or idx == 199:
                            if idx ==1:
                                nose_2d = (lm.x * img_w, lm.y * img_h)
                                nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)
                            x_point, y_point = int(lm.x * img_w), int(lm.y * img_h)

                            #Get the 2d coordinates
                            face_2d.append([x_point,y_point])

                            #3d coordinates
                            face_3d.append([x_point,y_point, lm.z])
                    face_2d = np.array(face_2d, dtype=np.float64)
                    face_3d = np.array(face_3d, dtype=np.float64)

                    #The camera matrix
                    focal_length = 1 * img_w

                    cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                            [0, focal_length, img_w / 2],
                                            [0, 0, 1]])
                    dist_matrix = np.zeros((4,1), dtype=np.float64)
                    success, rot_vec, trans_vec = cv2.solvePnP\
                        (face_3d, face_2d, cam_matrix, dist_matrix)
                    rmat, jac = cv2.Rodrigues(rot_vec)
                    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                    x = angles[0] * 360
                    y = angles[1] * 360
                    z = angles[2] * 360

                    # if y < -10:
                    #     print('looking left')
                    # elif y > 10:
                    #     print('looking right')
                    # elif x < -10:
                    #     print('looking down')
                    # elif x > 10:
                    #     print('looking up')
                    # else:
                    #     print('looking forward')
                    nose_3d_projection, jacobian = cv2.projectPoints\
                        (nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

                    point_1 = (int(nose_2d[0]), int(nose_2d[1]))
                    point_2 = (int(nose_2d[0] + y * 10), int(nose_2d[1] - x * 10))
                    cv2.line(image, point_1, point_2, (255,0,0), 3)
                    mp_drawing.draw_landmarks(
                        image=image,
                        landmark_list=face_landmarks,
                        connections=mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_drawing_styles
                        .get_default_face_mesh_tesselation_style())

            # Display the image
            cv2.imshow('face pose estimation', image)
            # Terminate the process
            if cv2.waitKey(5) & 0xFF == 27:
                break
