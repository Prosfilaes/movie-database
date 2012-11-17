def julian_date(YY,MM,DD,HR,Min,Sec,UTcor):  
	return 367*YY - (7*(YY+((MM+9)/12))/4) + (275*MM/9)+ DD + 
1721013.5 + UTcor/24 - 0.5*sign((100*YY)+MM-190002.5) + 0.5 + HR/24.0 + 
Min/(60.0*24.0) + Sec/(3600.0*24.0)
