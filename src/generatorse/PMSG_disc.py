"""PMSG_disc.py
Created by Latha Sethuraman, Katherine Dykes. 
Copyright (c) NREL. All rights reserved.
Electromagnetic design based on conventional magnetic circuit laws
Structural design based on McDonald's thesis """

from openmdao.main.api import Component,Assembly
from openmdao.lib.datatypes.api import Float,Array,Str
import numpy as np
from numpy import array, float,min
from math import pi, cos, sqrt, radians, sin,cosh,sinh, exp, log10, log, tan, atan
from openmdao.lib.drivers.api import COBYLAdriver, CONMINdriver,NEWSUMTdriver,SLSQPdriver,Genetic
import pandas as pd


class PMSG(Component):
	
	""" Estimates overall mass dimensions and Efficiency of PMSG -disc rotor generator. """
	
	# PMSG_disc generator design inputs
	
	r_s = Float(iotype='in', desc='airgap radius r_s')
	l_s = Float(iotype='in', desc='Stator core length l_s')
	h_s = Float(iotype='in', desc='Yoke height h_s')
	tau_p =Float(iotype='in', desc='Pole pitch self.tau_p')
	B_g = Float(iotype='out', desc='Peak air gap flux density B_g')
	machine_rating=Float(iotype='in', desc='Machine rating')
	n_nom=Float(iotype='in', desc='rated speed')
	Torque=Float(iotype='in', desc='Rated torque ')
	h_m=Float(iotype='in', desc='magnet height')
	h_ys=Float(iotype='in', desc='Yoke height')
	h_yr=Float(iotype='in', desc='rotor yoke height')
	
	# structural design variables
	n_s =Float(iotype='in', desc='number of stator arms n_s')
	b_st = Float(iotype='in', desc='arm width b_r')
	d_s= Float(iotype='in', desc='arm depth d_r')
	t_ws =Float(iotype='in', desc='arm depth thickness self.t_wr')
	t= Float(0.0, iotype='in', desc='rotor back iron')
	t_s= Float(0.0, iotype='in', desc='stator back iron t')
	t_d = Float(0.0, iotype='in', desc='disc thickness')
	R_o=Float(iotype='in', desc='Shaft radius')
	
	# PMSG_disc generator design outputs
	# Magnetic loading
	B_symax = Float(iotype='out', desc='Peak Stator Yoke flux density B_ymax')
	B_tmax=Float(iotype='out', desc='Peak Teeth flux density')
	B_rymax=Float(iotype='out', desc='Peak Rotor yoke flux density')
	B_smax=Float(iotype='out', desc='Peak Stator flux density')
	B_pm1=Float(iotype='out', desc='Fundamental component of peak air gap flux density')
	B_g = Float(iotype='out', desc='Peak air gap flux density B_g')
	
	#Stator design
	N_s =Float(iotype='out', desc='Number of turns in the stator winding')
	b_s=Float(iotype='out', desc='slot width')
	b_t=Float(iotype='out', desc='tooth width')
	A_Cuscalc=Float(iotype='out', desc='Conductor cross-section mm^2')
	
	#Rotor magnet dimension
	b_m=Float(iotype='out', desc='magnet width')
	p=Float(iotype='out', desc='No of pole pairs')
	
	# Electrical performance
	E_p=Float(iotype='out', desc='Stator phase voltage')
	f=Float(iotype='out', desc='Generator output frequency')
	I_s=Float(iotype='out', desc='Generator output phase current')
	R_s=Float(iotype='out', desc='Stator resistance')
	L_s=Float(iotype='out', desc='Stator synchronising inductance')
	A_1 =Float(0,iotype='out', desc='Electrical loading')
	J_s=Float(iotype='out', desc='Current density')

	# Objective functions
	Mass=Float(iotype='out', desc='Actual mass')
	K_rad=Float(iotype='out', desc='K_rad')
	Losses=Float(iotype='out', desc='Total loss')
	gen_eff=Float(iotype='out', desc='Generator efficiency')
	
	# Structural performance
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
	
	# Other parameters
	R_out=Float(iotype='out', desc='Outer radius')
	S			=Float(iotype='out', desc='Stator slots')
	Slot_aspect_ratio=Float(iotype='out', desc='Slot aspect ratio')
	
	#inputs/outputs for interface with drivese
	main_shaft_cm = Array(np.array([0.0, 0.0, 0.0]),iotype='in', desc='Main Shaft CM')
	main_shaft_length=Float(iotype='in', desc='main shaft length')
	cm=Array(np.array([0.0, 0.0, 0.0]),iotype='out', desc='COM [x,y,z]')
	I=Array(np.array([0.0, 0.0, 0.0]),iotype='out', desc='Moments of Inertia for the component [Ixx, Iyy, Izz] around its center of mass')
	
	# Mass Outputs
	mass_PM=Float(iotype='out', desc='Magnet mass')
	Copper		=Float(iotype='out', desc='Copper Mass')
	Iron	=Float(iotype='out', desc='Electrical Steel Mass')
	Structural_mass	=Float(iotype='out', desc='Structural Mass')
	
	# Material properties
	rho_Fes=Float(iotype='in', desc='Structural Steel density kg/m^3')
	rho_Fe=Float(iotype='in', desc='Magnetic Steel density kg/m^3')
	rho_Copper=Float(iotype='in', desc='Copper density kg/m^3')
	rho_PM=Float(iotype='in', desc='Magnet density kg/m^3')
	
	def execute(self):
		
		
		r_s = self.r_s
		l_s = self.l_s
		h_s = self.h_s
		tau_p =self.tau_p
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
		
		Mass=self.Mass
		gen_eff =self.gen_eff
		Losses=self.Losses
		A_1=self.A_1
		K_rad=self.K_rad
		N_s=self.N_s
		S=self.S
		
		Iron=self.Iron
		Copper=self.Copper
		Structural_mass=self.Structural_mass
		mass_PM=self.mass_PM
		
		u_As=self.u_As
		u_Ar=self.u_Ar
		y_As=self.y_As
		y_Ar=self.y_Ar
		z_A_s=self.z_A_s
		z_all_s=self.z_all_s
		z_all_r=self.z_all_r
		b_all_r=self.b_all_r
		b_all_s=self.b_all_s
		TC1	=self.TC1
		TC2=self.TC2
		TC3=self.TC3
		R_o=self.R_o
		
		
		R_out=self.R_out
		B_pm1=self.B_pm1
		B_tmax= self.B_tmax
		B_symax=self.B_symax
		B_rymax=self.B_rymax
		B_smax=self.B_smax
		B_g = self.B_g
		A_Cuscalc=self.A_Cuscalc
		
		machine_rating=self.machine_rating
		Slot_aspect_ratio=self.Slot_aspect_ratio
		Torque=self.Torque
		main_shaft_cm = self.main_shaft_cm
		main_shaft_length=self.main_shaft_length
		cm=self.cm
		I=self.I
		
		rho_Fe= self.rho_Fe
		rho_Fes=self.rho_Fes
		rho_Copper=self.rho_Copper
		rho_PM=self.rho_PM
		
		#Assign values to universal constants
		
		B_r    =1.2                 # Tesla remnant flux density
		g1      =9.81               # m/s^2 acceleration due to gravity
		E      =2e11                # N/m^2 young's modulus
		sigma  =40e3                # shear stress assumed
		ratio  =0.7                 # ratio of magnet width to pole pitch(bm/self.tau_p)
		mu_0   =pi*4e-7             # permeability of free space
		mu_r   =1.06								# relative permeability
		phi    =90*2*pi/360         # tilt angle (rotor tilt -90 degrees during transportation)
		cofi   =0.85                # power factor
		
		#Assign values to design constants
		h_w    =0.005										# wedge height
		y_tau_p=1												# coiil span to pole pitch
		m      =3                    # no of phases
		q1     =1                    # no of slots per pole per phase
		b_s_tau_s=0.45							 # slot width/slot pitch ratio
		k_sfil =0.65								 # Slot fill factor
		P_Fe0h =4			               #specific hysteresis losses W/kg @ 1.5 T 
		P_Fe0e =1			               #specific hysteresis losses W/kg @ 1.5 T 
		rho_Cu=1.8*10**(-8)*1.4      # resistivity of copper
		b_so			=  0.004					 #stator slot opening
		k_fes =0.9									#useful iron stack length
		T =   self.Torque
		v=0.3                        # poisson's ratio
		
		# back iron thickness for rotor and stator
		self.t_s =self.h_ys    
		self.t =self.h_yr
		
		# Aspect ratio
		self.K_rad=self.l_s/(2*self.r_s) # aspect ratio
		
		###################################################### Electromagnetic design#############################################
		
		dia				=  2*self.r_s              # air gap diameter
		g         =  0.001*dia							 # air gap length
		self.b_m  =0.7*self.tau_p							# magnet width
		l_u       =k_fes * self.l_s                   #useful iron stack length
		We				=self.tau_p
		l_b       = 2*self.tau_p  										#end winding length
		l_e       =self.l_s+2*0.001*self.r_s     			# equivalent core length
		r_r				=  self.r_s-g                       #rotor radius
		self.p		=  round(pi*dia/(2*self.tau_p))			# pole pairs
		self.f    =  self.n_nom*self.p/60							# frequency
		self.S				= 2*self.p*q1*m 								# Stator slots
		N_conductors=self.S*2
		self.N_s=N_conductors/2/3											# Stator turns per phase
		tau_s=pi*dia/self.S														# slot pitch
		self.b_s	=  b_s_tau_s*tau_s    							#slot width
		self.b_t	=  tau_s-(self.b_s)          				#tooth width
		self.Slot_aspect_ratio=self.h_s/self.b_s
		alpha_p		=  pi/2*0.7
		
		# Calculating Carter factor for statorand effective air gap length
		gamma			=  4/pi*(b_so/2/(g+self.h_m/mu_r)*atan(b_so/2/(g+self.h_m/mu_r))-log(sqrt(1+(b_so/2/(g+self.h_m/mu_r))**2)))
		k_C				=  tau_s/(tau_s-gamma*(g+self.h_m/mu_r))   # carter coefficient
		g_eff			=  k_C*(g+self.h_m/mu_r)
		
		# angular frequency in radians
		om_m			=  2*pi*self.n_nom/60
		om_e			=  self.p*om_m/2
		
		# Calculating magnetic loading
		self.B_pm1	 		=  B_r*self.h_m/mu_r/(g_eff)
		self.B_g=  B_r*self.h_m/mu_r/(g_eff)*(4/pi)*sin(alpha_p)
		self.B_symax=self.B_g*self.b_m*l_e/(2*self.h_ys*l_u)
		self.B_rymax=self.B_g*self.b_m*l_e/(2*self.h_yr*self.l_s)
		self.B_tmax	=self.B_g*tau_s/self.b_t
		
		
		k_wd			= sin(pi/6)/q1/sin(pi/6/q1)      # winding factor
		L_t=self.l_s+2*self.tau_p
		
		# Stator winding length ,cross-section and resistance
		l_Cus			= 2*(self.N_s)*(2*self.tau_p+L_t)
		A_s				= self.b_s*(self.h_s-h_w)*q1*self.p
		A_scalc   = self.b_s*1000*(self.h_s*1000-h_w*1000)*q1*self.p
		A_Cus			= A_s*k_sfil/(self.N_s)
		self.A_Cuscalc = A_scalc *k_sfil/(self.N_s)
		self.R_s	= l_Cus*rho_Cu/A_Cus
		
		# Calculating leakage inductance in  stator
		L_m				= 2*m*k_wd**2*(self.N_s)**2*mu_0*self.tau_p*L_t/pi**2/g_eff/self.p
		L_ssigmas=2*mu_0*self.l_s*self.N_s**2/self.p/q1*((self.h_s-h_w)/(3*self.b_s)+h_w/b_so)  #slot leakage inductance
		L_ssigmaew=(2*mu_0*self.l_s*self.N_s**2/self.p/q1)*0.34*g*(l_e-0.64*self.tau_p*y_tau_p)/self.l_s #end winding leakage inductance
		L_ssigmag=2*mu_0*self.l_s*self.N_s**2/self.p/q1*(5*(g*k_C/b_so)/(5+4*(g*k_C/b_so))) # tooth tip leakage inductance#tooth tip leakage inductance
		L_ssigma	= (L_ssigmas+L_ssigmaew+L_ssigmag)
		self.L_s  = L_m+L_ssigma
		
		# Calculating no-load voltage induced in the stator and stator current
		self.E_p	= 2*(self.N_s)*L_t*self.r_s*k_wd*om_m*self.B_g/sqrt(2)
		
		Z=(self.machine_rating/(m*self.E_p))
		G=(self.E_p**2-(om_e*self.L_s*Z)**2)
		self.I_s= sqrt(Z**2+(((self.E_p-G**0.5)/(om_e*self.L_s)**2)**2))
		self.B_smax=sqrt(2)*self.I_s*mu_0/g_eff
		
		# Calculating stator current and electrical loading
		self.J_s	= self.I_s/self.A_Cuscalc
		I_snom		=(self.machine_rating/m/self.E_p/cofi) #rated current
		I_qnom		=self.machine_rating/(m*self.E_p)
		X_snom		=om_e*(L_m+L_ssigma)
		self.A_1 = 6*self.N_s*self.I_s/(pi*dia)
		
		#Calculating electromagnetically active mass
		
		V_Cus 	=m*l_Cus*A_Cus     # copper volume
		V_Fest	=L_t*2*self.p*q1*m*self.b_t*self.h_s   # volume of iron in stator tooth
		V_Fesy	=L_t*pi*((self.r_s+self.h_s+self.h_ys)**2-(self.r_s+self.h_s)**2) # volume of iron in stator yoke
		V_Fery	=L_t*pi*((r_r-self.h_m)**2-(r_r-self.h_m-self.h_yr)**2) # volume of iron in rotor yoke
		self.Copper		=V_Cus*self.rho_Copper  
		M_Fest	=V_Fest*self.rho_Fe               # mass of stator tooth
		M_Fesy	=V_Fesy*self.rho_Fe								# mass of stator yoke
		M_Fery	=V_Fery*self.rho_Fe								# mass of rotor yoke
		self.Iron		=M_Fest+M_Fesy+M_Fery
		
		#Calculating losses"
		#1.Copper losses
		K_R=1.2                                   # Skin effect correction co-efficient
		P_Cu		=m*I_snom**2*self.R_s*K_R
		
		# Iron Losses ( from Hysteresis and eddy currents)
		P_Hyys	=M_Fesy*(self.B_symax/1.5)**2*(P_Fe0h*om_e/(2*pi*60)) # Hysteresis losses in stator yoke
		P_Ftys	=M_Fesy*((self.B_symax/1.5)**2)*(P_Fe0e*(om_e/(2*pi*60))**2)# Eddy losses in stator yoke
		P_Fesynom=P_Hyys+P_Ftys
		P_Hyd=M_Fest*(self.B_tmax/1.5)**2*(P_Fe0h*om_e/(2*pi*60)) # Hysteresis losses in stator teeth
		P_Ftd=M_Fest*(self.B_tmax/1.5)**2*(P_Fe0e*(om_e/(2*pi*60))**2) # Eddy losses in stator teeth
		P_Festnom=P_Hyd+P_Ftd
		P_ad=0.2*(P_Hyys + P_Ftys + P_Hyd + P_Ftd ) # additional stray losses due to leakage flux
		pFtm =300 																	# specific magnet loss
		P_Ftm=pFtm*2*self.p*self.b_m*self.l_s					#magnet losses
		
		self.Losses=P_Cu+P_Festnom+P_Fesynom+P_ad+P_Ftm
		self.gen_eff=self.machine_rating*100/(self.machine_rating+self.Losses)
		
		################################################## Structural  Design ############################################################
		
		## Structural deflection calculations
		#rotor structure
		R					= self.r_s-g-self.h_m-0.5*self.t   # mean radius of the rotor rim
		l=L_t
		b					=self.R_o													 # Shaft radius
		R_b				=R-0.5*self.t											# Inner radius of the rotor
		R_a=R+0.5*self.h_yr													# Outer radius of rotor yoke
		a=R-0.5*self.t;
		a_1=R_b
		c					=R/500
		self.u_all_r    =c/20  																			# allowable radial deflection
		self.y_all    =2*l/100    																	# allowable axial deflection
		R_1				= R-self.t*0.5      															#inner radius of rotor cylinder
		K					=4*(sin(ratio*pi/2))/pi
		q3					= self.B_g**2/2/mu_0   													# normal component of Maxwell's stress
		
		self.mass_PM   =(2*pi*(R+0.5*self.t)*l*self.h_m*ratio*self.rho_PM)           # magnet mass
		mass_st_lam=self.rho_Fe*2*pi*R*l*self.h_yr                                     # mass of rotor yoke steel
		
		
		# Calculation of radial deflection of rotor
		# cylindrical shell function and circular plate parameters for disc rotor based on Table 11.2 Roark's formulas
		lamb   =((3*(1-v**2)/R_a**2/self.h_yr**2)**0.25)
		x1=lamb*l
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
		
		# Radial deflection analytical model from McDonald's thesis defined in parts
		Part_1 =R_b*((1-v)*R_b**2+(1+v)*self.R_o**2)/(R_b**2-self.R_o**2)/E
		Part_2 =(C_2*C_a2-2*C_3*C_a1)/2/C_11
		Part_3 = (C_3*C_a2-C_4*C_a1)/C_11
		Part_4 =((0.25/D_r/lamb**3))
		Part_5=q3*R_b**2/(E*(R_a-R_b))
		f_d = Part_5/(Part_1-self.t_d*(Part_4*Part_2*F_2_ls2-Part_3*2*Part_4*F_1_ls2-Part_4*F_a4_ls2))
		fr=f_d*self.t_d
		self.u_Ar				=abs(Part_5+fr/2/D_r/lamb**3*((-F_1_x0/C_11)*(C_3*C_a2-C_4*C_a1)+(F_2_x0/2/C_11)*(C_2*C_a2-2*C_3*C_a1)-F_a4_x0/2))
		
		# Calculation of Axial deflection of rotor
		W=0.5*g1*sin(phi)*((l-self.t_d)*self.h_yr*self.rho_Fes)        # uniform annular line load acting on rotor cylinder assumed as an annular plate 
		w=self.rho_Fes*g1*sin(phi)*self.t_d	                           # disc assumed as plate with a uniformly distributed pressure between
		a_i=self.R_o
		
		# Flat circular plate constants according to Roark's table 11.2
		C_2p= 0.25*(1-(((self.R_o/R)**2)*(1+(2*log(R/self.R_o)))))
		C_3p=(self.R_o/4/R)*((1+(self.R_o/R)**2)*log(R/self.R_o)+(self.R_o/R)**2-1)
		C_6= (self.R_o/4/R_a)*((self.R_o/R_a)**2-1+2*log(R_a/self.R_o))
		C_5=0.5*(1-(self.R_o/R)**2)
		C_8= 0.5*(1+v+(1-v)*((self.R_o/R)**2))
		C_9=(self.R_o/R)*(0.5*(1+v)*log(R/self.R_o) + (1-v)/4*(1-(self.R_o/R)**2))
		
		# Flat circular plate loading constants
		L_11=(1 + 4*(self.R_o/a_1)**2 - 5*(self.R_o/a_1)**4 - 4*((self.R_o/a_1)**2)*log(a_1/self.R_o)*(2+(self.R_o/a_1)**2))/64
		L_14=(1/16)*(1-(self.R_o/R_b)**4-4*(self.R_o/R_b)**2*log(R_b/self.R_o))
		y_ai=-W*(a_1**3)*(C_2p*(C_6*a_1/self.R_o - C_6)/C_5 - a_1*C_3p/self.R_o +C_3p)/D_ax  # Axial deflection of plate due to The deflection of an annular plate with a uniform annular line load
		
		# Axial Deflection due to uniformaly distributed pressure load
		M_rb=-w*R**2*(C_6*(R**2-self.R_o**2)*0.5/R/self.R_o-L_14)/C_5
		Q_b=w*0.5*(R**2-self.R_o**2)/self.R_o
		y_aii=M_rb*R_a**2*C_2p/D_ax+Q_b*R_a**3*C_3p/D_ax-w*R_a**4*L_11/D_ax
		
		self.y_Ar=abs(y_ai+y_aii)
		
		self.z_all_r=0.05*2*pi*R/360  # allowable torsional deflection of rotor
		
				
		#stator structure deflection calculation
		
		self.R_out=(R/0.995+self.h_s+self.h_ys)
		a_s       = (self.b_st*self.d_s)-((self.b_st-2*self.t_ws)*(self.d_s-2*self.t_ws)) # cross-sectional area of stator armms
		A_st      =l*self.t_s                     # cross-sectional area of rotor cylinder
		N_st			= round(self.n_s)
		theta_s		=pi*1/N_st  # half angle between spokes
		I_st       =l*self.t_s**3/12                      # second moment of area of stator cylinder
		I_arm_axi_s	=((self.b_st*self.d_s**3)-((self.b_st-2*self.t_ws)*(self.d_s-2*self.t_ws)**3))/12  # second moment of area of stator arm
		I_arm_tor_s	= ((self.d_s*self.b_st**3)-((self.d_s-2*self.t_ws)*(self.b_st-2*self.t_ws)**3))/12  # second moment of area of rotot arm w.r.t torsion
		R_st 			=self.r_s+self.h_s+self.h_ys*0.5
		k_2       = sqrt(I_st/A_st)  # radius of gyration
		self.b_all_s		=2*pi*self.R_o/N_st
		m2        =(k_2/R_st)**2
		c1        =R_st/500
		R_1s      = R_st-self.t_s*0.5
		d_se=dia+2*(self.h_ys+self.h_s+h_w)  # stator outer diameter
		
		# Calculation of radial deflection of stator
		Numers=R_st**3*((0.25*(sin(theta_s)-(theta_s*cos(theta_s)))/(sin(theta_s))**2)-(0.5/sin(theta_s))+(0.5/theta_s))
		Povs=((theta_s/(sin(theta_s))**2)+1/tan(theta_s))*((0.25*R_st/A_st)+(0.25*R_st**3/I_st))
		Qovs=R_st**3/(2*I_st*theta_s*(m2+1))
		Lovs=(R_1s-self.R_o)*0.5/a_s
		Denoms=I_st*(Povs-Qovs+Lovs)
		
		self.u_As				=(q3*R_st**2/E/self.t_s)*(1+Numers/Denoms)
		
		# Calculation of axial deflection of stator
		mass_st_lam_s= M_Fest+pi*l*self.rho_Fe*((R_st+0.5*self.h_ys)**2-(R_st-0.5*self.h_ys)**2)
		W_is			=0.5*g1*sin(phi)*(self.rho_Fes*l*self.d_s**2)                          # length of stator arm beam at which self-weight acts
		W_iis     =g1*sin(phi)*(mass_st_lam_s+V_Cus*self.rho_Copper)/2/N_st							 # weight of stator cylinder and teeth
		w_s         =self.rho_Fes*g1*sin(phi)*a_s*N_st																	 # uniformly distributed load of the arms
		
		l_is      =R_st-self.R_o																													# distance at which the weight of the stator cylinder acts
		l_iis     =l_is																																		# distance at which the weight of the stator cylinder acts
		l_iiis    =l_is																																		# distance at which the weight of the stator cylinder acts
		self.u_all_s    = c1/20
		
		X_comp1 = (W_is*l_is**3/12/E/I_arm_axi_s)																				# deflection component due to stator arm beam at which self-weight acts
		X_comp2 =(W_iis*l_iis**4/24/E/I_arm_axi_s)																			# deflection component due to 1/nth of stator cylinder
		X_comp3 =w_s*l_iiis**4/24/E/I_arm_axi_s																					# deflection component due to weight of arms
		
		self.y_As       =X_comp1+X_comp2+X_comp3  # axial deflection
		
		# Stator circumferential deflection
		self.z_all_s     =0.05*2*pi*R_st/360  # allowable torsional deflection
		self.z_A_s  =2*pi*(R_st+0.5*self.t_s)*l/(2*N_st)*sigma*(l_is+0.5*self.t_s)**3/3/E/I_arm_tor_s

		mass_stru_steel  =2*(N_st*(R_1s-self.R_o)*a_s*self.rho_Fes)
		
		self.TC1=T/(2*pi*sigma)     # Torque/shear stress
		self.TC2=R**2*l              # Evaluating Torque constraint for rotor
		self.TC3=R_st**2*l           # Evaluating Torque constraint for stator
		self.Structural_mass=mass_stru_steel+(pi*(R**2-R_o**2)*self.t_d*self.rho_Fes)
		self.Mass =  self.Structural_mass+self.Iron+self.Copper+self.mass_PM
		
		# Calculating mass moments of inertia and center of mass
		self.I[0]   = (0.5*self.Mass*self.R_out**2)
		self.I[1]   = (0.25*self.Mass*self.R_out**2+(1/12)*self.Mass*self.l_s**2)
		self.I[2]   = self.I[1]
		
		cm[0]  = self.main_shaft_cm[0] + self.main_shaft_length/2. + self.l_s/2
		cm[1]  = self.main_shaft_cm[1]
		cm[2]  = self.main_shaft_cm[2]

####################################################Cost Analysis#######################################################################

class PMSG_Cost(Component):
	
	""" Provides a material cost estimate for a PMSG _disc generator. Manufacturing costs are excluded"""
	# Inputs
	# Specific cost of material by type
	C_Cu=Float( iotype='in', desc='Specific cost of copper')
	C_Fe=Float(iotype='in', desc='Specific cost of magnetic steel/iron')
	C_Fes=Float(iotype='in', desc='Specific cost of structural steel')
	C_PM=Float(iotype='in', desc='Specific cost of Magnet')  
	
	# Mass of each material type
	Copper=Float(iotype='in', desc='Copper mass')
	Iron=Float(iotype='in', desc='Iron mass')
	mass_PM =Float(iotype='in', desc='Magnet mass')
	Structural_mass=Float(iotype='in', desc='Structural mass')
	# Outputs
	Costs= Float(iotype='out', desc='Total cost')
	
	def execute(self):
		Copper=self.Copper
		C_Cu=self.C_Cu
		Iron=self.Iron
		C_Fe=self.C_Fe
		C_Fes=self.C_Fes
		C_PM=self.C_PM
		Costs=self.Costs
		Structural_mass=self.Structural_mass
		
		# Material cost as a function of material mass and specific cost of material
		K_gen=self.Copper*self.C_Cu+self.Iron*self.C_Fe+self.C_PM*self.mass_PM
		Cost_str=self.C_Fes*self.Structural_mass
		self.Costs=K_gen+Cost_str
		
####################################################OPTIMISATION SET_UP ############################################################### 

class PMSG_disc_Opt(Assembly):
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

	C_Cu=Float( iotype='in', desc='Specific cost of copper')
	C_Fe=Float(iotype='in', desc='Specific cost of magnetic steel/iron')
	C_Fes=Float(iotype='in', desc='Specific cost of structural steel')
	C_PM=Float(iotype='in', desc='Specific cost of Magnet')
	
	rho_Fes=Float(iotype='in', desc='Structural Steel density kg/m^3')
	rho_Fe=Float(iotype='in', desc='Magnetic Steel density kg/m^3')
	rho_Copper=Float(iotype='in', desc='Copper density kg/m^3')
	rho_PM=Float(iotype='in', desc='Magnet density kg/m^3')
  
	
	
	def __init__(self,Optimiser='',Objective_function='',print_results=''):
		
		super(PMSG_disc_Opt,self).__init__()

		""" Creates a new Assembly containing PMSG and an optimizer"""
		
		# add PMSG component, connect i/o
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
		self.connect('PMSG.Mass','Mass')
		self.connect('PMSG.gen_eff','Efficiency')
		self.connect('PMSG.r_s','r_s')
		self.connect('PMSG.l_s','l_s')
		self.connect('PMSG.I','I')
		self.connect('PMSG.cm','cm')
		
		self.connect('rho_PM','PMSG.rho_PM')
		self.connect('rho_Fe','PMSG.rho_Fe')
		self.connect('rho_Fes','PMSG.rho_Fes')
		self.connect('rho_Copper','PMSG.rho_Copper')
		
		# add PMSG_Cost component, connect i/o
		self.add('PMSG_Cost',PMSG_Cost())
		self.connect('C_Fe','PMSG_Cost.C_Fe')
		self.connect('C_Fes','PMSG_Cost.C_Fes')
		self.connect('C_Cu','PMSG_Cost.C_Cu')
		self.connect('C_PM','PMSG_Cost.C_PM')
		self.connect('PMSG.Iron','PMSG_Cost.Iron')
		self.connect('PMSG.Copper','PMSG_Cost.Copper')
		self.connect('PMSG.mass_PM','PMSG_Cost.mass_PM')
		self.connect('PMSG.Structural_mass','PMSG_Cost.Structural_mass')
		
		# add optimizer and set-up problem (using user defined input on objective function"
		self.Optimiser=Optimiser
		self.Objective_function=Objective_function
		Opt1=globals()[self.Optimiser]
		self.add('driver',Opt1())
		self.driver.add_objective(self.Objective_function)
		self.driver.workflow.add(['PMSG','PMSG_Cost'])
		# set up design variables for the PMSG_arms generator
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
		
				
		self.driver.iprint=print_results
		
		# set up constraints for the PMSG_arms generator
		
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
		self.driver.add_constraint('PMSG.gen_eff>=Eta_target')						#24
		
				
def PMSG_disc_Opt_example():
	
	#Example optimization of a PMSG_disc rotor generator for costs on a 5 MW reference turbine
	
	opt_problem = PMSG_disc_Opt('CONMINdriver','PMSG_Cost.Costs',1)
	
	#Initial design variables for a DD PMSG designed for a 5MW turbine
	
	opt_problem.P_rated=5e6
	opt_problem.T_rated=4.143289e6
	opt_problem.Eta_target = 93
	opt_problem.N=12.1
	opt_problem.PMSG_r_s=3.49
	opt_problem.PMSG_l_s= 1.5
	opt_problem.PMSG_h_s = 0.060
	opt_problem.PMSG_tau_p = 0.07
	opt_problem.PMSG_h_m = 0.0105
	opt_problem.PMSG_h_ys = 0.085
	opt_problem.PMSG_h_yr = 0.055
	opt_problem.PMSG_n_s = 5
	opt_problem.PMSG_b_st = 0.460
	opt_problem.PMSG_t_d = 0.105
	opt_problem.PMSG_d_s= 0.350
	opt_problem.PMSG_t_ws =0.150
	opt_problem.PMSG_R_o =0.43
	
	# Specific costs
	opt_problem.C_Cu   =4.786
	opt_problem.C_Fe	= 0.556
	opt_problem.C_Fes =0.50139
	opt_problem.C_PM  =95
	
	#Material properties
	opt_problem.rho_Fe = 7700                 #Steel density
	opt_problem.rho_Fes = 7850                 #Steel density
	opt_problem.rho_Copper =8900                  # Kg/m3 copper density
	opt_problem.rho_PM =7450
	
	#Run optimization
	opt_problem.run()

	""" Uncomment to print solution to an excel file
	
	import pandas
	
	raw_data = {'Parameters': ['Rating','Stator Arms', 'Stator Axial arm dimension','Stator Circumferential arm dimension',' Stator arm Thickness' ,'Rotor disc Thickness',' Stator Radial deflection', 'Stator Axial deflection','Stator circum deflection',' Rotor Radial deflection', 'Rotor Axial deflection','Air gap diameter','Overall Outer diameter', 'Stator length', 'l/d ratio','Slot_aspect_ratio','Pole pitch', 'Stator slot height','Stator slotwidth','Stator tooth width', 'Stator yoke height', 'Rotor yoke height', 'Magnet height', 'Magnet width', 'Peak air gap flux density fundamental','Peak stator yoke flux density','Peak rotor yoke flux density','Flux density above magnet','Maximum Stator flux density','Maximum tooth flux density','Pole pairs', 'Generator output frequency', 'Generator output phase voltage', 'Generator Output phase current', 'Stator resistance','Synchronous inductance', 'Stator slots','Stator turns','Conductor cross-section','Stator Current density ','Specific current loading','Generator Efficiency ','Iron mass','Magnet mass','Copper mass','Mass of Arms and disc', 'Total Mass', 'Total Material Cost'],
			'Values': [opt_problem.P_rated/1000000,opt_problem.PMSG.n_s,opt_problem.PMSG.d_s*1000,opt_problem.PMSG.b_st*1000,opt_problem.PMSG.t_ws*1000,opt_problem.PMSG.t_d*1000,opt_problem.PMSG.u_As*1000,opt_problem.PMSG.y_As*1000,opt_problem.PMSG.z_A_s*1000,opt_problem.PMSG.u_Ar*1000,opt_problem.PMSG.y_Ar*1000,2*opt_problem.PMSG.r_s,opt_problem.PMSG.R_out*2,opt_problem.PMSG.l_s,opt_problem.PMSG.K_rad,opt_problem.PMSG.Slot_aspect_ratio,opt_problem.PMSG.tau_p*1000,opt_problem.PMSG.h_s*1000,opt_problem.PMSG.b_s*1000,opt_problem.PMSG.b_t*1000,opt_problem.PMSG.t_s*1000,opt_problem.PMSG.t*1000,opt_problem.PMSG.h_m*1000,opt_problem.PMSG.b_m*1000,opt_problem.PMSG.B_g,opt_problem.PMSG.B_symax,opt_problem.PMSG.B_rymax,opt_problem.PMSG.B_pm1,opt_problem.PMSG.B_smax,opt_problem.PMSG.B_tmax,opt_problem.PMSG.p,opt_problem.PMSG.f,opt_problem.PMSG.E_p,opt_problem.PMSG.I_s,opt_problem.PMSG.R_s,opt_problem.PMSG.L_s,opt_problem.PMSG.S,opt_problem.PMSG.N_s,opt_problem.PMSG.A_Cuscalc,opt_problem.PMSG.J_s,opt_problem.PMSG.A_1/1000,opt_problem.PMSG.gen_eff,opt_problem.PMSG.Iron/1000,opt_problem.PMSG.mass_PM/1000,opt_problem.PMSG.Copper/1000,opt_problem.PMSG.Structural_mass/1000,opt_problem.PMSG.Mass/1000,opt_problem.PMSG_Cost.Costs/1000],
				'Limit': ['','','',opt_problem.PMSG.b_all_s*1000,'','',opt_problem.PMSG.u_all_s*1000,opt_problem.PMSG.y_all*1000,opt_problem.PMSG.z_all_s*1000,opt_problem.PMSG.u_all_r*1000,opt_problem.PMSG.y_all*1000,'','','','(0.2-0.27)','(4-10)','','','','','','','','','<2','<2','<2','<2','<2',opt_problem.PMSG.B_g,'<2','','','>500','','','','','5','3-6','60','>93%','','','','','',''],
				'Units':['MW','unit','mm','mm','mm','','mm','mm','mm','mm','mm','m','m','m','','','mm','mm','mm','mm','mm','mm','mm','mm','T','T','T','T','T','T','-','Hz','V','A','ohm/phase','','A/mm^2','slots','turns','mm^2','kA/m','%','tons','tons','tons','tons','tons','k$']}
	df=pd.DataFrame(raw_data, columns=['Parameters','Values','Limit','Units'])
	print df
	df.to_excel('PMSG_'+str(opt_problem.P_rated/1e6)+'_discRotor_MW.xlsx')
	
	 """
		
if __name__=="__main__":
  
  # Run an example optimization of PMSG generator on cost
  PMSG_disc_Opt_example()
