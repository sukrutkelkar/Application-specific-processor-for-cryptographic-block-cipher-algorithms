#==========================================================================================
#Portland State University
#ECE 586 Computer Architecture
#SingleCycle Datapath MultiCore Processor running IDEA Algorithm asm
#Sukrut Kelkar
#938621692
#
#Note: All the variable and definition names used are similiar to the shown in the
#Architecture block diagram provided in the report
#Best Viewed in notepad++
#================================Importing Libraries=======================================
import sys
import re
import threading
import time

#for generating trace files
#sys.stdout = open("trace.txt", "w")
#====================GLobal Declaration for both the cores=================================
global instrMem,dataMem
global RegisterFile,RegisterFilec
global WD3,WD3c
global Result,Resultc
global A3,A3c
global RD3,RD3c
global PC,PCc
global Branch,Branchc
global zero,zeroc
global Imm,Immc
global RD,RDc
global f,c,cc,cyc
global mulcon,mulconc
global start,startc

f=0
RD=RDc=0
Imm=Immc=0
zero=zeroc=0
Branch=Branchc=0
PC=PCc=-1
Result=Resultc=0
WD3=WD3c=0
A3=A3c=0
RD3=RD3c=0
c=cc=cyc=0
start=startc=0
mulcon=mulconc=0

#==========================Instruction Memory==============================================
#The text file contains memory image of the instructions
#importing this file into a dictionary
#enumeration assigns keys as line # to each line imported
#Therefore keys in my dictionary are my memory locations 
instructM=open('InstructionMem.txt','r')
instrMem = dict(enumerate(line.strip() for line in instructM))
print ('\ninstrMem: ',instrMem)
#=============================Data Memory==================================================  
#The text file contains memory image of the data and keys
#importing this file into a dictionary
#enumeration assigns keys as line # to each line imported
#Therefore keys in my dictionary are my memory locations 
#Data Memory
dataM=open('KeysandDataMem.txt','r')
dataMemT = dict(enumerate(line.strip() for line in dataM))

#Using this short algorithm the design reads only lower 16 bits from each location
#as the register size in this design is 16 bit
p=0
l=1
temp1=dt='0'
while p<181:
    temp1=temp1+dataMemT[p]
    p=p+1
k=temp1[1:]
temp1=re.findall('....',k)
while l<181:
    r=2*l
    dt=dt+temp1[r-1]
    l=l+1
dt=dt[1:]
dt=re.findall('....',dt)

#this dictionary acts as a data Memory which contains 16 bit data on each location
dataMem=dict(enumerate(line.strip() for line in dt))
print ('\ndataMem: ',dataMem)
#==================================Keys====================================================
#Using this algorithm only keys are separated from the main data memory 
j=0
key1='0'
while j<52:
    key1=key1+dataMem[j]
    j=j+1
k=key1[1:]
key1=re.findall('....',k)
key=dict(enumerate(line.strip() for line in key1))
print ('\nkey: ',key)
#=====================Data Memory for Core 1===============================================
#Using the following algorithm keys and first 512 bits of data 
#is stored from the main data memory
#This is stored in the core 1 memory
j=0
d=d2='0'
while j<84:
    d=d+dataMem[j]
    j=j+1
d1=d[1:]
data=re.findall('....',d1)
#Memory for core 1
dataMem1=dict(enumerate(line.strip() for line in data))
print ('\ndataMem1: ',dataMem1)
#=====================Data Memory for Core 2==============================================
#Using the following algorithm keys and second 512 bits of data 
#is stored from the main data memory
#This is stored in the core 2 memory
j=84
while j<116:
    d2=d2+dataMem[j]
    j=j+1
d=d2[1:]
data=re.findall('....',d)
data=key1+data
#Memory for core 2
dataMem2=dict(enumerate(line.strip() for line in data))
print ('\ndataMem2: ',dataMem2)  
#=====================Common mux and adder Modules=========================================
#functional blocks for Multiplexer and Adder
def mux(sel,firstinp,secondinp):
    if sel==0:
        out=firstinp
    else: 
        out=secondinp
    return(out)

def adderPC(inp):
    addOut=inp+1
    return(addOut)  
#======================================CORE 1===============================================
#Register files for core 1
RegisterFile = {k:0 for k in range(31)}

#Program Counter module which updates the PC after every instruction
def ProgramCounter():
    global PC
    global A
    PC=mux((Branch & zero),adderPC(PC),Imm)
    A=PC
    print ('\nPC: ',PC)
    
#Instrction Memory Module  
#This is the module in which the decoding of the hex instruction opcode takes place  
def instrMemo(A):
    global Op
    global funct
    global RD
    global A1
    global A2
    global Ard
    global Imm
    global instr
    
    #i points to the memory location in the instruction memory
    #each instruction is taken out of the memory on every PC increment
    for i in instrMem:
            if A==i:
                RD=instrMem[i]
    
    #scale_data= 16 ## equals to hexadecimal
    instr=bin(int(RD, 16))[2:].zfill(32)

    Op=int(instr[0:6],2)#opcode
    print ("Opcode: ",Op)
    funct=int(instr[21:27],2)#funct
    print ("Function: ",funct)
    rt=instr[11:16]#A2 rt
    rd=instr[16:21]# rd
    rs=instr[6:11]#A1 rs
    Imm=int(instr[16:32],2)#Immediate offset
    A1=int(rs,2)
    print ("Source register rs: ",A1)
    A2=int(rt,2)
    print ("Register rt: ",A2)
    Ard=int(rd,2)
    print ("Destination register rd: ",Ard)
    

#Control Unit Module 
#depending on the opcode and the function combination
#This module generates a set of control signals   
def ControlU(Op,funct):
    global RegWrite
    global RegDst
    global AluSrc
    global Branch
    global MemWrite
    global MemtoReg
    global AluCon
    global ALUresult
    global A3
    global start
    global mulcon
    #R-type Instructions
    if Op==0:
        RegWrite=1
        RegDst=1
        AluSrc=0
        Branch=0
        MemWrite=0
        MemtoReg=0
        
        if funct==0:
            AluCon=0
        elif funct==1:
            AluCon=1
        elif funct==2:
            AluCon=2
            start=1
            mulcon=1
        elif funct==3:
            AluCon=3
        elif funct==4:
            AluCon=4
        elif funct==5:
            AluCon=5
    #Load Word       
    elif Op==2:
        RegWrite=1
        RegDst=0
        AluSrc=1
        Branch=0
        MemWrite=0
        MemtoReg=1
        AluCon=0
    #Load Imm
    elif Op==1:
        RegWrite=1
        RegDst=0
        AluSrc=1
        Branch=0
        MemWrite=0
        MemtoReg=0
        AluCon=0    
    #Store Word      
    elif Op==3:
        RegWrite=0
        RegDst=0
        AluSrc=1
        Branch=0
        MemWrite=1
        MemtoReg=0
        AluCon=0    
    #Branch if equal
    elif Op==5:
        RegWrite=0
        RegDst=0
        AluSrc=0
        Branch=1
        MemWrite=0
        MemtoReg=0
        AluCon=1
    #Add Imm
    elif Op==9:
        RegWrite=1
        RegDst=0
        AluSrc=1
        Branch=0
        MemWrite=0
        MemtoReg=0
        AluCon=0
    #Branch if zero
    elif Op==4:
        RegWrite=0
        RegDst=0
        AluSrc=0
        Branch=1
        MemWrite=0
        MemtoReg=0
        AluCon=12
    #Branch if greater than
    elif Op==6:
        RegWrite=0
        RegDst=0
        AluSrc=0
        Branch=1
        MemWrite=0
        MemtoReg=0
        AluCon=6    
    #Branch if less than
    elif Op==7:
        RegWrite=0
        RegDst=0
        AluSrc=0
        Branch=1
        MemWrite=0
        MemtoReg=0
        AluCon=7
    #AddMod
    elif Op==11:
        RegWrite=1
        RegDst=1
        AluSrc=0
        Branch=0
        MemWrite=0
        MemtoReg=0
        AluCon=11  
    #MulMod
    elif Op==10:
        RegWrite=1
        RegDst=1
        AluSrc=0
        Branch=0
        MemWrite=0
        MemtoReg=0
        AluCon=10
        start=1
        mulcon=1
    #jump
    elif Op==8:
        RegWrite=0
        RegDst=0
        AluSrc=0
        Branch=1
        MemWrite=0
        MemtoReg=0
        AluCon=8
    A3=mux(RegDst,A2,Ard)
    print ("RegWrite: ",RegWrite)
    print ("RegDst: ",RegDst)
    print ("AluSrc: ",AluSrc)
    print ("Branch: ",Branch)
    print ("MemWrite: ",MemWrite)
    print ("MemtoReg: ",MemtoReg)
    print ("AluCon: ",AluCon)
    print ("start: ",start)
    print ("mulcon: ",mulcon)

#Register File Module
#In this module depending on the value of A1 and A2
#which are the register address pointers
#The register is selected and the output port is set with the corresponding value
def RegisterFiles(A1,A2):
    global RD1
    global RD2
    global SrcA
    global SrcB
    for i in RegisterFile:
        if (A1==i):
            RD1=RegisterFile[i]

    for i in RegisterFile:
        if (A2==i):
            RD2=RegisterFile[i]
    
    #Soruce operands are set here 
    SrcB=mux(AluSrc,RD2,Imm)
    SrcA=RD1  

#Arithmetic Logic Unit ALU 
#depending on the control signals and the register values
#Arithmetic or Multiplication operations are performed in this module
def ALU_main(AluCon,inp1,inp2):
        
    global ALUresult
    global zero
    global start
    global mulcon
    if AluCon==0:#add
        ALUresult=inp1+inp2
    
    elif AluCon==1:#sub
        ALUresult=inp1-inp2
    
    elif AluCon==2:#mul
        if start==1:
            MULresult=inp1*inp2
            start=0
            ALUresult=mux(mulcon,ALUresult,MULresult)
    
    elif AluCon==3:#or
        ALUresult=inp1 | inp2
    
    elif AluCon==4:#and
        ALUresult=inp1 & inp2
    
    elif AluCon==5:#XOR
        ALUresult=inp1 ^ inp2
    
    elif AluCon==11:#AddMod
        ALUresult=inp1+inp2
        ALUresult=bin(ALUresult)[2:].zfill(32) 
        temp=int(ALUresult[0:16],2)-int(ALUresult[16:32],2)
        ALUresult=int(ALUresult[16:32],2)         
        
    elif AluCon==10:#MulMod
        if start==1:
        #if any of the operand is zero the take it as 65536
            if inp1==0:
                inp1=65536
                
            if inp2==0:
                inp2=65536
       
            MULresult=inp1*inp2
            MULresult=bin(MULresult)[2:].zfill(32) 
            #higher 16 bits subtracted from lower 16 bits
            temp=int(MULresult[16:32],2)-int(MULresult[0:16],2)
            #if positive the answer is the subtraction
            if temp>0:
                MULresult=temp
            #if negative the answer is subtraction result added with 65537
            elif temp<0:
                MULresult=temp+65537
            start=0
            ALUresult=mux(mulcon,ALUresult,MULresult)
    
    #All the branch and Jump operations make the ALUresult zero 
    #this sets the zero flag
    #which sets the PCSrc flag
    elif AluCon==6:#BGT
        if inp2>inp1:
            ALUresult=0
        else:
            ALUresult=1
            
    elif AluCon==7:#BLT
        if inp2<inp1:
            ALUresult=0
        else:
            ALUresult=1
    
    elif AluCon==12:#BZ
        if inp1==inp2:
            ALUresult=0
        else:
            ALUresult=1
            
    elif AluCon==8:#jump
            ALUresult=0
    #If ALU result is zero then the zero flag goes high
    if ALUresult==0:
        zero=1
    else:
        zero=0
    print ("ALUresult: ",ALUresult)
    print ("zero flag: ",zero)
        
        
#Write into register files
#This module is a write back module 
#It performs the operation of writing back to the register
#depending on the value of A3 which points to the destination register
def RegisterFileWrite():
    global WD3
    Result=mux(MemtoReg,ALUresult,RD3)
    WD3=Result
    if RegWrite==1:
        for i in RegisterFile:
            if (A3==i):
                RegisterFile[i]=WD3
    print ('RegisterFile: ',RegisterFile)    

#This is data Memory read write module for this core
#depending on the value of A4 specific memory location is accessed
def dataMemo():
    global RD3
    global Result
    global c
    WD=RD2
    A4=ALUresult
    
    if MemWrite==0:
        for i in dataMem1:
            if A4==i:
                RD3=int(dataMem1[i],16)
    else:
        for i in dataMem:
            if A4==i:
                dataMem[i]=hex(WD)[2:]
                
#===========================================CORE 2===============================================================
#Core two has exact same convention as core 1
#The only change in core two is the memory
#Each core has its own separate memory which holds the keys and the data
#Register files
RegisterFilec = {k:0 for k in range(31)}

#program counter    
def ProgramCounterc():
    global PCc
    global Ac
    global cyc
    PCc=mux((Branchc & zeroc),adderPC(PCc),Immc)
    Ac=PCc
    print ('\nPCc: ',PCc)
    
#Instrction Memory Module    
def instrMemoc(Ac):
    global Opc
    global functc
    global RDc
    global A1c
    global A2c
    global Ardc
    global Immc
    global instrc

    for i in instrMem:
            if Ac==i:
                RDc=instrMem[i]
    
    #scale_data= 16 ## equals to hexadecimal
    instrc=bin(int(RDc, 16))[2:].zfill(32)

    Opc=int(instrc[0:6],2)#opcode
    print ("Opcodec2: ",Opc)
    functc=int(instrc[21:27],2)#funct
    print ("Functionc2: ",functc)
    rtc=instrc[11:16]#A2 rt
    rdc=instrc[16:21]# rd
    rsc=instrc[6:11]#A1 rs
    Immc=int(instrc[16:32],2)#Immediate offset
    A1c=int(rsc,2)
    print ("Source register rs c2: ",A1c)
    A2c=int(rtc,2)
    print ("Register rt c2: ",A2c)
    Ardc=int(rdc,2)
    print ("Destination register rd c2: ",Ardc)
    
#Control Unit Module    
def ControlUc(Opc,functc):
    global RegWritec
    global RegDstc
    global AluSrcc
    global Branchc
    global MemWritec
    global MemtoRegc
    global AluConc
    global ALUresultc
    global A3c
    global startc
    global mulconc
    #R-type Instructions
    if Opc==0:
        RegWritec=1
        RegDstc=1
        AluSrcc=0
        Branchc=0
        MemWritec=0
        MemtoRegc=0
        
        if functc==0:
            AluConc=0
        elif functc==1:
            AluConc=1
        elif functc==2:
            AluConc=2
            startc=1
            mulconc=1
        elif functc==3:
            AluConc=3
        elif functc==4:
            AluConc=4
        elif functc==5:
            AluConc=5
    #Load Word       
    elif Opc==2:
        RegWritec=1
        RegDstc=0
        AluSrcc=1
        Branchc=0
        MemWritec=0
        MemtoRegc=1
        AluConc=0
    #Load Imm
    elif Opc==1:
        RegWritec=1
        RegDstc=0
        AluSrcc=1
        Branchc=0
        MemWritec=0
        MemtoRegc=0
        AluConc=0    
    #Store Word      
    elif Opc==3:
        RegWritec=0
        RegDstc=0
        AluSrcc=1
        Branchc=0
        MemWritec=1
        MemtoRegc=0
        AluConc=0    
    #Branch if equal
    elif Opc==5:
        RegWritec=0
        RegDstc=0
        AluSrcc=0
        Branchc=1
        MemWritec=0
        MemtoRegc=0
        AluConc=1
    #Add Imm
    elif Opc==9:
        RegWritec=1
        RegDstc=0
        AluSrcc=1
        Branchc=0
        MemWritec=0
        MemtoRegc=0
        AluConc=0
    #Branch if zero
    elif Opc==4:
        RegWritec=0
        RegDstc=0
        AluSrcc=0
        Branchc=1
        MemWritec=0
        MemtoRegc=0
        AluConc=12
    #Branch if greater than
    elif Opc==6:
        RegWritec=0
        RegDstc=0
        AluSrcc=0
        Branchc=1
        MemWritec=0
        MemtoRegc=0
        AluConc=6    
    #Branch if less than
    elif Opc==7:
        RegWritec=0
        RegDstc=0
        AluSrcc=0
        Branchc=1
        MemWritec=0
        MemtoRegc=0
        AluConc=7
    #AddMod
    elif Opc==11:
        RegWritec=1
        RegDstc=1
        AluSrcc=0
        Branchc=0
        MemWritec=0
        MemtoRegc=0
        AluConc=11  
    #MulMod
    elif Opc==10:
        RegWritec=1
        RegDstc=1
        AluSrcc=0
        Branchc=0
        MemWritec=0
        MemtoRegc=0
        AluConc=10
        startc=1
        mulconc=1
    #jump
    elif Opc==8:
        RegWritec=0
        RegDstc=0
        AluSrc=0
        Branchc=1
        MemWritec=0
        MemtoRegc=0
        AluConc=8
    A3c=mux(RegDstc,A2c,Ardc)
    print ("RegWritec: ",RegWritec)
    print ("RegDstc: ",RegDstc)
    print ("AluSrcc: ",AluSrcc)
    print ("Branchc: ",Branchc)
    print ("MemWritec: ",MemWritec)
    print ("MemtoRegc: ",MemtoRegc)
    print ("AluConc: ",AluConc)
    print ("startc: ",startc)
    print ("mulconc: ",mulconc)
    

#Register File Module
def RegisterFilesc(A1c,A2c):
    global RD1c
    global RD2c
    global SrcAc
    global SrcBc
    for i in RegisterFilec:
        if (A1c==i):
            RD1c=RegisterFilec[i]

    for i in RegisterFilec:
        if (A2c==i):
            RD2c=RegisterFilec[i]
                
    SrcBc=mux(AluSrcc,RD2c,Immc)
    SrcAc=RD1c  

#Arithmetic Logic Unit ALU 
def ALU_mainc(AluConc,inp1c,inp2c):
        
    global ALUresultc
    global zeroc
    global startc
    if AluConc==0:#add
        ALUresultc=inp1c+inp2c
    
    elif AluConc==1:#sub
        ALUresultc=inp1c-inp2c
    
    elif AluConc==2:#mul
        if startc==1:
            MULresultc=inp1c*inp2c
            startc=0
            ALUresultc=mux(mulconc,ALUresultc,MULresultc)
            
    elif AluConc==3:#or
        ALUresultc=inp1c | inp2c
    
    elif AluConc==4:#and
        ALUresultc=inp1c & inp2c
    
    elif AluConc==5:#XOR
        ALUresultc=inp1c ^ inp2c
    
    elif AluConc==11:#AddMod
        ALUresultc=inp1c+inp2c
        ALUresultc=bin(ALUresultc)[2:].zfill(32) 
        temp=int(ALUresultc[0:16],2)-int(ALUresultc[16:32],2)
        ALUresultc=int(ALUresultc[16:32],2)         
        
    elif AluConc==10:#MulMod
        if startc==1:
            if inp1c==0:
                inp1c=65536
                
            if inp2c==0:
                inp2c=65536
       
            MULresultc=inp1c*inp2c
            MULresultc=bin(MULresultc)[2:].zfill(32) 
            temp=int(MULresultc[16:32],2)-int(MULresultc[0:16],2)
            if temp>0:
                MULresultc=temp
            elif temp<0:
                MULresultc=temp+65537
        startc=0
        ALUresultc=mux(mulconc,ALUresultc,MULresultc)
        
    elif AluConc==6:#BGT
        if inp2c>inp1c:
            ALUresultc=0
        else:
            ALUresultc=1
            
    elif AluConc==7:#BLT
        if inp2c<inp1c:
            ALUresultc=0
        else:
            ALUresultc=1
    
    elif AluConc==12:#BZ
        if inp1c==inp2c:
            ALUresultc=0
        else:
            ALUresultc=1
    
    elif AluConc==8:#jump
        ALUresultc=0
            
    if ALUresultc==0:
        zeroc=1
    else:
        zeroc=0
    print ("ALUresult c2: ",ALUresultc)
    print ("zero flag c2: ",zeroc)    
        
#Write to register files      
def RegisterFileWritec():
    global WD3c
    Resultc=mux(MemtoRegc,ALUresultc,RD3c)
    WD3c=Resultc
    if RegWritec==1:
        for i in RegisterFilec:
            if (A3c==i):
                RegisterFilec[i]=WD3c
    print ('RegisterFile c2: ',RegisterFilec)   
        

#data memory for core 2
def dataMemoc():
    global RD3c
    global Resultc
    WDc=RD2c
    A4c=ALUresultc
    
    if MemWritec==0:
        for i in dataMem2:
            if A4c==i:
                RD3c=int(dataMem2[i],16)
    else:
        for i in dataMem:
            if A4c==i:
                q=i+32
                dataMem[q]=hex(WDc)[2:]
    
#============================================CORE 1 CLASS THREAD===================================================            
class core1(threading.Thread):        
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global t1
        #starting time is noted for this thread
        t0=time.clock()
        while 1:   
            ProgramCounter()
            instrMemo(A)
            if int(instr,2)==1:
                break
            ControlU(Op,funct)
            RegisterFiles(A1,A2)
            ALU_main(AluCon,SrcA,SrcB)
            dataMemo()
            RegisterFileWrite()
        print ('Exiting Thread 1')
        #Ending time is noted and starting time is subtracted from it
        t1=time.clock()-t0
#======================================CORE 2 CLASS THREAD===================================================
class core2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global t3
        global cyc
        #starting time is noted for this thread
        t2=time.clock()
        while 1:   
            ProgramCounterc()
            instrMemoc(Ac)
            if int(instrc,2)==1:
                break
            ControlUc(Opc,functc)
            RegisterFilesc(A1c,A2c)
            ALU_mainc(AluConc,SrcAc,SrcBc)
            dataMemoc()
            RegisterFileWritec()
            #Counter for counting the clock cycles
            cyc=cyc+1
            print ("\nCyc: ",cyc)
        print ('Exiting Thread 2')
        #Starting time subracted from the ending time
        t3=time.clock()-t2
#==================================EXECUTING THREADS============================================================         
proc=[]
#A global time is noted at the starting of the program
tt=time.clock()
c1 = core1()
c2 = core2()
#Both the cores are Started at the same time
c2.start()
c1.start()
#Synchronizig the time of both the clocks
c2.join()
c1.join()
#Total time taken by the Program is calculated
t=time.clock()-tt
print ("Exiting Main thread")
#===================================Print Final Data===========================================================
final = '0'
j=116
i=1
print ("Data Memory: \n",dataMem)
while i<17:
    final = final + dataMem[j] + dataMem[j+1] + dataMem[j+2] + dataMem[j+3]
    i=i+1
    j=j+4
finalbin=bin(int(final[1:],16))[2:].zfill(1024)
final=final[1:]
#==============================Storing Everything back to text file===========================================
push2text = [ v for v in dataMem.values() ]
push2text=push2text[116:180]  
file=open('output.txt','w')
file.write("\n".join(push2text))
print ("\n******************************Output**********************************************")
print ('Encrypted Data: ',final)
print ('\nLength of Encrpted Data: ',len(finalbin))
print ("\nTotal Clock Cycles: ",cyc,' Clock Cycles')
print ('Time required for thread 1= ',t1,' seconds')
print ('Time required for thread 2= ',t3,' seconds')
print ('Total Time required for both threads= ',t,' seconds')
print ('\nBandwidth is ',((len(finalbin)/(2.925*cyc))*1000),'Mbits/second')
print ("**********************************************************************************")