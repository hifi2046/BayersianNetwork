# -*- coding: GBK -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

'''
PassengerId => �˿�ID
Pclass => �Ͳյȼ�(1/2/3�Ȳ�λ)
Name => �˿�����
Sex => �Ա� ��ϴ��male=1 female=0
Age => ���� �岹���0,1,2 ���� ���꣨0-15�� ���꣨15-55�� ���꣨55-��
SibSp => �ֵܽ�����/��ż��
Parch => ��ĸ��/��Ů��
Ticket => ��Ʊ���
Fare => ��Ʊ�۸� �������0 1 2 ������ �� �ܶ�
Cabin => �Ͳպ� ��ϴ�����޴���������е������ʸ�
Embarked => �Ǵ��ۿ� ��ϴna,��S
'''
# combine train and test set.
train=pd.read_csv('./train.csv')
test=pd.read_csv('./test.csv')
full=pd.concat([train,test],ignore_index=True)
full['Embarked'].fillna('S',inplace=True)
full.Fare.fillna(full[full.Pclass==3]['Fare'].median(),inplace=True)
full.loc[full.Cabin.notnull(),'Cabin']=1
full.loc[full.Cabin.isnull(),'Cabin']=0
full.loc[full['Sex']=='male','Sex']=1
full.loc[full['Sex']=='female','Sex']=0

full['Title']=full['Name'].apply(lambda x: x.split(',')[1].split('.')[0].strip())
nn={'Capt':'Rareman', 'Col':'Rareman','Don':'Rareman','Dona':'Rarewoman',
    'Dr':'Rareman','Jonkheer':'Rareman','Lady':'Rarewoman','Major':'Rareman',
    'Master':'Master','Miss':'Miss','Mlle':'Rarewoman','Mme':'Rarewoman',
    'Mr':'Mr','Mrs':'Mrs','Ms':'Rarewoman','Rev':'Mr','Sir':'Rareman',
    'the Countess':'Rarewoman'}
full.Title=full.Title.map(nn)
# assign the female 'Dr' to 'Rarewoman'
full.loc[full.PassengerId==797,'Title']='Rarewoman'
full.Age.fillna(999,inplace=True)
def girl(aa):
    if (aa.Age!=999)&(aa.Title=='Miss')&(aa.Age<=14):
        return 'Girl'
    elif (aa.Age==999)&(aa.Title=='Miss')&(aa.Parch!=0):
        return 'Girl'
    else:
        return aa.Title

full['Title']=full.apply(girl,axis=1)

Tit=['Mr','Miss','Mrs','Master','Girl','Rareman','Rarewoman']
for i in Tit:
    full.loc[(full.Age==999)&(full.Title==i),'Age']=full.loc[full.Title==i,'Age'].median()
    
full.loc[full['Age']<=15,'Age']=0
full.loc[(full['Age']>15)&(full['Age']<55),'Age']=1
full.loc[full['Age']>=55,'Age']=2
full['Pclass']=full['Pclass']-1
from sklearn.cluster import KMeans
Fare=full['Fare'].values
Fare=Fare.reshape(-1,1)
km = KMeans(n_clusters=3).fit(Fare)   #�����ݼ���Ϊ2��
Fare = km.fit_predict(Fare)
full['Fare']=Fare
full['Fare']=full['Fare'].astype(int)
full['Age']=full['Age'].astype(int)
full['Cabin']=full['Cabin'].astype(int)
full['Pclass']=full['Pclass'].astype(int)
full['Sex']=full['Sex'].astype(int)
#full['Survived']=full['Survived'].astype(int)


dataset=full.drop(columns=['Embarked','Name','Parch','PassengerId','SibSp','Ticket','Title'])
dataset.dropna(inplace=True)
dataset['Survived']=dataset['Survived'].astype(int)
#dataset=pd.concat([dataset, pd.DataFrame(columns=['Pri'])])
train=dataset[:800]
test=dataset[800:]
'''
�����������Ŀ��
Pclass => �Ͳյȼ�(1/2/3�Ȳ�λ)
Sex => �Ա� male=1 female=0
Age => ���� �岹���0,1,2 ���� ���꣨0-15�� ���꣨15-55�� ���꣨55-��
Fare => ��Ʊ�۸� �������0 1 2 ������ �� �ܶ�
Cabin => �Ͳպ� ��ϴ�����޴���������е������ʸ�
'''

train.head()

from pgmpy.models import BayesianModel
from pgmpy.estimators import BayesianEstimator

#model = BayesianModel([('Age', 'Pri'), ('Sex', 'Pri'),('Pri','Survived'),('Fare','Pclass'),('Pclass','Survived'),('Cabin','Survived')])
model = BayesianModel([('Age', 'Survived'), ('Sex', 'Survived'),('Fare','Pclass'),('Pclass','Survived'),('Cabin','Survived')])
model.fit(train, estimator=BayesianEstimator, prior_type="BDeu") # default equivalent_sample_size=5

def showBN(model,save=False):
    '''����BayesianModel���󣬵���graphviz���ƽṹͼ��jupyter�п�ֱ����ʾ'''
    from graphviz import Digraph
    node_attr = dict(
     style='filled',
     shape='box',
     align='left',
     fontsize='12',
     ranksep='0.1',
     height='0.2'
    )
    dot = Digraph(node_attr=node_attr, graph_attr=dict(size="12,12"))
    seen = set()
    edges=model.edges()
    for a,b in edges:
        dot.edge(a,b)
    if save:
        dot.view(cleanup=True)
    return dot
showBN(model)

for cpd in model.get_cpds():
    print(cpd)
predict_data=test.drop(columns=['Survived'],axis=1)
y_pred = model.predict(predict_data)

#(y_pred['Survived']==test['Survived']).sum()/len(test)#���Լ�����

from pgmpy.inference import VariableElimination
model_infer = VariableElimination(model)
q = model_infer.query(variables=['Survived'], evidence={'Fare': 0})
print(q)
q = model_infer.map_query(variables=['Fare','Age','Sex','Pclass','Cabin'], evidence={'Survived': 1})
print(q)

