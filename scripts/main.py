from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
from PIL import Image
import numpy as np
from configprovider import ConfigProvider
from webcam import Webcam
from markers import Markers
from constants import *
from objloader import *
import math
import time

class MarkersAR:
 
    # constants
    INVERSE_MATRIX = np.array([[ 1.0, 1.0, 1.0, 1.0],
                               [-1.0,-1.0,-1.0,-1.0],
                               [-1.0,-1.0,-1.0,-1.0],
                               [ 1.0, 1.0, 1.0, 1.0]])

    def __init__(self, debugOn):
        # initialise config
        self.config_provider = ConfigProvider()

        # initialise webcam
        self.webcam = Webcam()

        # initialize sound player
        pygame.mixer.init()

        # initialise markers
        self.markers = Markers(debugOn)
        print "Debug mode: {}".format(debugOn)
        self.markers_cache = None
        self.cache_counter = 0

        # initialise background texture
        self.texture_background = None

        # initialize face classifier
        self.faceCascade = cv2.CascadeClassifier("cascades/haarcascade_frontalface_default.xml")
        self.faceslist = None

        # initialize hands classifier
        self.okeyCascade = cv2.CascadeClassifier("cascades/haarcascade_okaygesture.xml")
        self.okeylist = None
        self.peaceCascade = cv2.CascadeClassifier("cascades/haarcascade_vickygesture.xml")
        self.peacelist = None

    def _init_gl(self):
        # setup OpenGL
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(33.7, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

        # load shapes
        self.arrow = OBJ('models/arrow/arrowC.obj')
        self.batman = OBJ('models/batman/batman1.obj')
        self.superman = OBJ('models/superman/superman0.obj')
        self.rockR = OBJ('models/rock/rockRR.obj')
        self.rockG = OBJ('models/rock/rockGG.obj')
        self.rockB = OBJ('models/rock/rockBB.obj')
        self.paperR = OBJ('models/paper/paperRR.obj')
        self.paperB = OBJ('models/paper/paperBB.obj')
        self.paperG = OBJ('models/paper/paperGG.obj')
        self.scissorsR = OBJ('models/scissors/scissorsRR.obj')
        self.scissorsG = OBJ('models/scissors/scissorsGG.obj')
        self.scissorsB = OBJ('models/scissors/scissorsBB.obj')

        # set sound names
        self.superman_sound = ["sounds/superman.mp3", 0]
        self.batman_sound = ["sounds/batman2.mp3", 0]
        self.rock_sound = ["sounds/rock.mp3", 0]
        self.paper_sound = ["sounds/paper.mp3", 0]
        self.scissors_sound = ["sounds/scissors.mp3", 0]
        self.tie_sound = ["sounds/tie.mp3", 0]
        self.max_time = 2.0

        # start webcam thread
        self.webcam.start()

        # assign texture
        glEnable(GL_TEXTURE_2D)
        self.texture_background = glGenTextures(1)

    def _draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # get image from webcam
        image = self.webcam.get_current_frame()

        # handle background
        self._handle_background(image.copy())

        # handle markers
        self._handle_markers(image.copy())

        glutSwapBuffers()

    def _handle_background(self, image):

        # recognize faces and draw square around
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.faceslist = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        bigface = 0
        bigfacedict = {}
        for i, (x, y, w, h) in enumerate(self.faceslist):
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green
            if (w*w + h*h) > bigface:
                bigface = w*w + h*h
                self.faceindex = i
            bigfacedict[i] = w + h
        x = sorted(bigfacedict.items(), key=lambda x: x[1], reverse=True)
        y = []
        for a, b in x:
            y.append(a)
        if len(x) > 0:
            self.faceindex = y
        else:
            self.faceindex = None

        # # recognize hands and draw square around (does not work great so we have commented it)
        # self.okeylist = self.okeyCascade.detectMultiScale(
        #     gray,
        #     scaleFactor=1.1,
        #     minNeighbors=9,
        #     minSize=(30, 30),
        #     flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        # )
        # for (x, y, w, h) in self.okeylist:
        #     cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  #Red
        #
        # self.peacelist = self.peaceCascade.detectMultiScale(
        #     gray,
        #     scaleFactor=1.1,
        #     minNeighbors=36,
        #     minSize=(30, 30),
        #     flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        # )
        # for (x, y, w, h) in self.peacelist:
        #     cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)  #Blue

        # convert image to OpenGL texture format
        bg_image = cv2.flip(image, 0)
        bg_image = Image.fromarray(bg_image)     
        ix = bg_image.size[0]
        iy = bg_image.size[1]
        bg_image = bg_image.tobytes('raw', 'BGRX', 0, -1)
 
        # create background texture
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)
        
        # draw background as a vertical plane far away from the camera
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-20.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-8.0, -6.0, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 8.0, -6.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 8.0,  6.0, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-8.0,  6.0, 0.0)
        glEnd( )
        glPopMatrix()

    def _handle_markers(self, image):

        # attempt to detect markers
        markers = []
        try:
            markers = self.markers.detect(image)
        except Exception as ex:
            print(ex)

        # manage markers cache
        if not markers:
            return

        # examine markers to determine if we are playing rock, paper, scissors
        markersRockPaperScissors = {}
        rockPaperScissors = [0, 0, 0]  # [rock, paper, scissors]
        for i, marker in enumerate(markers):
            marker_name = marker[3]
            if marker_name == ROCK or marker_name == PAPER or marker_name == SCISSORS:
                markersRockPaperScissors[i] = [marker_name, False]
                if marker_name == ROCK:  # Rock
                    rockPaperScissors[0] += 1
                elif marker_name == PAPER:  # Paper
                    rockPaperScissors[1] += 1
                else:  # Scissors
                    rockPaperScissors[2] += 1

        # determine results of the rock, paper, scissors game
        if len(markersRockPaperScissors) > 1:
            for pos in markersRockPaperScissors:
                marker_name = markersRockPaperScissors[pos][0]
                if marker_name == ROCK and rockPaperScissors[0] == 1 and rockPaperScissors[1] == 0 and rockPaperScissors[2] > 0:  # Rock
                    markersRockPaperScissors[pos][1] = True
                elif marker_name == PAPER and rockPaperScissors[0] > 0 and rockPaperScissors[1] == 1 and rockPaperScissors[2] == 0:  # Paper
                    markersRockPaperScissors[pos][1] = True
                elif marker_name == SCISSORS and rockPaperScissors[0] == 0 and rockPaperScissors[1] > 0 and rockPaperScissors[2] == 1:  # Scissors
                    markersRockPaperScissors[pos][1] = True

        # take care of every marker
        for i, marker in enumerate(markers):
            rvecs, tvecs, marker_rotation, marker_name, marker_coords = marker

            # correct rotation and translation to center figures in marker
            rvecs[2] -= (math.pi * marker_rotation / 2.0)
            if marker_rotation == 0:
                tvecs[0] += (0.6) * (math.cos(rvecs[2]) - math.sin(rvecs[2]))
                tvecs[1] += (0.6) * (math.cos(rvecs[2]) + math.sin(rvecs[2]))
            elif marker_rotation == 1:
                tvecs[0] -= (0.6) * (math.cos(rvecs[2]) - math.sin(-rvecs[2]))
                tvecs[1] += (0.6) * (math.cos(rvecs[2]) + math.sin(-rvecs[2]))
            elif marker_rotation == 2:
                tvecs[0] -= (0.6) * (math.cos(rvecs[2]) - math.sin(rvecs[2]))
                tvecs[1] -= (0.6) * (math.cos(rvecs[2]) + math.sin(rvecs[2]))
            else: # 3
                tvecs[0] += (0.6) * (math.cos(rvecs[2]) - math.sin(-rvecs[2]))
                tvecs[1] -= (0.6) * (math.cos(rvecs[2]) + math.sin(-rvecs[2]))

            # rotate to point with the arrow at the closer face
            if len(self.faceslist) > 0 and marker_name == ARROW:
                # center of the marker
                m_pos = [0.0, 0.0]
                for pos in marker_coords:
                    m_pos[0] += pos[0]
                    m_pos[1] += pos[1]
                m_pos[0] /= len(marker_coords)
                m_pos[1] /= len(marker_coords)
                # center of the face
                p_pos = [self.faceslist[self.faceindex[0]][0] + self.faceslist[self.faceindex[0]][2]/2.0,
                         self.faceslist[self.faceindex[0]][1] + self.faceslist[self.faceindex[0]][3]/2.0]
                # Setting the angle of the model
                rvecs[2] = math.atan2((p_pos[1] - m_pos[1]), (p_pos[0] - m_pos[0]))

            # build view matrix
            rmtx = cv2.Rodrigues(rvecs)[0]
            view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0]],
                                    [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1]],
                                    [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2]],
                                    [0.0       ,0.0       ,0.0       ,1.0    ]])
            view_matrix = view_matrix * self.INVERSE_MATRIX
            view_matrix = np.transpose(view_matrix)

            # load view matrix and draw cube
            glPushMatrix()
            glLoadMatrixd(view_matrix)

            # Draw markers and add sound to each marker
            if marker_name == ARROW:
                glCallList(self.arrow.gl_list)
            elif marker_name == BATMAN:
                glCallList(self.batman.gl_list)
                t = time.time()
                if t - self.batman_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.batman_sound[0])
                    pygame.mixer.music.play()
                self.batman_sound[1] = t
            elif marker_name == SUPERMAN:
                glCallList(self.superman.gl_list)
                t = time.time()
                if t - self.superman_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(self.superman_sound[0])
                    pygame.mixer.music.play()
                self.superman_sound[1] = t
            # Rock, Paper, Scissors game starts here, choose model depending on who wins or loses
            elif marker_name == PAPER:  # Paper
                if len(markersRockPaperScissors) > 1:
                    if markersRockPaperScissors[i][1]:
                        glCallList(self.paperG.gl_list)
                        t = time.time()
                        if t - self.paper_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load(self.paper_sound[0])
                            pygame.mixer.music.play()
                        self.paper_sound[1] = t
                    else:
                        glCallList(self.paperR.gl_list)
                else:
                    glCallList(self.paperB.gl_list)
            elif marker_name == SCISSORS:  # Scissors
                if len(markersRockPaperScissors) > 1:
                    if markersRockPaperScissors[i][1]:
                        glCallList(self.scissorsG.gl_list)
                        t = time.time()
                        if t - self.scissors_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load(self.scissors_sound[0])
                            pygame.mixer.music.play()
                        self.scissors_sound[1] = t
                    else:
                        glCallList(self.scissorsR.gl_list)
                else:
                    glCallList(self.scissorsB.gl_list)
            elif marker_name == ROCK:  # Rock
                if len(markersRockPaperScissors) > 1:
                    if markersRockPaperScissors[i][1]:
                        glCallList(self.rockG.gl_list)
                        t = time.time()
                        if t - self.rock_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                            pygame.mixer.music.load(self.rock_sound[0])
                            pygame.mixer.music.play()
                        self.rock_sound[1] = t
                    else:
                        glCallList(self.rockR.gl_list)
                else:
                    glCallList(self.rockB.gl_list)

            glColor3f(1.0, 1.0, 1.0)
            glPopMatrix()

        if len(markersRockPaperScissors) > 1:
            t = time.time()
            if t - self.tie_sound[1] > self.max_time and not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.tie_sound[0])
                pygame.mixer.music.play()
            self.tie_sound[1] = t



    def main(self):
        # setup and run OpenGL
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(100, 100)
        glutCreateWindow('Marker based AR')
        glutDisplayFunc(self._draw_scene)
        glutIdleFunc(self._draw_scene)
        self._init_gl()
        glutMainLoop()

if __name__ == "__main__":
    # run an instance of our AR class
    AR = MarkersAR(len(sys.argv) > 1)
    AR.main()
