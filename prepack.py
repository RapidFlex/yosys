import plb
import re
import argparse
maxconflicts=3000000
#special mapping for DSLUT <AG> <BH> <CE> <DF> <EA> <FB> <HC> <GD> <FA> <EB> <DH> <CG>
def pinsMap(pinMap, config):
    pins=[0 for i in range(8)]
    if config[0]==0:
        pins[0] = pinMap[0]
    else:
        pins[6] = pinMap[0]
    if config[1]==0:
        pins[1] = pinMap[1]
    else:
        pins[7] = pinMap[1]
    if config[2]==0:
        pins[2] = pinMap[2]
    else:
        pins[4] = pinMap[2]
    if config[3]==0:
        pins[3] = pinMap[3]
    else:
        pins[5] = pinMap[3]
    if config[4]==0:
        pins[4] = pinMap[4]
    else:
        pins[0] = pinMap[4]
    if config[5]==0:
        pins[5] = pinMap[5]
    else:
        pins[1] = pinMap[5]
    if config[6]==0:
        pins[7] = pinMap[6]
    else:
        pins[2] = pinMap[6]
    if config[7]==0:
        pins[6] = pinMap[7]
    else:
        pins[3] = pinMap[7]
    if config[8]==0:
        pins[5] = pinMap[8]
    else:
        pins[0] = pinMap[8]
    if config[9]==0:
        pins[4] = pinMap[9]
    else:
        pins[1] = pinMap[9]
    if config[10]==0:
        pins[3] = pinMap[10]
    else:
        pins[7] = pinMap[10]
    if config[11]==0:
        pins[2] = pinMap[11]
    else:
        pins[6] = pinMap[11]
    return pins

# compute truthTable
def tt_rec(line, base, pos, tt, value, nInputs):
    if(pos < nInputs):
        if(line[pos] == '1'):
            base += (1<<(nInputs-1-pos))
            tt_rec(line, base, pos+1, tt, value, nInputs)
        elif(line[pos]=='0'):
            tt_rec(line, base, pos+1, tt, value, nInputs)
        else :
            tt_rec(line, base, pos+1, tt,  value, nInputs)
            base += (1<<(nInputs-1-pos))
            tt_rec(line, base, pos+1, tt,  value, nInputs)
    else:
  
        tt[base] = value
def fun2tt(line,tt,value, nInputs):
    
    base = 0
    pos = 0
    tt_rec(line, base, pos, tt,  value, nInputs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inout_file')
    args = parser.parse_args()
    plb_6 = plb.PLB_Model(6,plb.PlbDescription(plb.PlbType.SINGLE_DSLUT)) #generate DSLUT6
    plb_8 = plb.PLB_Model(6,plb.PlbDescription(plb.PlbType.FRAC_PLB_2)) #generate PLB8
    line_list= []
    with open(args.inout_file,'r') as f:
        pin_dict = dict()
        line = f.readline()
        while(line):
            
            line=line.strip()
            tmp = line
            if(re.match('.names',line)): # revise .names
                tmp1 = ''
                if(line.endswith('\\')):
                    
                    while(line.endswith('\\')):
                        line=line.rstrip('\\')
                        tmp1 += line
                        line = f.readline()
                        line = line.strip()
                    tmp1 += line
                if(len(tmp1)!=0):
                    line = tmp1
                pins = re.split(' +',line)
                del pins[0]
                if(len(pins)== 8):  # 7-input
                    tmp2 = line
                    line=f.readline()
                    
                    if(line[8]=='0'):
                        tt=[1 for i in range(0,128)]
                    else:
                        tt=[0 for i in range(0,128)]
                    tmpTtLine=[]
                    while((line[0]=='0' or line[0] == '1' or line[0] == '-')):
                        tmpTtLine.append(line)

                        if(line[8] == '0'):
                            fun2tt(line,tt,0, 7)
                        elif(line[8] == '1'):
                            fun2tt(line,tt,1, 7)
                        line = f.readline()
                    #print(tt) 
                    
                    tt_value = plb.tt2int(tt)

                    res, restt, pinMap, config=plb_8.solveQBF(tt_value,7,maxconflicts)
                    pins2 = pinsMap(pinMap, config)
                    
                    if(res != True):
                        
                    
                        print("found 7-input not SAT!!")
                        exit(0)
                    if config[12]==1 and config[13]==0:
                        tmp_line='.names {}_old {}'.format(pins[7],pins[7])
                        tmp_line2='0 1'
                        subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}_old'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[7])
                        line_list.append(tmp_line)
                        line_list.append(tmp_line2)
                        line_list.append(subckt)
                    else:
                        subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[7])
                        line_list.append(subckt)
                    del config[12]
                    del config[13]
                    if len(config)!=74:
                        print("fetal config")
                        exit(0)
                    s ='|'.join(str(i) for i in config)
                    s1 = '# '+ s
                    line_list.append(s1)
                        
                    continue
                
                elif(len(pins)==9): #8-input
                    tmp2 = line
                    line=f.readline()
                    
                    if(line[9]=='0'):
                        tt=[1 for i in range(0,256)]
                    else:
                        tt=[0 for i in range(0,256)]
                    tmpTtLine=[]
                    while((line[0]=='0' or line[0] == '1' or line[0] == '-')):
                        tmpTtLine.append(line)

                        if(line[9] == '0'):
                            fun2tt(line,tt,0, 8)
                        elif(line[9] == '1'):
                            fun2tt(line,tt,1, 8)
                        line = f.readline()
                    #print(tt) 
                    
                    tt_value = plb.tt2int(tt)

                    res, restt, pinMap, config =plb_8.solveQBF(tt_value,8,maxconflicts)
                    pins2 = pinsMap(pinMap, config)
                    
                    if(res != True):
                       
                        print("found 8-input not SAT!!")
                        exit(0)
                    if config[12]==1 and config[13]==0:
                        tmp_line='.names {}_old {}'.format(pins[8],pins[8])
                        tmp_line2='0 1'
                        subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}_old'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[8])
                        line_list.append(tmp_line)
                        line_list.append(tmp_line2)
                        line_list.append(subckt)
                    else:
                        subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]], pins[8])
                        line_list.append(subckt)
                    del config[12]
                    del config[13]
                    if len(config)!=74:
                        print("fetal config")
                        exit(0)
                    s ='|'.join(str(i) for i in config)
                    s1 = '# '+ s
                    line_list.append(s1)
                    
                
                    continue
                    
                elif(len(pins)==7):  #6-input
                    tmp2 = line
                    line=f.readline()
                    
                    if(line[7]=='0'):
                        tt=[1 for i in range(0,64)]
                    else:
                        tt=[0 for i in range(0,64)]
                    tmpTtLine=[]
                    while((line[0]=='0' or line[0] == '1' or line[0] == '-')):
                        tmpTtLine.append(line)

                        if(line[7] == '0'):
                            fun2tt(line,tt,0, 6)
                        elif(line[7] == '1'):
                            fun2tt(line,tt,1, 6)
                        line = f.readline()
                    #print(tt) 
                    
                    tt_value = plb.tt2int(tt)

                    res, restt, pinMap, config = plb_6.solveQBF(tt_value,6,maxconflicts)
                    if(res == True):
                        
                       
                        subckt = '.subckt plb6 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} out[0]={}'.format(pins[pinMap[0]],pins[pinMap[1]],pins[pinMap[2]],pins[pinMap[3]],pins[pinMap[4]],pins[pinMap[5]],pins[6])
                        line_list.append(subckt)
                        if len(config)!=31:
                            print("fetal config for dslut6")
                            exit(0)
                        s ='|'.join(str(i) for i in config)
                        s1 = '# '+ s
                        line_list.append(s1)
                    else :
                        #print("False")
                        res2, restt, pinMap2, config=plb_8.solveQBF(tt_value,6,maxconflicts)
                        if(res2!=True):
                            print("6-Input not SAT")
                            exit(0)
                        pins2=pinsMap(pinMap2,config)
                        if config[12]==1 and config[13]==0:
                            tmp_line='.names {}_old {}'.format(pins[6],pins[6])
                            tmp_line2='0 1'
                            subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}_old'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[6])
                            line_list.append(tmp_line)
                            line_list.append(tmp_line2)
                            line_list.append(subckt)
                        else:
                            subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[6])
                            line_list.append(subckt)
                        del config[12]
                        del config[13]
                        if len(config)!=74:
                            print("fetal config")
                            exit(0)
                        s ='|'.join(str(i) for i in config)
                        s1 = '#'+ s
                        line_list.append(s1)
                        
                    continue
                
                elif(len(pins)==6): #5-input
                    tmp2 = line
                    line=f.readline()
                    
                    if(line[6]=='0'):
                        tt=[1 for i in range(0,32)]
                    else:
                        tt=[0 for i in range(0,32)]
                    tmpTtLine=[]
                    while((line[0]=='0' or line[0] == '1' or line[0] == '-')):
                        tmpTtLine.append(line)

                        if(line[6] == '0'):
                            fun2tt(line,tt,0, 5)
                        elif(line[6] == '1'):
                            fun2tt(line,tt,1, 5)
                        line = f.readline()
                    #print(tt) 
                    
                    tt_value = plb.tt2int(tt)

                    res, restt, pinMap, config=plb_6.solveQBF(tt_value,5,maxconflicts)
                    if(res == True):
                        
                        
                        subckt = '.subckt plb6 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} out[0]={}'.format(pins[pinMap[0]],pins[pinMap[1]],pins[pinMap[2]],pins[pinMap[3]],pins[pinMap[4]],pins[pinMap[5]],pins[5])
                        line_list.append(subckt)
                        if(len(config)!=31):
                            print("fetal config for dslut6")
                            exit(0)
                        s ='|'.join(str(i) for i in config)
                        s1 = '# '+ s
                        line_list.append(s1)
                    else :
                        #print("False")
                        res2, restt, pinMap2, config=plb_8.solveQBF(tt_value,5,maxconflicts)
                        if(res2!=True):
                            print("5-Input not SAT")
                            exit(0)
                        pins2= pinsMap(pinMap2, config)
                        if config[12]==1 and config[13]==0:
                            tmp_line='.names {}_old {}'.format(pins[5],pins[5])
                            tmp_line2='0 1'
                            subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}_old'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[5])
                            line_list.append(tmp_line)
                            line_list.append(tmp_line2)
                            line_list.append(subckt)
                        else:
                            subckt = '.subckt plb8 in[0]={} in[1]={} in[2]={} in[3]={} in[4]={} in[5]={} in[6]={} in[7]={} out[0]={}'.format(pins[pins2[0]],pins[pins2[1]],pins[pins2[2]],pins[pins2[3]],pins[pins2[4]],pins[pins2[5]],pins[pins2[6]],pins[pins2[7]],pins[5])
                            line_list.append(subckt)
                        del config[12]
                        del config[13]
                        if len(config)!=74:
                            print("fetal config")
                            exit(0)
                        s ='|'.join(str(i) for i in config)
                        s1 = '# '+ s
                        line_list.append(s1)
                        
                    continue
                
                
                else:
                    line_list.append(line)
                    line= f.readline()
                

            else:
                line_list.append(line)
                line=f.readline()
    with open(args.inout_file,'w') as r:
        r.writelines(line+'\n' for line in line_list)
    print("Succeedd!!")

