from mass import *
import helper_functions

  
"""
Gravitation class is responsible for calculating initial data provided by 
each Mass instance created in the Main class, then updating each mass's data 
structures for the next calculation. """
class Gravitation:

    time_step = 3000                 # Default 5000 seconds per frame 

    # Initialising class so class instances can be made and its 
    # methods and attrbutes accessed
    def __init__(self,main):
        assert Gravitation.time_step > 0 and Gravitation.time_step <= 10**4
        assert abs(self.time_step) <= 3000
        self.main = main
        assert self.main.TIME_LAPSE >=0 and self.main.TIME_LAPSE <= 1
        self.current_system = main.input
        self.initialise_data_structures()
        
    def initialise_data_structures(self):
        self.map, self.p_total = {}, []
        self.dT = Gravitation.time_step*self.main.TIME_LAPSE
        self.removed, self.rem_ids, self.new_ids, self.new_system = [],[],[],[]

    
    # ________________________ Methods for calculating object positions
    # 1. Creating a method which ientidies all mass instances surrounding the current 
    # mass. A dictionary / self.map contains {mass : surrounding masses} elements.
    def mass_network(self):
        dict = {}
        for ind in range(len(self.current_system)):
            if type(self.current_system[ind]) == Mass:
                vals = []
                for n in self.current_system:
                    if self.current_system[ind] != n:
                        vals.append(n)
                dict[self.current_system[ind]] = tuple(vals)
        self.map = dict

    # 2. The following method will itterate through this dictionary and update the 
    # Mass.others data structure, creating a 'gravitational network' of mass instances
    def get_neighbours(self):
        for n in self.map:
            others = []
            for i in self.map[n]:
                others.append(i)
            n.others=others

    # 3. Calculate vector spanning between center of current object and surrounding objects
    def r_vectors(self):
        for n in self.map:
            out = []
            if len(n.others)>0:
                for i in self.map[n]:
                    r = [-(n.s[j]-i.s[j]) for j in range(2)]
                    out.append(r)
            n.r = out

    # 4. Calculating the magnitude of these vectors 
    def R_mag(self):
        for n in self.current_system:
            result = []
            for i in n.r:
                dist = ((i[0])**2 + (i[1])**2)**0.5
                result.append(dist)
            n.r_mag = result

    # 5. Calculating the acceleration vector of current object due to gravitational force 
    # exerted by surrounding objects
    def g_vectors(self):
        for n in self.current_system:
            result = []
            if len(n.others) > 0:
                for k in range(len(n.r_mag)):
                    if n.r_mag[k] > n.real_diameter + n.others[k].real_diameter:
                        gx = round(self.main.G*n.others[k].m*n.r[k][0]/(n.r_mag[k]**3),10)
                        gy = round(self.main.G*n.others[k].m*n.r[k][1]/(n.r_mag[k]**3),10)
                        # Becomes a cubic function of vector magnitude when written in vector form.
                    else: 
                        gx,gy=0,0
                        n.others[k].g = [[0,0]]
                        # Assuming gn = 0 below surface of each object to avoid assymptotic 
                        # gravity and erroneous position updates
                    result.append([gx,gy])
            n.g = result

    # 6. Adding these g vectors together to find the overall/resultant vector acting 
    # on current object.
    def resultant_g(self):
        for n in self.current_system:
            gR_x, gR_y = 0,0
            if len(n.others)>0:
                for i in n.g:
                    gR_x += i[0]
                    gR_y += i[1]
            n.gR = [gR_x, gR_y]

    # 7. From this we can directly calculate the current object's resultant velocity vector.
    def calc_velocity(self):
        for n in self.current_system:
            vx,vy = 0,0
            if len(n.gR) >0:
                vx += n.v[0] + n.gR[0]*self.dT 
                vy += n.v[1] + n.gR[1]*self.dT
            n.v = [vx,vy]

    # 8. This allows us to determine the current position of the object 
    def reposition(self):
        self.combine_removed_masses()
        for n in self.current_system:
            if len(n.gR) >0: 
                sx,sy = 0,0
                sx += n.s[0] + n.v[0]*self.dT 
                sy += n.s[1] + n.v[1]*self.dT 
                n.s = [sx,sy]
                n.screen_points = helper_functions.pygame_array([n.s[0]], [n.s[1]], 
                                                                self.main.screen_width, 
                                                                self.main.screen_height)
        
                
    # __________________The following methods deal with collisions and momentum transfer: 
    # 9. The following method will allow the the machine to differentiate between 
    #    collided masses and other masses. 
    def remove_collided(self):
        removed,new = [],[]
        for n in self.current_system:
            for distance in n.r_mag:
                ind = n.r_mag.index(distance)
                size_other = n.others[ind].real_diameter
                gRx, gRy= 0,0
                vf_x = abs(n.v[0]) + abs(n.others[ind].v[0]) + gRx*self.dT  
                vf_y = abs(n.v[1]) + abs(n.others[ind].v[1]) + gRy*self.dT
                vf_mag = (vf_x**2 +vf_y**2)**0.5                             
                deletion_dist = (0.5*n.real_diameter + 0.5*size_other)
                LIMIT = deletion_dist + vf_mag*self.dT
                if distance <= LIMIT: 
                    removed.append(n) 
                    n.gR=[0,0]
            if n in removed: continue
            else: new.append(n)  
        return removed, new

    # 10.
    # This function deals with transfer of momentum and other physical attributes. I've since discovered that 
    # pygame has it's own collsion handling methods but the 2-3 other projects I have seen since 
    # still don't seem to address momentum transfer. The following is fine until masses at different locations 
    # occasionally collide simulatneously. 
    def combine_removed_masses(self):
        removed, new = self.remove_collided()
        if len(removed) > 0:
            new = self.restrict_system_size(new)
            total_mass = sum([n.m for n in new])
            masses_collected = [n.m for n in removed]
            ind = masses_collected.index(max(masses_collected))
            self.substitute_colour = removed[ind].colour
            m_final = 0
            density = 0
            px,py = 0,0
            sx,sy = 0,0
            rem_pos_x, rem_pos_y = [], []
            append=False
            for n in removed: 
                rem_pos_x, rem_pos_y = [j.s[0] for j in removed if j.locale == n.locale], [j.s[1] for j in removed if j.locale == n.locale]
                mass_ratio = 0
                for i in n.others:
                    if i in removed and i.locale == n.locale: 
                        m_final += n.m
                        density += n.avg_density*n.m 
                        mass_ratio += i.m/(n.m+i.m) 
                        px += n.m*n.v[0]
                        py += n.m*n.v[1] 
                        sx += n.s[0]*(1-mass_ratio)   
                        sy += n.s[1]*(1-mass_ratio)   
            if sx >= min(rem_pos_x) and sx<max(rem_pos_x) and sy >=min(rem_pos_y) and sy<max(rem_pos_y):
                append=True
            elif sx > min(rem_pos_x) and sx<=max(rem_pos_x) and sy >min(rem_pos_y) and sy<=max(rem_pos_y):
                append=True  
            if append: 
                p_final= [px,py]
                v_f = [n/m_final for n in p_final] 
                for n in v_f: 
                    if n >10**2: n ==10**2
                v_final = [n for n in v_f]
                avg_density = density/m_final
                s_final = [sx,sy]
                M = Mass(m=m_final, s=s_final, v=v_final, colour = self.substitute_colour, 
                            avg_density = avg_density)
                new.append(M)
                new[-1].gR=[0,0]
                for n in removed: 
                    if n.ID == self.main.center_object_ID:
                        new[-1].ID = self.main.center_object_ID
                self.rem_ids = [n.ID for n in removed]
                self.new_ids = [n.ID for n in new]
                new_total_mass = sum([n.m for n in new])
                # Now if the above criterior are not met, the updated system will simply not 
                # contain the new mass. This causes masses to 'vanish'. 
                if new_total_mass >= total_mass:
                    self.current_system = new
                # The above if block seems to help get around that a bit 
    

    # _________________________________ Additional methods for efficiency_________________
    # 11 *
    def object_locale_data(self):
        uniques = []
        for n in self.current_system: 
            unit = 1
            locale = []
            for i in n.s:
                if i !=0: 
                    unit = i/abs(i)
                    locale.append(round(unit*math.log10(abs(i))))
                else: 
                    unit = 0
                    locale.append(unit)
            n.locale = locale
            if n.locale not in uniques: uniques.append(n.locale)
    # 12 **
    def restrict_system_size(self, system): 
        for n in system:
            if n.locale is not None:
                item = n.locale
                for i in item:
                    if abs(i) > 1.1*math.log10(self.main.SCREEN_SCALE*self.main.AU):
                        system.remove(n)
        return system
    
    """
    11 * 
        It turns out the methods above do not perfeorm well when multiple collisions occur
        simulatneously at different points in space. Although the issue has not been resolved, it has 
        been mitigated. 
        The above method labels all removed objects with a locale attribute - arounded base ten 
        logarithm of the position vector which will be the same for distinct clusters of coliding 
        objects. It could be crucial to a better method for handling collisons. 

    12 ** Eliminating objects which are way off screen
    __________________________________________________________________________________________________
    """
         
         