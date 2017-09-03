"""PMDD.py
Created by Latha Sethuraman, Katherine Dykes.
Copyright (c) NREL. All rights reserved."""

from openmdao.main.api import Component,Assembly
from openmdao.lib.datatypes.api import Float,Array,Str
import numpy as np
from numpy import array, float,min
from scipy.interpolate import interp1d
from openmdao.lib.drivers.api import COBYLAdriver, CONMINdriver,NEWSUMTdriver,SLSQPdriver,Genetic
import pandas as pd


class PMSG(Component):

 """ Evaluates the total cost """
 
 r_s = Float(0.0, iotype='in', desc='airgap radius r_s')
 l_s = Float(0.0, iotype='in', desc='Stator core length l_s')
 h_s = Float(0.0, iotype='in', desc='Yoke height h_s')
 tau_p =Float(0.0, iotype='in', desc='Pole pitch self.tau_p')
 B_g = Float(0.0, iotype='out', desc='Peak air gap flux density B_g')
 machine_rating=Float(iotype='in', desc='Machine rating')
 n_nom=Float(iotype='in', desc='rated speed')
 Torque=Float(iotype='in', desc='Rated torque ')
 t= Float(0.0, iotype='in', desc='rotor back iron')
 t_s= Float(0.0, iotype='in', desc='stator back iron t')
 t_d = Float(0.0, iotype='in', desc='disc thickness')
 n_s =Float(0.0, iotype='in', desc='number of stator arms n_s')
 b_st = Float(0.0, iotype='in', desc='arm width b_r')
 d_s= Float(0.0, iotype='in', desc='arm depth d_r')
 t_ws =Float(0.0, iotype='in', desc='arm depth thickness self.t_wr')
 b_s=Float(0.0, iotype='out', desc='slot width')
 b_t=Float(0.0, iotype='out', desc='tooth width')
 h_ys=Float(0.0, iotype='in', desc='Yoke height')
 h_yr=Float(0.0, iotype='in', desc='rotor yoke height')
 h_m=Float(0.0, iotype='in', desc='magnet height')
 R_o=Float(0.0, iotype='in', desc='Shaft radius')
 b_m=Float(0.0, iotype='out', desc='magnet width')
 M_actual=Float(0.0, iotype='out', desc='Actual mass')
 Mass=Float(0.0, iotype='out', desc='Actual mass')
 p=Float(0.0, iotype='out', desc='No of pole pairs')
 f=Float(0.0, iotype='out', desc='Output frequency')
 E_p=Float(0.0, iotype='out', desc='Stator phase voltage')
 f=Float(0.0, iotype='out', desc='Generator output frequency')
 I_s=Float(0.0, iotype='out', desc='Generator output phase current')
 R_s=Float(0.0, iotype='out', desc='Stator resistance')
 L_s=Float(0.0, iotype='out', desc='Stator synchronising inductance')
 J_s=Float(0.0, iotype='out', desc='Current density')
 B_symax = Float(1.2, iotype='out', desc='Peak Stator Yoke flux density B_ymax')
 B_tmax=Float(0.01, iotype='out', desc='Peak Teeth flux density')
 B_rymax=Float(0.01, iotype='out', desc='Peak Rotor yoke flux density')
 B_smax=Float(0.01, iotype='out', desc='Peak Stator flux density')
 B_pm1=Float(0.01, iotype='out', desc='Fundamental component of peak air gap flux density')
 A_Cuscalc=Float(0.01, iotype='out', desc='Conductor cross-section mm^2')
 A_1 =Float(0, iotype='out', desc='Electrical loading')
 Costs= Float(0.0, iotype='out', desc='Total cost')
 K_rad=Float(0.0, iotype='out', desc='K_rad')
 W_1a =Float(100, iotype='out', desc='Number of turns in the stator winding')
 Losses=Float(0.0, iotype='out', desc='Total loss')
 gen_eff=Float(0.0, iotype='out', desc='Generator efficiency')
 Active=Float(0.0, iotype='out', desc='Generator efficiency')
 Stator=Float(0.0, iotype='out', desc='Generator efficiency')
 Rotor=Float(0.0, iotype='out', desc='Generator efficiency')
 mass_PM=Float(0.0, iotype='out', desc='Generator efficiency')
 M_Cus		=Float(0.0, iotype='out', desc='Generator efficiency')
 M_Fest	=Float(0.0, iotype='out', desc='Generator efficiency')
 M_Fesy	=Float(0.0, iotype='out', desc='Generator efficiency')
 M_Fery	=Float(0.0, iotype='out', desc='Generator efficiency')
 Iron=Float(0.0, iotype='out', desc='Electrical steel mass')
 Stator_radial=Float(0.01, iotype='out', desc='Rotor radial deflection')
 Stator_axial=Float(0.01, iotype='out', desc='Stator Axial deflection')
 Stator_circum=Float(0.01, iotype='out', desc='Rotor radial deflection')
 Rotor_radial=Float(0.01, iotype='out', desc='Generator efficiency')
 Rotor_axial=Float(0.01, iotype='out', desc='Rotor Axial deflection')
 Rotor_circum=Float(0.01, iotype='out', desc='Rotor circumferential deflection')
 P_gennom=Float(0.01, iotype='out', desc='Generator Power')
 u_Ar	=Float(0.01, iotype='out', desc='Rotor radial deflection')
 y_Ar =Float(0.01, iotype='out', desc='Rotor axial deflection')
 u_As=Float(0.01, iotype='out', desc='Stator radial deflection')
 y_As =Float(0.01, iotype='out', desc='Stator axial deflection')
 z_A_s=Float(0.01, iotype='out', desc='Stator circumferential deflection')  
 u_all_r=Float(0.01, iotype='out', desc='Allowable radial rotor')
 u_all_s=Float(0.01, iotype='out', desc='Allowable radial stator')
 y_all=Float(0.01, iotype='out', desc='Allowable axial')
 z_all_s=Float(0.01, iotype='out', desc='Allowable circum stator')
 z_all_r=Float(0.01, iotype='out', desc='Allowable circum rotsor')
 b_all_s=Float(0.01, iotype='out', desc='Allowable arm')
 b_all_r=Float(0.01, iotype='out', desc='Allowable arm dimensions')
 TC1	=Float(0.1, iotype='out', desc='Torque constraint')
 TC2=Float(0.1, iotype='out', desc='Torque constraint-rotor')
 TC3=Float(0.1, iotype='out', desc='Torque constraint-stator')
 R_out=Float(0.01, iotype='out', desc='Outer radius')
 N_s_max			=Float(0.1, iotype='out', desc='Maximum number of turns per coil')
 S			=Float(0.1, iotype='out', desc='Stator slots')
 K_load=Float(0.1, iotype='out', desc='Load factor')
 Slot_aspect_ratio=Float(0.1, iotype='out', desc='Slot aspect ratio')
 main_shaft_cm = Array(np.array([0.0, 0.0, 0.0]),iotype='in', desc='High speed side CM')
 main_shaft_length=Float(iotype='in', desc='main shaft length')
 cm=Array(np.array([0.0, 0.0, 0.0]),iotype='out', desc='COM [x,y,z]')
 I=Array(np.array([0.0, 0.0, 0.0]), iotype='out', desc='Moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass')
 
 
 def execute(self):
  r_s = self.r_s
  l_s = self.l_s
  h_s = self.h_s
  tau_p =self.tau_p
  B_g = self.B_g
  n_s=self.n_s
  t= self.t
  t_s=self.t_s
  t_d =self.t_d
  b_st = self.b_st
  d_s = self.d_s
  t_ws =self.t_ws
  b_s =self.b_s
  b_t= self.b_t
  h_ys = self.h_ys
  h_yr  = self.h_yr
  h_m =self.h_m
  b_m =self.b_m
  f=self.f
  E_p=self.E_p
  I_s=self.I_s
  R_s=self.R_s
  L_s=self.L_s
  J_s=self.J_s
  M_actual=self.M_actual
  Mass=self.Mass
  gen_eff =self.gen_eff
  Losses=self.Losses
  A_1=self.A_1
  K_rad=self.K_rad
  W_1a=self.W_1a
  Active=self.Active
  Stator=self.Stator
  Rotor=self.Rotor
  mass_PM=self.mass_PM
  M_Cus		=self.M_Cus	
  M_Fest	=self.M_Fest
  M_Fesy	=self.M_Fesy
  M_Fery	=self.M_Fery
  Iron=self.Iron
  Stator_radial=self.Stator_radial
  Stator_axial=self.Stator_axial
  Stator_circum=self.Stator_circum
  Rotor_radial=self.Rotor_radial
  Rotor_axial=self.Rotor_axial
  Rotor_circum=self.Rotor_circum
  P_gennom=self.P_gennom
  u_As=self.u_As
  u_Ar=self.u_Ar
  y_As=self.y_As
  y_Ar=self.y_Ar
  z_A_s=self.z_A_s
  z_all_s=self.z_all_s
  z_all_r=self.z_all_r
  R_out=self.R_out
  B_pm1=self.B_pm1
  B_tmax= self.B_tmax
  B_symax=self.B_symax
  B_rymax=self.B_rymax
  B_smax=self.B_smax
  B_pm1=self.B_pm1
  N_s_max=self.N_s_max
  A_Cuscalc=self.A_Cuscalc
  b_all_r=self.b_all_r
  b_all_s=self.b_all_s
  S=self.S
  Stator=self.Stator
  Rotor=self.Rotor
  K_load=self.K_load
  machine_rating=self.machine_rating
  Slot_aspect_ratio=self.Slot_aspect_ratio
  Torque=self.Torque
  main_shaft_cm = self.main_shaft_cm
  main_shaft_length=self.main_shaft_length
  cm=self.cm
  I=self.I
  TC1	=self.TC1
  TC2=self.TC2
  TC3=self.TC3
  R_o=self.R_o
  Costs=self.Costs
	
  from math import pi, cos, sqrt, radians, sin, exp, log10, log, floor, ceil, tan, atan,cosh,sinh
  import numpy as np
  from numpy import sign
  
  rho    =7850                # Kg/m3 steel density
  rho_PM =7450                # Kg/m3 magnet density
  B_r    =1.2                 # Tesla remnant flux density 
  g1      =9.81                # m/s^2 acceleration due to gravity
  E      =2e11                # N/m^2 young's modulus
  sigma  =40e3                # shear stress assumed
  ratio  =0.8                 # ratio of magnet width to pole pitch(bm/self.tau_p) 
  mu_0   =pi*4e-7              # permeability of free space
  mu_r   =1.06								# relative permeability 
  phi    =90*2*pi/360         # tilt angle (rotor tilt -90 degrees during transportation)
  cofi   =0.85                 # power factor
  C_pm   =95
  C_Fes  =0.50139
  C_Fe   =0.556
  C_Cu   =4.786
  h_sy0  =0
  h_w    =0.005
  h_i=0.001 										# coil insulation thickness
  h_s1= 0.001
  h_s2=0.004
  h_s3=self.h_s-h_s1-h_s2
  h_cu=(h_s3-4*h_i)*0.5
  self.t =self.h_yr
  self.t_s =self.h_ys
  y_tau_p=1
  self.K_rad=self.l_s/(2*self.r_s)
  m      =3                    # no of phases
  B_rmax=1.4                  
  q1     =1                    # no of slots per pole per phase
  b_s_tau_s=0.45
  k_sfil =0.65								 # Slot fill factor
  P_Fe0h =4			               #specific hysteresis losses W/kg @ 1.5 T @50 Hz
  P_Fe0e =1			               #specific hysteresis losses W/kg @ 1.5 T @50 Hz
  rho_Cu=1.8*10**(-8)*1.4
  k_fes =0.9
  T =   self.Torque    #549296.586 #4143289.841 #9549296.586 #250418.6168  #698729.0185 #1.7904931e6 # #248679.5986 #9947183.943 #4143289.841 #9549296.586 #4143289.841 #9549296.586 #250418.6168 #698729.0185 #1.7904931e6 #4143289.841  #9947183.943 #for Todd 7.29e6 #9947183.943  #9549296.586 #9947183.943  #698729.0185 #1.7904931e6 #4143289.841 #9549296.586  #9947183.943 #4143289.841 #698729.0185 #9947183.943 #7.29e6 #4143289.841 #250418.6168 #1.7904931e6 #698729.0185 #1.7904931e6 # #9947183.943 #9549296.586 #4143289.841 #250418.6168 #698729.0185 #9549296.586 #4143289.841 #1.7904931e6
  self.P_gennom = self.machine_rating
  E_pnom   = 3000
  n_nom = self.n_nom #10 #16 #10 #12.1 #10 #28.6 #20.5 #16 #12.1 #9.6 #7.2 #9.6 #12.1 #20.5 #9.6 #612.1 # # 16 #16 #12.1 #9.6 #10 #12.1 #28.6 #12.1 #12.1 #16
  v=0.3                        # poisson's ratio
  gear      =1 
    
  self.K_load =1
  B_curve=(0.000,0.050,0.130,0.152,0.176,0.202,0.229,0.257,0.287,0.318,0.356,0.395,0.435,0.477,0.523,0.574,0.627,0.683,0.739,0.795,0.850,0.906,0.964,1.024,1.084,1.140,1.189,1.228,1.258,1.283,1.304,1.324,1.343,1.360,1.375,1.387,1.398,1.407,1.417,1.426,1.437,1.448,1.462,1.478,1.495,1.513,1.529,1.543,1.557,1.570,1.584,1.600,1.617,1.634,1.652,1.669,1.685,1.701,1.717,1.733,1.749,1.769,1.792,1.820,1.851,1.882,1.909,1.931,1.948,1.961,1.972,1.981)
  H_curve=(0,10,20,23,25,28,30,33,35,38,40,43,45,48,52,56,60,66,72,78,87,97,112,130,151,175,200,225,252,282,317,357,402,450,500,550,602,657,717,784,867,974,1117,1299,1515,1752,2000,2253,2521,2820,3167,3570,4021,4503,5000,5503,6021,6570,7167,7839,8667,9745,11167,12992,15146,17518,20000,22552,25417,28906,33333,38932)
  h_interp=interp1d(B_curve,H_curve,fill_value='extrapolate')
  U_Nrated=3.3e3
  # rotor structure      
  
  l					= self.l_s                          #l-stator core length
  l_u       =k_fes * self.l_s                   #useful iron stack length
  We				=self.tau_p
  l_b       = 2*self.tau_p  #end winding length
  l_e       =self.l_s+2*0.001*self.r_s     # equivalent core length
  self.b_m  =0.7*self.tau_p 
  constant=0.5
  a_s       = (self.b_st*self.d_s)-((self.b_st-2*self.t_ws)*(self.d_s-2*self.t_ws)) # cross-sectional area of stator armms
  A_st      =l*self.t_s                     # cross-sectional area of rotor cylinder
  N_st			= round(self.n_s)
  theta_s		=pi*1/N_st  # half angle between spokes
  I_st       =l*self.t_s**3/12                      # second moment of area of stator cylinder
  I_arm_axi_s	=((self.b_st*self.d_s**3)-((self.b_st-2*self.t_ws)*(self.d_s-2*self.t_ws)**3))/12  # second moment of area of stator arm
  I_arm_tor_s	= ((self.d_s*self.b_st**3)-((self.d_s-2*self.t_ws)*(self.b_st-2*self.t_ws)**3))/12  # second moment of area of rotot arm w.r.t torsion
  dia				=  2*self.r_s              # air gap diameter
  g         =  0.001*dia
  
  R					= self.r_s-g-self.h_m-0.5*self.t
  b=self.R_o
  R_b=R-0.5*self.t
  R_a=R+0.5*self.h_yr
  a=R-0.5*self.t;
  a_1=R_b
  c					=R/500
  R_1				= R-self.t*0.5      
  K					=4*(sin(ratio*pi/2))/pi
  self.R_out=(R/0.995+self.h_s+self.h_ys)
  k_2       = sqrt(I_st/A_st)  # radius of gyration
                                
  
  R_st 			=self.r_s+self.h_s+self.h_ys*0.5

  self.b_all_s		=2*pi*self.R_o/N_st                           
  
  K					=4*(sin(ratio*pi/2))/pi
 
  
  b_s1			=  0.003
  self.p		=  round(pi*dia/(2*self.tau_p))
  self.f    =  self.n_nom*self.p/60
  self.S				= 2*self.p*q1*m 
  N_conductors=self.S*2
  self.W_1a=N_conductors/2/3
  tau_s=pi*dia/self.S
  
  self.b_s	=  b_s_tau_s*tau_s    #slot width 
  self.b_t	=  tau_s-(self.b_s)          #tooth width
  self.Slot_aspect_ratio=self.h_s/self.b_s
  k_t       =self.b_t/tau_s
  b_so			=  0.004
  b_cu			=  self.b_s -2*h_i         # conductor width
  gamma			=  4/pi*(b_so/2/(g+self.h_m/mu_r)*atan(b_so/2/(g+self.h_m/mu_r))-log(sqrt(1+(b_so/2/(g+self.h_m/mu_r))**2)))
  k_C				=  tau_s/(tau_s-gamma*(g+self.h_m/mu_r))   # carter coefficient
  g_eff			=  k_C*(g+self.h_m/mu_r)                   
  om_m			=  gear*2*pi*self.n_nom/60
  
  om_e			=  self.p*om_m/2
  
  alpha_p		=  pi/2*0.7
  self.B_pm1	 		=  B_r*self.h_m/mu_r/(g_eff)
  
  self.B_g=  B_r*self.h_m/mu_r/(g_eff)*(4/pi)*sin(alpha_p)
  self.B_symax=self.B_g*self.b_m*l_e/(2*self.h_ys*l_u)
  self.B_rymax=self.B_g*self.b_m*l_e/(2*self.h_yr*l)
  
  self.B_tmax	=self.B_g*tau_s/self.b_t
  q3					= self.B_g**2/2/mu_0   # normal stress
  m2        =(k_2/R_st)**2   
  c1        =R_st/500
  R_1s      = R_st-self.t_s*0.5
  d_se=dia+2*(self.h_ys+self.h_s+h_w)  # stator outer diameter
  
  self.mass_PM   =(2*pi*(R+0.5*self.t)*l*self.h_m*ratio*rho_PM)           # magnet mass
  
                                      
  mass_st_lam=7700*2*pi*(R+0.5*self.t)*l*self.h_yr                                     # mass of rotor yoke steel  
    
  lamb   =((3*(1-v**2)/R_a**2/self.h_yr**2)**0.25)
  x1=lamb*self.l_s
  # cylindrical shell function and circular plate parameters for disc rotor
  #C_1=0.5*(1+v)*(b/a)*log(a/b)+(1-v)*0.25*((a/b)-(b/a))
  C_2=cosh(x1)*sin(x1)+sinh(x1)*cos(x1)
  C_3=sinh(x1)*sin(x1)
  C_4=cosh(x1)*sin(x1)-sinh(x1)*cos(x1)
  C_11=(sinh(x1))**2-(sin(x1))**2
  C_13=cosh(x1)*sinh(x1)-cos(x1)*sin(x1)
  C_14=(sinh(x1)**2+sin(x1)**2)
  C_a1=cosh(x1*0.5)*cos(x1*0.5) 
  C_a2=cosh(x1*0.5)*sin(x1*0.5)+sinh(x1*0.5)*cos(x1*0.5) 
  F_1_x0=cosh(lamb*0)*cos(lamb*0)
  F_1_ls2=cosh(lamb*0.5*self.l_s)*cos(lamb*0.5*self.l_s)
  F_2_x0=cosh(lamb*0)*sin(lamb*0)+sinh(lamb*0)*cos(lamb*0)
  F_2_ls2=cosh(x1/2)*sin(x1/2)+sinh(x1/2)*cos(x1/2)
  if (self.l_s<2*a):
  	a=self.l_s/2
  else:
  	a=self.l_s*0.5-1
  F_a4_x0=cosh(lamb*(0))*sin(lamb*(0))-sinh(lamb*(0))*cos(lamb*(0))
  
  
  F_a4_ls2=cosh(pi/180*lamb*(0.5*self.l_s-a))*sin(pi/180*lamb*(0.5*self.l_s-a))-sinh(pi/180*lamb*(0.5*self.l_s-a))*cos(pi/180*lamb*(0.5*self.l_s-a))
  D_r=E*self.h_yr**3/(12*(1-v**2))  
  D_ax=E*self.t_d**3/(12*(1-v**2))
  
  
  Part_1 =R_b*((1-v)*R_b**2+(1+v)*self.R_o**2)/(R_b**2-self.R_o**2)/E
  
  Part_2 =(C_2*C_a2-2*C_3*C_a1)/2/C_11
 
  
  Part_3 = (C_3*C_a2-C_4*C_a1)/C_11
  
  Part_4 =((0.25/D_r/lamb**3))
  
  Part_5=q3*R_b**2/(E*(R_a-R_b))
  
  f_d = Part_5/(Part_1-self.t_d*(Part_4*Part_2*F_2_ls2-Part_3*2*Part_4*F_1_ls2-Part_4*F_a4_ls2))
  fr=f_d*self.t_d
 
  W=0.5*g1*sin(phi)*((self.l_s-self.t_d)*self.h_yr*rho)
  w=rho*g1*sin(phi)*self.t_d
  a_i=self.R_o
 
  self.u_Ar				=abs(Part_5+fr/2/D_r/lamb**3*((-F_1_x0/C_11)*(C_3*C_a2-C_4*C_a1)+(F_2_x0/2/C_11)*(C_2*C_a2-2*C_3*C_a1)-F_a4_x0/2))
  
  self.u_all_r    =c/20  # allowable radial deflection
  
  self.u_all_s    = c1/20

  self.y_all    =2*l/100    # allowable axial deflection
  
  C_2p= 0.25*(1-(((self.R_o/R)**2)*(1+(2*log(R/self.R_o)))))
  C_3p=(self.R_o/4/R)*((1+(self.R_o/R)**2)*log(R/self.R_o)+(self.R_o/R)**2-1)
  C_6= (self.R_o/4/R_a)*((self.R_o/R_a)**2-1+2*log(R_a/self.R_o))
  C_5=0.5*(1-(self.R_o/R)**2)
  C_8= 0.5*(1+v+(1-v)*((self.R_o/R)**2));
  C_9=(self.R_o/R)*(0.5*(1+v)*log(R/self.R_o) + (1-v)/4*(1-(self.R_o/R)**2));
  L_17=0.25*(1 - (1-v)*(1-(self.R_o/a_1)**4)/4 - ((self.R_o/a_1)**2)*(1 + (1-v)*log(a_1/self.R_o)));
  L_11=(1 + 4*(self.R_o/a_1)**2 - 5*(self.R_o/a_1)**4 - 4*((self.R_o/a_1)**2)*log(a_1/self.R_o)*(2+(self.R_o/a_1)**2))/64
  L_14=(1/16)*(1-(self.R_o/R_b)**4-4*(self.R_o/R_b)**2*log(R_b/self.R_o))
 

  y_ai=-W*(a_1**3)*(C_2p*(C_6*a_1/self.R_o - C_6)/C_5 - a_1*C_3p/self.R_o +C_3p)/D_ax;
  M_rb=-w*R**2*(C_6*(R**2-self.R_o**2)*0.5/R/self.R_o-L_14)/C_5
  Q_b=w*0.5*(R**2-self.R_o**2)/self.R_o
  y_aii=M_rb*R_a**2*C_2p/D_ax+Q_b*R_a**3*C_3p/D_ax-w*R_a**4*L_11/D_ax
  self.y_Ar=abs(y_ai+y_aii)
 
  self.z_all_s     =0.05*2*pi*R_st/360  # allowable torsional deflection
  self.z_all_r=0.05*2*pi*R/360  # allowable torsional deflection
  
  val_str_cost_rotor	= C_pm*mass_PM+C_Fe*(pi*l*(R_a**2-R**2)*7700)+C_Fes*pi*self.t_d*(R**2-self.R_o**2)*rho
  val_str_rotor		= self.mass_PM+(pi*l*(R_a**2-R**2)*7700)+pi*self.t_d*(R**2-self.R_o**2)*rho
  
  self.Rotor_radial=self.u_Ar
  self.Rotor_axial=self.y_Ar
  
  
  
  r_m     	=  self.r_s+h_sy0+self.h_ys+self.h_s #magnet radius
  
  r_r				=  self.r_s-g             #rotor radius
  
  v_ys=constant*(self.tau_p+pi*(self.h_s+0.5*self.h_ys)/self.p)*h_interp(self.B_symax)
  v_d=h_interp(self.B_tmax)*(h_s3+0.5*h_s2)+h_interp(self.B_tmax)*(0.5*h_s2+h_s1)
  v_yr=constant*(self.tau_p+pi*(g+self.h_m+0.5*self.h_yr)/self.p)*h_interp(self.B_rymax)
  v_m=self.h_m*self.B_g/mu_r/mu_0
  v_g       =  g_eff*self.B_g/mu_0
  
  # stator %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
  k_wd			= sin(pi/6)/q1/sin(pi/6/q1)      # winding factor
  beta_skew	= tau_s/self.r_s;
  k_wskew		= sin(self.p*beta_skew/2)/(self.p*beta_skew/2)
  L_t=self.l_s+2*self.tau_p
  
  self.E_p	= 2*(self.W_1a)*L_t*self.r_s*k_wd*k_wskew*om_m*self.B_g/sqrt(2)
  
  l_Cus			= 2*(self.W_1a)*(2*self.tau_p+L_t)
  A_s				= self.b_s*(self.h_s-h_w)*q1*self.p
  A_scalc   = self.b_s*1000*(self.h_s*1000-h_w*1000)*q1*self.p
  A_Cus			= A_s*k_sfil/(self.W_1a)
  self.A_Cuscalc = A_scalc *k_sfil/(self.W_1a)
  self.R_s	= l_Cus*rho_Cu/A_Cus

  L_m				= 2*m*k_wd**2*(self.W_1a)**2*mu_0*self.tau_p*L_t/pi**2/g_eff/self.p
  L_ssigmas=2*mu_0*self.l_s*self.W_1a**2/self.p/q1*((self.h_s-h_w)/(3*self.b_s)+h_w/b_so)  #slot leakage inductance
  L_ssigmaew=(2*mu_0*self.l_s*self.W_1a**2/self.p/q1)*0.34*g*(l_e-0.64*self.tau_p*y_tau_p)/self.l_s                                #end winding leakage inductance
  L_ssigmag=2*mu_0*self.l_s*self.W_1a**2/self.p/q1*(5*(g*k_C/b_so)/(5+4*(g*k_C/b_so))) # tooth tip leakage inductance#tooth tip leakage inductance
  L_ssigma	= (L_ssigmas+L_ssigmaew+L_ssigmag)
  self.L_s  = L_m+L_ssigma
  Z=(self.P_gennom/(m*self.E_p))
  
  #self.I_s=Z
  G=(self.E_p**2-(om_e*self.L_s*Z)**2)
   
  self.I_s= sqrt(Z**2+(((self.E_p-G**0.5)/(om_e*self.L_s)**2)**2))
  
  self.J_s	= self.I_s/self.A_Cuscalc

  I_snom		=(self.P_gennom/m/self.E_p/cofi) #rated current

  I_qnom		=self.P_gennom/(m*self.E_p)
  X_snom		=om_e*(L_m+L_ssigma)
  
  self.B_smax=sqrt(2)*self.I_s*mu_0/g_eff
  pp=1  #number of parallel paths
  N_s_j=sqrt(3)*(self.h_s-h_w)*tau_s*(1-k_t)*k_sfil*self.J_s*pp*U_Nrated/self.P_gennom
  N_s_s=(self.h_s-h_w)*tau_s*(1-k_t)*k_sfil*0.5
  
  self.A_1 = 6*self.W_1a*self.I_s/(pi*dia)
  N_s_EL=self.A_1*pi*(dia-g)/(q1*self.p*m)
  self.N_s_max=min([N_s_j,N_s_s,N_s_EL])
  

  #" masses %%%%%%%%%%%%%%%%%%%%%%%%%%%%#%%%%%%"
  V_Cus 	=m*l_Cus*A_Cus     # copper volume
  V_Fest	=L_t*2*self.p*q1*m*self.b_t*self.h_s   # volume of iron in stator tooth
  V_Fesy	=L_t*pi*((self.r_s+self.h_s+self.h_ys+h_sy0)**2-(self.r_s+self.h_s)**2) # volume of iron in stator yoke
  V_Fery	=L_t*pi*((r_r-self.h_m)**2-(r_r-self.h_m-self.h_yr)**2)
  
  self.M_Cus		=V_Cus*8900
  self.M_Fest	=V_Fest*7700
  self.M_Fesy	=V_Fesy*7700
  self.M_Fery	=V_Fery*7700
  M_Fe		=self.M_Fest+self.M_Fesy+self.M_Fery
  M_gen		=(self.M_Cus)
  K_gen		=self.M_Cus*C_Cu
  
  mass_st_lam_s= self.M_Fest+pi*l*7700*((R_st+0.5*self.h_ys)**2-(R_st-0.5*self.h_ys)**2) 
  W_is			=0.5*g1*sin(phi)*(rho*l*self.d_s**2) # weight of rotor cylinder                               # length of rotor arm beam at which self-weight acts
  W_iis     =g1*sin(phi)*(mass_st_lam_s+V_Cus*8900)/2/N_st
  w_s         =rho*g1*sin(phi)*a_s*N_st
  
  l_is      =R_st-self.R_o
  l_iis     =l_is 
  l_iiis    =l_is
    

  
  
  #stator structure deflection calculation
  mass_stru_steel  =2*(N_st*(R_1s-self.R_o)*a_s*rho)
  Numers=R_st**3*((0.25*(sin(theta_s)-(theta_s*cos(theta_s)))/(sin(theta_s))**2)-(0.5/sin(theta_s))+(0.5/theta_s))
  Povs=((theta_s/(sin(theta_s))**2)+1/tan(theta_s))*((0.25*R_st/A_st)+(0.25*R_st**3/I_st))
  Qovs=R_st**3/(2*I_st*theta_s*(m2+1))
  Lovs=(R_1s-self.R_o)*0.5/a_s
  Denoms=I_st*(Povs-Qovs+Lovs) 
 
  self.u_As				=(q3*R_st**2/E/self.t_s)*(1+Numers/Denoms)
  X_comp1 = (W_is*l_is**3/12/E/I_arm_axi_s)
  X_comp2 =(W_iis*l_iis**4/24/E/I_arm_axi_s)
  X_comp3 =w_s*l_iiis**4/24/E/I_arm_axi_s
  
  self.y_As       =X_comp1+X_comp2+X_comp3  # axial deflection
  self.z_A_s  =2*pi*(R_st+0.5*self.t_s)*l/(2*N_st)*sigma*(l_is+0.5*self.t_s)**3/3/E/I_arm_tor_s 
  
  val_str_stator		= mass_stru_steel+mass_st_lam_s      
  
  val_str_cost_stator =	C_Fes*mass_stru_steel+C_Fe*mass_st_lam_s
    
  val_str_mass=val_str_rotor+val_str_stator
  
  
  self.Stator_radial=self.u_As
  self.Stator_axial=self.y_As
  self.Stator_circum=self.z_A_s
  self.TC1=T/(2*pi*sigma)     # Desired shear stress 
  self.TC2=R**2*l              # Evaluating Torque constraint for rotor
  self.TC3=R_st**2*l           # Evaluating Torque constraint for stator
  
  self.Iron=mass_st_lam_s+(2*pi*t*l*(R+0.5*self.t)*7700)
  self.PM=self.mass_PM
  self.Copper=self.M_Cus
  self.Inactive=mass_stru_steel+(pi*(R**2-R_o**2)*self.t_d*rho)
  
  self.Stator=mass_st_lam_s+mass_stru_steel+self.Copper
  self.Rotor=(2*pi*t*l*(R+0.5*self.t)*7700)+(pi*(R**2-R_o**2)*self.t_d*rho)+self.PM
  self.M_actual	=self.Stator+self.Rotor
  self.Mass = self.M_actual
  self.Active=self.Iron+self.Copper+self.mass_PM
 #"% losses %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
  P_Cu		=m*self.I_s**2*self.R_s
  
  K_R=1.2
  P_Sc=m*(self.R_s)*K_R*(I_snom)**2*1  #losses to include skin effect
  
  
  if (self.K_load==0):
  	P_Cusnom_total=P_Cu
  else:
    P_Cusnom_total=P_Sc*self.K_load**2
  
  
  
  
  #B_tmax	=B_pm*tau_s/self.b_t
  P_Hyys	=self.M_Fesy*(self.B_symax/1.5)**2*(P_Fe0h*om_e/(2*pi*60))
  P_Ftys	=self.M_Fesy*((self.B_symax/1.5)**2)*(P_Fe0e*(om_e/(2*pi*60))**2)
  P_Fesynom=P_Hyys+P_Ftys
  P_Hyd=self.M_Fest*(self.B_tmax/1.5)**2*(P_Fe0h*om_e/(2*pi*60))
  P_Ftd=self.M_Fest*(self.B_tmax/1.5)**2*(P_Fe0e*(om_e/(2*pi*60))**2)
  P_Festnom=P_Hyd+P_Ftd
  P_ad=0.2*(P_Hyys + P_Ftys + P_Hyd + P_Ftd ) # additional stray losses due to leakage flux
  pFtm =300 # specific magnet loss
  P_Ftm=pFtm*2*self.p*self.b_m*self.l_s
  
  P_genlossnom=P_Cusnom_total+P_Festnom+P_Fesynom+P_ad+P_Ftm

  self.gen_eff=self.P_gennom*100/(self.P_gennom+P_genlossnom)
  
  self.Losses=P_genlossnom
  
  
  #"% cost of losses"
  val_str_cost=val_str_cost_rotor+val_str_cost_stator
  self.Costs=val_str_cost+K_gen
  
  self.I[0]   = (0.5*self.M_actual*self.R_out**2)
  self.I[1]   = (0.25*self.M_actual*self.R_out**2+(1/12)*self.M_actual*self.l_s**2) 
  self.I[2]   = self.I[1]
  cm[0]  = self.main_shaft_cm[0] + self.main_shaft_length/2. + self.l_s/2
  cm[1]  = self.main_shaft_cm[1]
  cm[2]  = self.main_shaft_cm[2]
  
  #print   g1*sin(phi)*(self.M_Fest+V_Cus*8900)/2/N_st,q3,self.z_all_r
  

class Drive_PMSG(Assembly):
	Eta_target=Float(iotype='in', desc='Target drivetrain efficiency')
	T_rated=Float(iotype='in', desc='Torque')
	N=Float(iotype='in', desc='rated speed')
	P_rated=Float(iotype='in', desc='rated power')
	main_shaft_cm = Array(np.array([0.0, 0.0, 0.0]),iotype='in', desc='High speed side CM')
	main_shaft_length=Float(iotype='in', desc='main shaft length')
	Objective_function=Str(iotype='in')
	Optimiser=Str(iotype = 'in')
	L=Float(iotype='out')
	Mass=Float(iotype='out')
	Efficiency=Float(iotype='out')
	r_s=Float(iotype='out', desc='Optimised radius')
	l_s=Float(iotype='out', desc='Optimised generator length')
	I = Array(np.array([0.0, 0.0, 0.0]), iotype='out', desc=' moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass')
	cm = Array(np.array([0.0, 0.0, 0.0]), iotype='out', desc=' Center of mass [x, y,z]')
	PMSG_r_s= Float(iotype='in', units='m', desc='Air gap radius of a permanent magnet excited synchronous generator')
	PMSG_l_s= Float(iotype='in', units='m', desc='Core length of the permanent magnet excited synchronous generator')
	PMSG_h_s = Float(iotype='in', units='m', desc='Stator Slot height of the permanent magnet excited synchronous generator')
	PMSG_tau_p = Float(iotype='in', units='m', desc='Pole pitch of the permanent magnet excited synchronous generator')
	PMSG_h_m = Float(iotype='in', units='m', desc='Magnet height of the permanent magnet excited synchronous generator')
	PMSG_h_ys = Float(iotype='in', units='m', desc='Stator yoke height of the permanent magnet excited synchronous generator')
	PMSG_h_yr = Float(iotype='in', units='m', desc='Rotor yoke height of the permanent magnet excited synchronous generator')
	PMSG_n_s = Float(iotype='in', units='m', desc='Stator Spokes of the permanent magnet excited synchronous generator')
	PMSG_b_st = Float(iotype='in', units='m', desc='Circumferential arm dimension of stator spoke')
	PMSG_d_s= Float(0.0, iotype='in', desc='Stator arm depth ')
	PMSG_t_d =Float(0.0, iotype='in', desc='Rotor disc thickness')
	PMSG_t_ws =Float(0.0, iotype='in', desc='Stator arm thickness')
	PMSG_R_o =Float(0.0, iotype='in', desc='Main shaft radius')
	Stator_radial=Float(0.01, iotype='out', desc='Rotor radial deflection')
 	Stator_axial=Float(0.01, iotype='out', desc='Stator Axial deflection')
 	Stator_circum=Float(0.01, iotype='out', desc='Rotor radial deflection')
 	Rotor_radial=Float(0.01, iotype='out', desc='Generator efficiency')
 	Rotor_axial=Float(0.01, iotype='out', desc='Rotor Axial deflection')
 	Rotor_circum=Float(0.01, iotype='out', desc='Rotor circumferential deflection')
  
	
	def __init__(self,Optimiser='',Objective_function=''):
		
		super(Drive_PMSG,self).__init__()
		self.Optimiser=Optimiser
		self.Objective_function=Objective_function
		""" Creates a new Assembly containing PMSG and an optimizer"""
		self.add('PMSG',PMSG())
		self.connect('PMSG_r_s','PMSG.r_s')
		self.connect('PMSG_l_s','PMSG.l_s')
		self.connect('PMSG_h_s','PMSG.h_s')
		self.connect('PMSG_tau_p','PMSG.tau_p')
		self.connect('PMSG_h_m','PMSG.h_m')
		self.connect('PMSG_h_ys','PMSG.h_ys')
		self.connect('PMSG_h_yr','PMSG.h_yr')
		self.connect('PMSG_n_s','PMSG.n_s')
		self.connect('PMSG_b_st','PMSG.b_st')
		self.connect('PMSG_d_s','PMSG.d_s')
		self.connect('PMSG_t_ws','PMSG.t_ws')
		self.connect('PMSG_t_d','PMSG.t_d')
		self.connect('PMSG_R_o','PMSG.R_o')
		self.connect('P_rated','PMSG.machine_rating')
		self.connect('N','PMSG.n_nom')
		self.connect('main_shaft_cm','PMSG.main_shaft_cm')
		self.connect('main_shaft_length','PMSG.main_shaft_length')
		self.connect('T_rated','PMSG.Torque')
		self.connect('PMSG.M_actual','Mass')
		self.connect('PMSG.gen_eff','Efficiency')
		self.connect('PMSG.r_s','r_s')
		self.connect('PMSG.l_s','l_s')
		self.connect('PMSG.I','I')
		self.connect('PMSG.cm','cm')
		
		
		Opt1=globals()[self.Optimiser]
		self.add('driver',Opt1())
		self.driver.iprint = 1 
		if (Opt1=='CONMINdriver'):
			#Create Optimizer instance
			self.driver.itmax = 100
			self.driver.fdch = 0.01
			self.driver.fdchm = 0.01
			self.driver.ctlmin = 0.01
			self.driver.delfun = 0.001
			self.driver.conmin_diff = True
		elif (Opt1=='COBYLAdriver'):
			# COBYLA-specific Settings
			self.driver.rhobeg=1.0
			self.driver.rhoend = 1.0e-4
			self.driver.maxfun = 1000
		elif (Opt1=='SLSQPdriver'):
			# SLSQP-specific Settings
			self.driver.accuracy = 1.0e-6
			self.driver.maxiter = 50
		elif (Opt1=='Genetic'):
			# Genetic-specific Settings
			self.driver.population_size = 90
			self.driver.crossover_rate = 0.9
			self.driver.mutation_rate = 0.02
			self.selection_method = 'rank'
		else:
			# NEWSUMT-specific Settings
			self.driver.itmax = 10 
		
			
		Obj1='PMSG'+'.'+self.Objective_function
		self.driver.add_objective(Obj1)
		self.driver.design_vars=['PMSG_r_s','PMSG_l_s','PMSG_h_s','PMSG_tau_p','PMSG_h_m','PMSG_h_ys','PMSG_h_yr','PMSG_n_s','PMSG_b_st','PMSG_d_s','PMSG_t_d','PMSG_t_ws']
		self.driver.add_parameter('PMSG_r_s', low=0.5, high=9)
		self.driver.add_parameter('PMSG_l_s', low=0.5, high=2.5)
		self.driver.add_parameter('PMSG_h_s', low=0.04, high=0.1)
		self.driver.add_parameter('PMSG_tau_p', low=0.04, high=0.1)
		self.driver.add_parameter('PMSG_h_m', low=0.005, high=0.1)
		self.driver.add_parameter('PMSG_h_yr', low=0.045, high=0.25)
		self.driver.add_parameter('PMSG_h_ys', low=0.045, high=0.25)
		self.driver.add_parameter('PMSG_t_d', low=0.1, high=0.25)
		self.driver.add_parameter('PMSG_n_s', low=5., high=15.)
		self.driver.add_parameter('PMSG_b_st', low=0.1, high=1.5)
		self.driver.add_parameter('PMSG_d_s', low=0.1, high=1.5)
		self.driver.add_parameter('PMSG_t_ws', low=0.001, high=0.2)
		
		self.driver.add_constraint('PMSG.B_symax<2')										  #1
		self.driver.add_constraint('PMSG.B_rymax<2')										  #2
		self.driver.add_constraint('PMSG.B_tmax<2')									      #3
		self.driver.add_constraint('PMSG.B_smax<PMSG.B_g') 								#4
		self.driver.add_constraint('PMSG.B_g>=0.7')  											#5                
		self.driver.add_constraint('PMSG.B_g<=1.2') 											#6
		self.driver.add_constraint('PMSG.E_p>=500')											  #7
		self.driver.add_constraint('PMSG.E_p<=5000')											#8
		self.driver.add_constraint('PMSG.u_As<PMSG.u_all_s')							#9
		self.driver.add_constraint('PMSG.z_A_s<PMSG.z_all_s')							#10
		self.driver.add_constraint('PMSG.y_As<PMSG.y_all')  							#11
		self.driver.add_constraint('PMSG.u_Ar<PMSG.u_all_r')							#12
		self.driver.add_constraint('PMSG.y_Ar<PMSG.y_all') 								#13
		self.driver.add_constraint('PMSG.TC1<PMSG.TC2')    								#14
		self.driver.add_constraint('PMSG.TC1<PMSG.TC3')    								#15
		self.driver.add_constraint('PMSG.b_st<PMSG.b_all_s')							#16
		self.driver.add_constraint('PMSG.A_1<60000')											#17
		self.driver.add_constraint('PMSG.J_s<=6') 												#18
		self.driver.add_constraint('PMSG.A_Cuscalc>=5') 									#19
		self.driver.add_constraint('PMSG.K_rad>0.2')											#20
		self.driver.add_constraint('PMSG.K_rad<=0.27')										#21 
		self.driver.add_constraint('PMSG.Slot_aspect_ratio>=4')						#22
		self.driver.add_constraint('PMSG.Slot_aspect_ratio<=10')					#23	
		self.driver.add_constraint('PMSG.gen_eff>=Eta_target')			#24
		
				
def optim_PMSG():
	opt_problem = Drive_PMSG('CONMINdriver','Costs')
#	# Initial design variables for a DD PMSG designed for a 5MW turbine
	opt_problem.Eta_target = 93
	# Initial design variables for a DD PMSG designed for a 1.5MW turbine
	opt_problem.P_rated=5.0e6
	opt_problem.T_rated=4143289.841
	opt_problem.N=12.1
	opt_problem.PMSG_r_s=3.49              
	opt_problem.PMSG_l_s= 1.5
	opt_problem.PMSG_h_s = 0.06
	opt_problem.PMSG_tau_p = 0.07
	opt_problem.PMSG_h_m = 0.0105
	opt_problem.PMSG_h_ys = 0.085
	opt_problem.PMSG_h_yr = 0.055
	opt_problem.PMSG_n_s = 5
	opt_problem.PMSG_b_st = 0.45
	opt_problem.PMSG_t_d = 0.105
	opt_problem.PMSG_d_s= 0.32
	opt_problem.PMSG_t_ws =0.15
	opt_problem.PMSG_R_o =0.43
	opt_problem.run()
#	
	
#	opt_problem.Eta_target = 93
##	# Initial design variables for a DD PMSG designed for a 1.5MW turbine
#	opt_problem.P_rated=0.75e6
#	opt_problem.T_rated=250418.6168            # 0.75MW:250418.6168   ;1.5MW: 698729.0185; 3MW: 1.7904931e6
#	opt_problem.N=28.6
#	opt_problem.PMSG_r_s=1.4             
#	opt_problem.PMSG_l_s= 0.7
#	opt_problem.PMSG_h_s = 0.040
#	opt_problem.PMSG_tau_p = 0.06
#	opt_problem.PMSG_h_m = 0.007
#	opt_problem.PMSG_h_ys = 0.050
#	opt_problem.PMSG_h_yr = 0.045
#	opt_problem.PMSG_n_s = 5
#	opt_problem.PMSG_b_st = 0.2
#	opt_problem.PMSG_t_d = 0.1
#	opt_problem.PMSG_d_s=0.170
#	opt_problem.PMSG_t_ws =0.03
#	opt_problem.PMSG_R_o =0.17625 								# 1.5MW: 0.2775; 3MW: 0.363882632; 10 MW:0.523950817
#	opt_problem.run()
	raw_data = {'Parameters': ['Rating','Stator Arms', 'Stator Axial arm dimension','Stator Circumferential arm dimension',' Stator arm Thickness' ,'Rotor disc Thickness',' Stator Radial deflection', 'Stator Axial deflection','Stator circum deflection',' Rotor Radial deflection', 'Rotor Axial deflection','Air gap diameter','Overall Outer diameter', 'Stator length', 'l/d ratio','Slot_aspect_ratio','Pole pitch', 'Stator slot height','Stator slotwidth','Stator tooth width', 'Stator yoke height', 'Rotor yoke height', 'Magnet height', 'Magnet width', 'Peak air gap flux density fundamental','Peak stator yoke flux density','Peak rotor yoke flux density','Flux density above magnet','Maximum Stator flux density','Maximum tooth flux density','Pole pairs', 'Generator output frequency', 'Generator output phase voltage', 'Generator Output phase current', 'Stator resistance','Synchronous inductance', 'Stator slots','Stator turns','Conductor cross-section','Stator Current density ','Specific current loading','Generator Efficiency ','Iron mass','Magnet mass','Copper mass','Mass of Arms and disc', 'Total Mass', 'Stator Mass','Rotor Mass','Total Material Cost'],
			'Values': [opt_problem.PMSG.P_gennom/1000000,opt_problem.PMSG.n_s,opt_problem.PMSG.d_s*1000,opt_problem.PMSG.b_st*1000,opt_problem.PMSG.t_ws*1000,opt_problem.PMSG.t_d*1000,opt_problem.PMSG.Stator_radial*1000,opt_problem.PMSG.Stator_axial*1000,opt_problem.PMSG.Stator_circum*1000,opt_problem.PMSG.Rotor_radial*1000,opt_problem.PMSG.Rotor_axial*1000,2*opt_problem.PMSG.r_s,opt_problem.PMSG.R_out*2,opt_problem.PMSG.l_s,opt_problem.PMSG.K_rad,opt_problem.PMSG.Slot_aspect_ratio,opt_problem.PMSG.tau_p*1000,opt_problem.PMSG.h_s*1000,opt_problem.PMSG.b_s*1000,opt_problem.PMSG.b_t*1000,opt_problem.PMSG.t_s*1000,opt_problem.PMSG.t*1000,opt_problem.PMSG.h_m*1000,opt_problem.PMSG.b_m*1000,opt_problem.PMSG.B_g,opt_problem.PMSG.B_symax,opt_problem.PMSG.B_rymax,opt_problem.PMSG.B_pm1,opt_problem.PMSG.B_smax,opt_problem.PMSG.B_tmax,opt_problem.PMSG.p,opt_problem.PMSG.f,opt_problem.PMSG.E_p,opt_problem.PMSG.I_s,opt_problem.PMSG.R_s,opt_problem.PMSG.L_s,opt_problem.PMSG.S,opt_problem.PMSG.W_1a,opt_problem.PMSG.A_Cuscalc,opt_problem.PMSG.J_s,opt_problem.PMSG.A_1/1000,opt_problem.PMSG.gen_eff,opt_problem.PMSG.Iron/1000,opt_problem.PMSG.mass_PM/1000,opt_problem.PMSG.M_Cus/1000,opt_problem.PMSG.Inactive/1000,opt_problem.PMSG.M_actual/1000,opt_problem.PMSG.Stator/1000,opt_problem.PMSG.Rotor/1000,opt_problem.PMSG.Costs/1000],
				'Limit': ['','','',opt_problem.PMSG.b_all_s*1000,'','',opt_problem.PMSG.u_all_s*1000,opt_problem.PMSG.y_all*1000,opt_problem.PMSG.z_all_s*1000,opt_problem.PMSG.u_all_r*1000,opt_problem.PMSG.y_all*1000,'','','','(0.2-0.27)','(4-10)','','','','','','','','','<2','<2','<2','<2','<2',opt_problem.PMSG.B_g,'<2','','','>500','','','','','5','3-6','60','>93%','','','','','','','',''],
				'Units':['MW','unit','mm','mm','mm','','mm','mm','mm','mm','mm','m','m','m','','','mm','mm','mm','mm','mm','mm','mm','mm','T','T','T','T','T','T','-','Hz','V','A','ohm/phase','','A/mm^2','slots','turns','mm^2','kA/m','%','tons','tons','tons','tons','tons','tons','tons','k$']}
	df=pd.DataFrame(raw_data, columns=['Parameters','Values','Limit','Units'])
	print df
	df.to_excel('PMSG_'+str(opt_problem.P_rated/1e6)+'_discRotor_MW.xlsx')


		
if __name__=="__main__":
	optim_PMSG()