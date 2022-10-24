from graphviz import Source
import csv
import numpy as np
import re

np.set_printoptions(threshold=np.inf)

class generateMap(object):

    def __init__(self):
        pass

    def createMatrix(self):        
        self.desAttackList = []
        self.srcAttackList = []
        self.rewardList = []
        self.rewardDict = {}
        self.qq = {}

        self.csvfile = open('../mulval_result/VERTICES.CSV', 'r')
        self.arcscsv = open('../mulval_result/ARCS.CSV', 'r')
        self.arcsCsvData = self.arcscsv.readlines()

        self.allCsvData = self.csvfile.readlines()
        self.endLine = self.allCsvData[-1]
        self.line=int(self.endLine.split(',')[0])
        
        self.MAP = -(np.ones((self.line, self.line), dtype=np.float))
        
        self.i = 0
        for self.csvdata in self.allCsvData:
            if(len(re.findall('execCode', self.csvdata)) > 0):
                if(self.i == 0):
                    self.rewardList.append(100.0)
                    self.rewardDict[self.i] = 100.0
                else:
                    self.rewardList.append(0.3)
                    self.rewardDict[self.i] = 0.3

            elif(len(re.findall('vulExists', self.csvdata)) > 0):
                
                self.cveNumber = self.csvdata.split('(')[1].split(',')[1].split("'")[1]
                self.cve_base_score, self.cve_exploitablity_score = self.get_cvss_score(self.cveNumber)
                
                self.cvss_score = self.cve_base_score * (self.cve_exploitablity_score/10)
                self.rewardList.append(self.cvss_score)
                self.rewardDict[self.i] = self.cvss_score
                self.qq[self.i] = self.cvss_score
           
            elif(len(re.findall('attackerLocated', self.csvdata)) > 0):
                self.startLabel = self.csvdata.split('(')[1].split(')')[0]
                if(self.startLabel == 'internet'):
                    self.rewardList.append(0.01)
                    self.rewardDict[self.i] = 0.01

            else:
                self.rewardList.append(0.1)
                self.rewardDict[self.i] = 0.1
        
            self.i = self.i + 1
        for self.data in self.allCsvData:
            if(len(re.findall('RULE 2', self.data)) > 0):
                for self.a in self.qq:
                    for self.b in self.arcsCsvData:
                        if int(self.a) == int(self.b.split(',')[1]) - 1 :
                            if self.allCsvData.index(self.data) == int(self.b.split(',')[0]) - 1:
                                self.rewardDict[self.allCsvData.index(self.data)] = self.qq[self.a]
                                
        self.txtfile = open('../mulval_result/AttackGraph.txt', 'r')
        self.allTxtData = self.txtfile.readlines()

        for self.txtdata in self.allTxtData:  
            if(len(re.findall('"', self.txtdata)) == 0):
                self.desAttack = int(self.txtdata.split(',')[0])
                self.srcAttack = int(self.txtdata.split(',')[1])
                self.desAttackList.append(self.desAttack)
                self.srcAttackList.append(self.srcAttack)

                self.state = [(self.srcAttack - 1), (self.desAttack - 1)]
                self.location = self.MAP[tuple(self.state)]

           
                if(self.srcAttack > self.desAttack):
                    if(self.rewardDict[self.srcAttack - 1] == 0.01):
                   
                        self.MAP[tuple(self.state)] = self.rewardDict[self.srcAttack - 1]                     
                    elif(self.rewardDict[self.desAttack - 1] == 100.0):                       
                        self.MAP[tuple(self.state)] = self.rewardDict[self.desAttack - 1]
                    else:                    
                        self.MAP[tuple(self.state)] = (self.rewardDict[self.srcAttack - 1] + self.rewardDict[self.desAttack - 1])
                else:
                    self.MAP[tuple(self.state)] = 0.0

                
        return self.MAP

    def get_cvss_score(self, cveNumber):
        with open('../Database/CVE_Info_Dataset.csv', 'r') as self.csvfile:
            self.allCveData = csv.reader(self.csvfile)
            for self.cvedata in self.allCveData:
                if self.cveNumber == self.cvedata[0]:
                    self.cve_base_score = float(self.cvedata[2])
                    self.cve_exploitablity_score = float(self.cvedata[3])
                    return self.cve_base_score, self.cve_exploitablity_score
                    
    @property
    def sendMap(self):
        self.x = self.createMatrix()
        return self.x
