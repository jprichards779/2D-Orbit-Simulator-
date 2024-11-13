import pygame
from pygame.locals import*
import random
from mass import*
from Newtonian_Grav import*
import helper_functions


class Main:         
    # _______________________________________Physical Constants                  
    AU, G = 1.496*10**11, 6.67430*10**-11    # Average distance between Sun and Earth # Newton's Gravitational Constant                                       
    
    # _______________________________________ Program constants
    SCREEN_SCALE = 3                         # Number of AU either side of screen center / origin
    DOT_SCALE = 1                            # Magnitude of size variation between dots representing objects       
    TIME_LAPSE = 1                           # Rate of evolution| 0 - 1 = 0 to 100% of hardcoded evolution rate         
    SPACE_COLOUR = (0,0,10)  
    assert SCREEN_SCALE > 0               
    assert DOT_SCALE < 5 and DOT_SCALE >=1
    assert TIME_LAPSE >= 0 and TIME_LAPSE <=1

    # _______________________________________ Solar System Input                                                          
    v_Earth = 29789                          # Velocity calculated assuming circular motion at average distance
    v_Merc = 29789*(1/0.378)**0.5           
    v_Ven = 29789*(1/0.72)**0.5             
    v_Mar = 29789*(1/1.5)**0.5
    v_Jup = 29789*(1/5.2)**0.5
    v_Sat = 29789*(1/9.5)**0.5
    v_Ura = 29789*(1/19)**0.5
    v_Nep = 29789*(1/30)**0.5
    Mass.distance_unit = SCREEN_SCALE*AU     
    Mass.scale *= DOT_SCALE 
    SOLAR_SYSTEM = [Mass(m=1.989*10**30, s=[0,0],       v=[0,0],      colour=(255,255,250), avg_density=1408),
                    Mass(m=3.285*10**23, s=[0.378*AU,0],v=[0,v_Merc], colour=(200,180,0),   avg_density=5429),
                    Mass(m=4.867*10**24, s=[0.72*AU,0], v=[0,v_Ven],  colour=(200,180,0),   avg_density=5243),
                    Mass(m=5.972*10**24, s=[AU,0],      v=[0,v_Earth],colour=(80,180,255),  avg_density=5514),
                    Mass(m=6.39*10**23,  s=[1.5*AU,0],  v=[0,v_Mar],  colour=(200,100,50),  avg_density=3934),
                    Mass(m=1.898*10**27, s=[-5.2*AU,0], v=[0,-v_Jup], colour=(200,150,100), avg_density=1326),
                    Mass(m=5.972*10**24, s=[9.5*AU,0],  v=[0,v_Sat],  colour=(150,150,70),  avg_density=687),
                    Mass(m=8.681*10**25, s=[19*AU,0],   v=[0,v_Ura], colour=(0,100,150),   avg_density=1270),
                    Mass(m=1.024*10**26, s=[30*AU,0],  v=[0,-v_Nep], colour=(0,100,255),   avg_density=1638),]
    #               Note that velocity vectors are perpendicular to dispalcement (from center of mass) vectors
    
    # ____________________________Initialising the class so we can instantiate it

    def __init__(self):  
        pygame.init()
        self.screen_width, self.screen_height = 700, 700 
        self.size = (self.screen_width, self.screen_height) 
        self.screen = pygame.display.set_mode(self.size)
        self.lines = pygame.Surface(self.size)   
        icon = pygame.image.load("Red Dwarf.png")
        pygame.display.set_icon(icon)
        self.run = True
        self.initialise_data_structures(input=self.SOLAR_SYSTEM, center_object_ID=None)  
        # self.initialise_data_structures()
        # self.initialise_data_structures(input=self.SOLAR_SYSTEM, center_object_ID=3)
        #  
    def initialise_data_structures(self, input=[], center_object_ID=None):
        self.countdown = 0
        self.started = False
        self.drawing = False 
        self.text_x, self.text_y = self.screen_width, self.screen_height/2
        self.input = input
        self.center_object_ID = center_object_ID
        if len(self.input) == 0: self.center_object_ID = None 
        self.time_elapsed, self.recent_event_log, self.recent_event_times = 0, [], []
        self.mouse_history = []  

    # ______________________________________ Consmetics  
    # Customising Caption
    def caption(self, years=False):
        title = "||RED DWARF||"
        title += " "*50
        if years and self.started: title += f"| Time: {round(self.time_elapsed/(365*24*3600),1)} calendar years |"
        pygame.display.set_caption(title)

    #   Ensuring time updates correctly having retrofitted a screen 
    #   message in draw() method below
    def update_displayed_info(self):
        if self.drawing and not self.started: 
            self.time_elapsed = 0
            self.started = True

    #   Displaying messages and objects on screen
    def draw(self, Model_System):
        zoom_out = (1/(Mass.distance_unit)) 
        lines = pygame.Surface(self.size) 
        lines.fill(self.SPACE_COLOUR)
        points, radii, colours = [],[],[]
        if not self.drawing:
            font1 = pygame.font.SysFont("Arial", 36)
            font2 = pygame.font.SysFont("Cambria", 25)
            text1 = "WHEN THE SCREEN CLEARS . . ."
            text2 = ". . . click on / touch the screen to create new masses."
            coordinates1 = (self.text_x/5, self.text_y -25)
            coordinates2 = (self.text_x/10, self.text_y+25)
            text_surface1 = font1.render(text1, True, (255,0,0))
            text_surface2 = font2.render(text2, False, (30,100,255))
            self.screen.blit(text_surface1,coordinates1)
            self.screen.blit(text_surface2,coordinates2)
        else:
            center = self.frame_of_reference(Model_System)
            for n in Model_System.current_system:
                assert type(n) == Mass
                screen_coordinates = helper_functions.pygame_array([zoom_out*(n.s[0]-center[0])],
                                                [zoom_out*(n.s[1]-center[1])], 
                                                self.screen_width, self.screen_height)[0]
                points.append(screen_coordinates)
                n.screen_points = points
                radii.append(n.dot_diameter)
                colours.append(n.colour)
            for n in range(len(points)):
                pygame.draw.circle(lines,colours[n], points[n], radii[n])
            self.screen.blit(lines, (0, 0))

    # __________________________________ Technical / User interaction
    # Total time elapsed 
    def clock_tick(self, Model):
        self.time_elapsed+=Model.dT

    # Allowing screen/viewer to follow an object
    def frame_of_reference(self, Model_System):
        if self.center_object_ID is not None and len(self.input)>0:
            if len(Model_System.new_ids) > 0:
                index = Model_System.new_ids.index(self.center_object_ID)
                center = Model_System.current_system[index].s
            else: 
                center = self.input[self.center_object_ID].s
        else: center=[0,0]
        return center
    
    # Adding masses to the simulation
    def event_loop(self, Model_System, mass_range=[10**27, 10**30]):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                    self.run = False
            if len(self.recent_event_log) >=2:
                self.recent_event_log = []
                self.recent_event_times=[]
            if event.type == MOUSEBUTTONDOWN:
                initial = pygame.mouse.get_pos()
                self.mouse_history.append(initial)
                self.recent_event_log.append(initial)
                self.recent_event_times.append(self.time_elapsed) 
            elif event.type == MOUSEBUTTONUP:
                final = pygame.mouse.get_pos()
                self.recent_event_log.append(final)
                self.recent_event_times.append(self.time_elapsed)
            # Analysis of gathered data an object creation
            if len(self.recent_event_log) == 2 and self.drawing:
                event_count = self.mouse_history.count(self.recent_event_log[0])
                if self.recent_event_log[0] in self.mouse_history and event_count == 1:
                    t0, t1 = self.recent_event_times[0], self.recent_event_times[1]
                    pts1, pts2 = self.recent_event_log[0], self.recent_event_log[-1]
                    s0 = helper_functions.translate_points_on_screen(pts=pts1, WIDTH=self.screen_width, 
                                                HEIGHT=self.screen_height, screen_scale=Mass.distance_unit)
                    s1 = helper_functions.translate_points_on_screen(pts=pts2, WIDTH=self.screen_width, 
                                                HEIGHT=self.screen_height, screen_scale=Mass.distance_unit)
                    # Adjusting position and velocity with respect to an object's frame of refernce
                    v_x_adjust, v_y_adjust = None,None
                    if self.center_object_ID is not None:
                        for n in Model_System.current_system:
                            if n.ID == self.center_object_ID:
                                s0[0], s0[1] = s0[0]+n.s[0], s0[1]+n.s[1]
                                s1[0], s1[1] = s1[0]+n.s[0], s1[1]+n.s[1]
                                v_x_adjust, v_y_adjust = n.v[0], n.v[1]
                    ds_x, ds_y = s1[0]-s0[0], s1[1]-s0[1]
                    dt = abs(t1-t0)
                    if dt > 1000: # Must be greater than zero...larger number will reduce velocity magnitude
                        [min_mass, max_mass] = mass_range
                        if len(self.mouse_history) > 20: self.mouse_history = []
                        if min_mass > 10**32: min_mass = 10**32
                        if max_mass > 10**33: max_mass = 10**33
                        colours = [(255,70,110), (50,100,255), 
                                    (255,255,200)]
                        colour = random.choice(colours)
                        m = random.randrange(min_mass, max_mass)
                        vx, vy = ds_x/dt, ds_y/dt
                        if (v_x_adjust and v_y_adjust) is not None:
                            vx+=v_x_adjust
                            vy+=v_y_adjust
                        s, v = s1, [vx, vy]
                        M = Mass(m=m, s=s, v=v, colour=colour, avg_density=1400)
                        Model_System.current_system.append(M) 
                    Model_System.combine_removed_masses() 

                        
    # Calling the all Gravitation object methods to perform the simulation
    def update_position(self, Model_System):
        if len(Model_System.current_system) > 0 and self.drawing:
            Model_System.restrict_system_size(Model_System.current_system) 
            Model_System.mass_network()
            Model_System.get_neighbours()
            Model_System.r_vectors()
            Model_System.R_mag()
            Model_System.g_vectors()
            Model_System.resultant_g()
            Model_System.calc_velocity()
            Model_System.reposition()  
            Model_System.object_locale_data() 
            Model_System.combine_removed_masses()    
        if self.time_elapsed >= self.countdown and self.drawing == False: self.drawing=True

    # _______________________________________ Execution___________________________________
    # Executing the simulation via a method containing gaming loop, which 
    # continually reiterates all the above, creating 
    def main(self):
        Model_System = Gravitation(self) 
        while self.run:     
            self.caption(years=True)    
            self.event_loop(Model_System, mass_range=[10**29,10**30])    
            self.draw(Model_System)
            self.frame_of_reference(Model_System)
            self.update_position(Model_System)
            self.update_displayed_info()
            self.clock_tick(Model_System)
            pygame.display.update()
        pygame.quit()
Main().main()